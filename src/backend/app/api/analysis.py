"""
分析 API 路由
Analysis API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Stock, FinancialIndicator

router = APIRouter()


class AnalysisRequest(BaseModel):
    """分析请求"""
    code: str
    indicators: list[str] = ["PE", "PB", "ROE", "safety_margin"]


class ValuationResult(BaseModel):
    """估值结果"""
    pe: Optional[float] = None
    pb: Optional[float] = None
    dcfrate: Optional[float] = None
    graham_number: Optional[float] = None
    safety_margin: Optional[float] = None
    rating: str = "N/A"


class GrowthResult(BaseModel):
    """成长性分析"""
    revenue_cagr: Optional[float] = None
    profit_cagr: Optional[float] = None
    trend: str = "N/A"


class AnalysisResponse(BaseModel):
    """分析响应"""
    code: str
    name: str
    valuation: ValuationResult
    growth: GrowthResult
    health_score: int = 0
    recommendation: str = "N/A"


@router.get("/{code}", response_model=AnalysisResponse)
async def analyze_stock(code: str, db: Session = Depends(get_db)):
    """分析股票"""
    # 获取股票
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 获取财务指标
    indicators = db.query(FinancialIndicator).filter(
        FinancialIndicator.stock_id == stock.id
    ).order_by(FinancialIndicator.report_date.desc()).limit(10).all()
    
    if not indicators:
        raise HTTPException(status_code=404, detail="暂无财务数据")
    
    # 计算估值
    latest = indicators[0]
    pe = latest.pe or 0
    pb = latest.pb or 0
    roe = latest.roe or 0
    
    # 格雷厄姆数字
    graham_number = 0
    if latest.net_profit and latest.roe:
        eps = latest.net_profit / 10000  # 转换为元
        graham_number = (eps * (8.5 + 2 * 10)) ** 0.5 * 15.6
    
    # 安全边际 (简化计算)
    safety_margin = 0
    if roe > 0 and pe > 0:
        earnings_yield = (1 / pe) * 100
        safety_margin = earnings_yield - 10  # 假设10%为无风险利率
    
    # 评级
    if roe > 15 and pe < 15 and safety_margin > 0:
        rating = "A"
    elif roe > 10 and pe < 25:
        rating = "B"
    else:
        rating = "C"
    
    # 成长性
    revenue_cagr = None
    profit_cagr = None
    if len(indicators) >= 4:
        # 简化 CAGR 计算
        latest_revenue = indicators[0].revenue or 0
        old_revenue = indicators[3].revenue or 0
        if old_revenue > 0:
            revenue_cagr = ((latest_revenue / old_revenue) ** 0.25 - 1) * 100
    
    # 健康评分 (0-100)
    health_score = 0
    if roe > 15: health_score += 30
    elif roe > 10: health_score += 20
    elif roe > 5: health_score += 10
    
    if latest.gross_margin and latest.gross_margin > 30: health_score += 20
    if latest.current_ratio and latest.current_ratio > 2: health_score += 20
    if safety_margin > 0: health_score += 30
    
    # 建议
    if health_score >= 80 and rating in ["A", "B"]:
        recommendation = "强烈推荐"
    elif health_score >= 60:
        recommendation = "可以考虑"
    elif health_score >= 40:
        recommendation = "谨慎考虑"
    else:
        recommendation = "不推荐"
    
    return {
        "code": stock.code,
        "name": stock.name,
        "valuation": {
            "pe": pe,
            "pb": pb,
            "graham_number": round(graham_number, 2) if graham_number else None,
            "safety_margin": round(safety_margin, 2) if safety_margin else None,
            "rating": rating
        },
        "growth": {
            "revenue_cagr": round(revenue_cagr, 2) if revenue_cagr else None,
            "profit_cagr": round(profit_cagr, 2) if profit_cagr else None,
            "trend": "增长" if revenue_cagr and revenue_cagr > 0 else "下降"
        },
        "health_score": health_score,
        "recommendation": recommendation
    }


@router.post("/batch")
async def batch_analyze(codes: list[str], db: Session = Depends(get_db)):
    """批量分析股票"""
    results = []
    for code in codes:
        try:
            result = await analyze_stock(code, db)
            results.append(result)
        except Exception as e:
            results.append({"code": code, "error": str(e)})
    return results
