"""
宏观数据 API 路由
Macro Data API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database import get_db
from app.models import MacroIndicator

router = APIRouter()


class MacroIndicatorResponse(BaseModel):
    """宏观指标响应"""
    id: int
    indicator_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    yoy: Optional[float] = None
    data_date: Optional[str] = None
    
    class Config:
        from_attributes = True


class MacroSummary(BaseModel):
    """宏观摘要"""
    gdp: Optional[dict] = None
    ppi: Optional[dict] = None
    cpi: Optional[dict] = None
    electricity: Optional[dict] = None
    power: Optional[dict] = None


@router.get("/", response_model=List[MacroIndicatorResponse])
async def get_macro_indicators(
    indicator_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取宏观指标列表"""
    query = db.query(MacroIndicator)
    
    if indicator_type:
        query = query.filter(MacroIndicator.indicator_type == indicator_type)
    
    if start_date:
        query = query.filter(MacroIndicator.data_date >= start_date)
    if end_date:
        query = query.filter(MacroIndicator.data_date <= end_date)
    
    indicators = query.order_by(MacroIndicator.data_date.desc()).limit(limit).all()
    return indicators


@router.get("/summary", response_model=MacroSummary)
async def get_macro_summary(db: Session = Depends(get_db)):
    """获取宏观数据摘要"""
    result = {}
    
    # 获取最新各项指标
    for indicator_type in ["GDP", "PPI", "CPI", "Electricity", "Power"]:
        indicator = db.query(MacroIndicator).filter(
            MacroIndicator.indicator_type == indicator_type
        ).order_by(MacroIndicator.data_date.desc()).first()
        
        if indicator:
            result[indicator_type.lower()] = {
                "value": indicator.value,
                "unit": indicator.unit,
                "yoy": indicator.yoy,
                "date": indicator.data_date.isoformat() if indicator.data_date else None
            }
    
    return result


@router.get("/{indicator_type}", response_model=List[MacroIndicatorResponse])
async def get_indicator_history(
    indicator_type: str,
    limit: int = 24,
    db: Session = Depends(get_db)
):
    """获取特定指标历史"""
    indicators = db.query(MacroIndicator).filter(
        MacroIndicator.indicator_type == indicator_type
    ).order_by(MacroIndicator.data_date.desc()).limit(limit).all()
    
    if not indicators:
        raise HTTPException(status_code=404, detail=f"指标 {indicator_type} 不存在")
    
    return indicators
