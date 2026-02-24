"""
增强版持仓管理 API - 支持实时价格
Enhanced Holdings API with Real-time Prices
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Stock, Holding, MarketType
from app.services.cache_service import cache, get_cached_quote, refresh_quote

router = APIRouter()

# 汇率
HKD_TO_CNY = 0.85


class HoldingResponse(BaseModel):
    """持仓响应 (含实时价格)"""
    id: int
    stock_id: int
    stock_code: str
    stock_name: str
    market_type: str
    shares: int
    avg_cost: float
    avg_cost_cny: float
    current_price: Optional[float] = None
    current_price_cny: Optional[float] = None
    market_value: Optional[float] = None
    market_value_cny: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    price_change: Optional[float] = None
    price_change_pct: Optional[float] = None
    purchase_date: Optional[str] = None
    last_updated: Optional[str] = None
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """持仓汇总 (含实时数据)"""
    total_holdings: int
    total_market_value: float
    total_market_value_cny: float
    total_cost: float
    total_profit_loss: float
    total_profit_loss_pct: float
    today_change: float
    today_change_pct: float
    holdings: List[HoldingResponse]
    industry_distribution: dict
    market_distribution: dict


async def fetch_and_update_price(holding: Holding, stock: Stock, db: Session) -> HoldingResponse:
    """获取并更新持仓价格"""
    # 尝试获取实时价格
    quote = await get_cached_quote(stock.code)
    
    if quote and quote.get('price'):
        current_price = float(quote['price'])
        current_price_cny = current_price * (HKD_TO_CNY if stock.market_type == MarketType.HK_STOCK else 1)
        
        # 更新数据库
        holding.current_price = current_price
        holding.current_price_cny = current_price_cny
        holding.last_updated = datetime.utcnow()
        db.commit()
    else:
        # 使用现有价格
        current_price = holding.current_price or holding.avg_cost
        current_price_cny = holding.current_price_cny or holding.avg_cost_cny
    
    # 计算市值
    market_value = current_price * holding.shares
    market_value_cny = current_price_cny * holding.shares
    
    # 计算盈亏
    cost = holding.avg_cost * holding.shares
    profit_loss = market_value - cost
    profit_loss_pct = ((current_price / holding.avg_cost) - 1) * 100 if holding.avg_cost > 0 else 0
    
    # 今日涨跌 (如果有开盘价)
    price_change = 0
    price_change_pct = 0
    if quote and quote.get('change'):
        price_change = float(quote['change'])
        price_change_pct = float(quote.get('change_pct', 0))
    
    return HoldingResponse(
        id=holding.id,
        stock_id=holding.stock_id,
        stock_code=stock.code,
        stock_name=stock.name,
        market_type=stock.market_type.value,
        shares=holding.shares,
        avg_cost=holding.avg_cost,
        avg_cost_cny=holding.avg_cost_cny,
        current_price=current_price,
        current_price_cny=current_price_cny,
        market_value=round(market_value, 2),
        market_value_cny=round(market_value_cny, 2),
        profit_loss=round(profit_loss, 2),
        profit_loss_pct=round(profit_loss_pct, 2),
        price_change=round(price_change, 2),
        price_change_pct=round(price_change_pct, 2),
        purchase_date=holding.purchase_date.isoformat() if holding.purchase_date else None,
        last_updated=holding.last_updated.isoformat() if holding.last_updated else None
    )


@router.get("/", response_model=List[HoldingResponse])
async def get_holdings(db: Session = Depends(get_db)):
    """获取所有持仓 (含实时价格)"""
    holdings = db.query(Holding).all()
    
    result = []
    for h in holdings:
        stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        if not stock:
            continue
        
        holding_resp = await fetch_and_update_price(h, stock, db)
        result.append(holding_resp)
    
    return result


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """获取持仓汇总 (含实时数据)"""
    holdings = db.query(Holding).all()
    
    total_market_value = 0.0
    total_market_value_cny = 0.0
    total_cost = 0.0
    total_profit_loss = 0.0
    today_change = 0.0
    
    industry_dist = {}
    market_dist = {}
    
    result_holdings = []
    
    for h in holdings:
        stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        if not stock:
            continue
        
        holding_resp = await fetch_and_update_price(h, stock, db)
        result_holdings.append(holding_resp)
        
        # 汇总
        if holding_resp.market_value:
            total_market_value += holding_resp.market_value
        if holding_resp.market_value_cny:
            total_market_value_cny += holding_resp.market_value_cny
        if holding_resp.profit_loss:
            total_profit_loss += holding_resp.profit_loss
        if holding_resp.price_change:
            today_change += holding_resp.price_change * holding_resp.shares
        
        # 行业分布
        sector = stock.sector or "其他"
        industry_dist[sector] = industry_dist.get(sector, 0) + (holding_resp.market_value_cny or 0)
        
        # 市场分布
        market_dist[stock.market_type.value] = market_dist.get(stock.market_type.value, 0) + (holding_resp.market_value_cny or 0)
    
    total_cost = sum(h.avg_cost * h.shares for h in holdings)
    total_profit_loss_pct = ((total_market_value_cny / total_cost) - 1) * 100 if total_cost > 0 else 0
    today_change_pct = (today_change / total_market_value) * 100 if total_market_value > 0 else 0
    
    # 转换为百分比
    total_industry = sum(industry_dist.values())
    for k in industry_dist:
        industry_dist[k] = round(industry_dist[k] / total_industry * 100, 1) if total_industry > 0 else 0
    
    total_market = sum(market_dist.values())
    for k in market_dist:
        market_dist[k] = round(market_dist[k] / total_market * 100, 1) if total_market > 0 else 0
    
    return PortfolioSummary(
        total_holdings=len(holdings),
        total_market_value=round(total_market_value, 2),
        total_market_value_cny=round(total_market_value_cny, 2),
        total_cost=round(total_cost, 2),
        total_profit_loss=round(total_profit_loss, 2),
        total_profit_loss_pct=round(total_profit_loss_pct, 2),
        today_change=round(today_change, 2),
        today_change_pct=round(today_change_pct, 2),
        holdings=result_holdings,
        industry_distribution=industry_dist,
        market_distribution=market_dist
    )


@router.post("/refresh")
async def refresh_prices(db: Session = Depends(get_db)):
    """强制刷新所有持仓价格"""
    holdings = db.query(Holding).all()
    
    results = []
    for h in holdings:
        stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        if not stock:
            continue
        
        # 强制刷新
        quote = await refresh_quote(stock.code)
        
        if quote and quote.get('price'):
            current_price = float(quote['price'])
            h.current_price = current_price
            h.current_price_cny = current_price * (HKD_TO_CNY if stock.market_type == MarketType.HK_STOCK else 1)
            h.last_updated = datetime.utcnow()
            db.commit()
            results.append({"code": stock.code, "price": current_price, "status": "updated"})
        else:
            results.append({"code": stock.code, "status": "failed"})
    
    return {
        "total": len(holdings),
        "results": results
    }
