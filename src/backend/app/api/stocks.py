"""
股票 API 路由
Stock API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Stock, FinancialIndicator

router = APIRouter()


# Pydantic 模型
class StockResponse(BaseModel):
    """股票响应模型"""
    id: int
    code: str
    name: str
    market: Optional[str] = None
    industry: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True


class StockDetailResponse(StockResponse):
    """股票详情响应"""
    financial_indicators: List["FinancialIndicatorResponse"] = []
    
    class Config:
        from_attributes = True


class FinancialIndicatorResponse(BaseModel):
    """财务指标响应"""
    id: int
    report_date: Optional[str] = None
    report_type: Optional[str] = None
    revenue: Optional[float] = None
    net_profit: Optional[float] = None
    roe: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    
    class Config:
        from_attributes = True


# 更新前向引用
StockDetailResponse.model_rebuild()


@router.get("/", response_model=List[StockResponse])
async def get_stocks(
    market: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取股票列表"""
    query = db.query(Stock)
    
    if market:
        query = query.filter(Stock.market == market)
    if industry:
        query = query.filter(Stock.industry == industry)
    
    stocks = query.limit(limit).all()
    return stocks


@router.get("/{code}", response_model=StockDetailResponse)
async def get_stock(code: str, db: Session = Depends(get_db)):
    """获取股票详情"""
    stock = db.query(Stock).filter(Stock.code == code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    return stock


@router.post("/")
async def create_stock(stock: StockResponse, db: Session = Depends(get_db)):
    """创建股票"""
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock
