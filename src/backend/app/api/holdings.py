"""
持仓管理 API 路由
Holdings/Portfolio API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Stock, Holding, MarketType

router = APIRouter()


# Pydantic 模型
class HoldingResponse(BaseModel):
    """持仓响应"""
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
    purchase_date: Optional[str] = None
    
    class Config:
        from_attributes = True


class HoldingCreate(BaseModel):
    """创建持仓请求"""
    stock_code: str
    stock_name: str
    shares: int
    avg_cost: float
    current_price: Optional[float] = None
    purchase_date: Optional[str] = None
    notes: Optional[str] = None


class HoldingUpdate(BaseModel):
    """更新持仓请求"""
    shares: Optional[int] = None
    avg_cost: Optional[float] = None
    current_price: Optional[float] = None
    notes: Optional[str] = None


class PortfolioSummary(BaseModel):
    """持仓汇总"""
    total_holdings: int
    total_market_value: float
    total_market_value_cny: float
    total_cost: float
    total_profit_loss: float
    total_profit_loss_pct: float
    holdings: List[HoldingResponse]
    
    # 行业分布
    industry_distribution: dict
    
    # 市场分布
    market_distribution: dict


# 汇率 (可以后续从 API 获取)
HKD_TO_CNY = 0.85  # 港币兑人民币


def parse_stock_code(code: str) -> tuple[str, MarketType, str]:
    """解析股票代码"""
    code = code.strip().upper()
    
    if code.endswith('.HK') or code.endswith('.HK'):
        return code, MarketType.HK_STOCK, code.replace('.HK', '').zfill(5)
    elif code.endswith('.SH'):
        return code, MarketType.A_SHARE, code.replace('.SH', '')
    elif code.endswith('.SZ'):
        return code, MarketType.A_SHARE, code.replace('.SZ', '')
    elif code.endswith('.US'):
        return code, MarketType.US_STOCK, code.replace('.US', '')
    else:
        # 尝试自动识别
        if code.startswith('00') or code.startswith('30'):
            return f"{code}.SZ", MarketType.A_SHARE, code
        elif code.startswith('60') or code.startswith('68'):
            return f"{code}.SH", MarketType.A_SHARE, code
        else:
            # 默认视为港股
            return f"{code}.HK", MarketType.HK_STOCK, code.zfill(5)


@router.get("/", response_model=List[HoldingResponse])
async def get_holdings(db: Session = Depends(get_db)):
    """获取所有持仓"""
    holdings = db.query(Holding).all()
    
    result = []
    for h in holdings:
        stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        if not stock:
            continue
        
        # 计算市值
        if h.current_price and h.shares:
            market_value = h.current_price * h.shares
            market_value_cny = market_value * (HKD_TO_CNY if stock.market_type == MarketType.HK_STOCK else 1)
        else:
            market_value = None
            market_value_cny = None
        
        # 计算盈亏
        if h.current_price and h.avg_cost:
            profit_loss = (h.current_price - h.avg_cost) * h.shares
            profit_loss_pct = ((h.current_price / h.avg_cost) - 1) * 100
        else:
            profit_loss = None
            profit_loss_pct = None
        
        result.append(HoldingResponse(
            id=h.id,
            stock_id=h.stock_id,
            stock_code=stock.code,
            stock_name=stock.name,
            market_type=stock.market_type.value,
            shares=h.shares,
            avg_cost=h.avg_cost,
            avg_cost_cny=h.avg_cost_cny or h.avg_cost,
            current_price=h.current_price,
            current_price_cny=h.current_price_cny,
            market_value=market_value,
            market_value_cny=market_value_cny,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct,
            purchase_date=h.purchase_date.isoformat() if h.purchase_date else None
        ))
    
    return result


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """获取持仓汇总"""
    holdings = db.query(Holding).all()
    
    total_market_value = 0.0
    total_market_value_cny = 0.0
    total_cost = 0.0
    total_profit_loss = 0.0
    
    industry_dist = {}
    market_dist = {}
    
    result_holdings = []
    
    for h in holdings:
        stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        if not stock:
            continue
        
        # 计算
        if h.current_price and h.shares:
            mv = h.current_price * h.shares
            mvcny = mv * (HKD_TO_CNY if stock.market_type == MarketType.HK_STOCK else 1)
            pl = (h.current_price - h.avg_cost) * h.shares
        else:
            mv = h.avg_cost * h.shares
            mvcny = mv
            pl = 0
        
        total_market_value += mv
        total_market_value_cny += mvcny
        total_cost += h.avg_cost * h.shares
        total_profit_loss += pl
        
        # 行业分布
        sector = stock.sector or "其他"
        industry_dist[sector] = industry_dist.get(sector, 0) + mvcny
        
        # 市场分布
        market_dist[stock.market_type.value] = market_dist.get(stock.market_type.value, 0) + mvcny
        
        result_holdings.append(HoldingResponse(
            id=h.id,
            stock_id=h.stock_id,
            stock_code=stock.code,
            stock_name=stock.name,
            market_type=stock.market_type.value,
            shares=h.shares,
            avg_cost=h.avg_cost,
            avg_cost_cny=h.avg_cost_cny or h.avg_cost,
            current_price=h.current_price,
            current_price_cny=h.current_price_cny,
            market_value=mv,
            market_value_cny=mvcny,
            profit_loss=pl,
            profit_loss_pct=((h.current_price / h.avg_cost) - 1) * 100 if h.current_price and h.avg_cost else 0,
            purchase_date=h.purchase_date.isoformat() if h.purchase_date else None
        ))
    
    total_profit_loss_pct = ((total_market_value_cny / total_cost) - 1) * 100 if total_cost > 0 else 0
    
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
        holdings=result_holdings,
        industry_distribution=industry_dist,
        market_distribution=market_dist
    )


@router.post("/", response_model=HoldingResponse)
async def create_holding(holding: HoldingCreate, db: Session = Depends(get_db)):
    """添加持仓"""
    # 解析股票代码
    code, market_type, original = parse_stock_code(holding.stock_code)
    
    # 查找或创建股票
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        stock = Stock(
            code=code,
            name=holding.stock_name,
            market_type=market_type,
            original_code=original,
            market="HK" if market_type == MarketType.HK_STOCK else ("SH" if ".SH" in code else "SZ")
        )
        db.add(stock)
        db.commit()
        db.refresh(stock)
    
    # 转换成本为人民币
    avg_cost_cny = holding.avg_cost * (HKD_TO_CNY if market_type == MarketType.HK_STOCK else 1)
    
    # 创建持仓
    db_holding = Holding(
        stock_id=stock.id,
        shares=holding.shares,
        avg_cost=holding.avg_cost,
        avg_cost_cny=avg_cost_cny,
        current_price=holding.current_price or holding.avg_cost,
        current_price_cny=(holding.current_price or holding.avg_cost) * (HKD_TO_CNY if market_type == MarketType.HK_STOCK else 1),
        notes=holding.notes
    )
    
    if holding.purchase_date:
        db_holding.purchase_date = datetime.fromisoformat(holding.purchase_date)
    
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)
    
    return HoldingResponse(
        id=db_holding.id,
        stock_id=stock.id,
        stock_code=stock.code,
        stock_name=stock.name,
        market_type=stock.market_type.value,
        shares=db_holding.shares,
        avg_cost=db_holding.avg_cost,
        avg_cost_cny=db_holding.avg_cost_cny,
        current_price=db_holding.current_price,
        current_price_cny=db_holding.current_price_cny,
        purchase_date=db_holding.purchase_date.isoformat() if db_holding.purchase_date else None
    )


@router.patch("/{holding_id}", response_model=HoldingResponse)
async def update_holding(holding_id: int, holding: HoldingUpdate, db: Session = Depends(get_db)):
    """更新持仓"""
    db_holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not db_holding:
        raise HTTPException(status_code=404, detail="持仓不存在")
    
    if holding.shares is not None:
        db_holding.shares = holding.shares
    if holding.avg_cost is not None:
        db_holding.avg_cost = holding.avg_cost
    if holding.current_price is not None:
        db_holding.current_price = holding.current_price
    if holding.notes is not None:
        db_holding.notes = holding.notes
    
    db.commit()
    db.refresh(db_holding)
    
    stock = db.query(Stock).filter(Stock.id == db_holding.stock_id).first()
    
    return HoldingResponse(
        id=db_holding.id,
        stock_id=db_holding.stock_id,
        stock_code=stock.code,
        stock_name=stock.name,
        market_type=stock.market_type.value,
        shares=db_holding.shares,
        avg_cost=db_holding.avg_cost,
        avg_cost_cny=db_holding.avg_cost_cny,
        current_price=db_holding.current_price,
        current_price_cny=db_holding.current_price_cny,
        purchase_date=db_holding.purchase_date.isoformat() if db_holding.purchase_date else None
    )


@router.delete("/{holding_id}")
async def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """删除持仓"""
    db_holding = db.query(Holding).filter(Holding.id == holding_id).first()
    if not db_holding:
        raise HTTPException(status_code=404, detail="持仓不存在")
    
    db.delete(db_holding)
    db.commit()
    
    return {"message": "持仓已删除"}


@router.post("/batch")
async def import_holdings(holdings: List[HoldingCreate], db: Session = Depends(get_db)):
    """批量导入持仓"""
    created = []
    errors = []
    
    for h in holdings:
        try:
            result = await create_holding(h, db)
            created.append(result.stock_code)
        except Exception as e:
            errors.append({"code": h.stock_code, "error": str(e)})
    
    return {
        "created": created,
        "errors": errors,
        "total": len(holdings),
        "success": len(created)
    }
