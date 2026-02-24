"""
预警 API 路由
Alert API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import AlertRule, AlertRecord, Stock

router = APIRouter()


class AlertRuleResponse(BaseModel):
    """预警规则响应"""
    id: int
    name: str
    description: Optional[str] = None
    indicator: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    severity: str
    enabled: bool
    
    class Config:
        from_attributes = True


class AlertRecordResponse(BaseModel):
    """预警记录响应"""
    id: int
    stock_id: Optional[int] = None
    alert_type: Optional[str] = None
    message: Optional[str] = None
    severity: str
    value: Optional[float] = None
    is_read: bool
    is_resolved: bool
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============= 预警规则 =============

@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取预警规则列表"""
    query = db.query(AlertRule)
    
    if enabled is not None:
        query = query.filter(AlertRule.enabled == enabled)
    
    return query.all()


@router.post("/rules")
async def create_alert_rule(
    rule: AlertRuleResponse,
    db: Session = Depends(get_db)
):
    """创建预警规则"""
    db_rule = AlertRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


# ============= 预警记录 =============

@router.get("/", response_model=List[AlertRecordResponse])
async def get_alerts(
    severity: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_resolved: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取预警记录"""
    query = db.query(AlertRecord)
    
    if severity:
        query = query.filter(AlertRecord.severity == severity)
    if is_read is not None:
        query = query.filter(AlertRecord.is_read == is_read)
    if is_resolved is not None:
        query = query.filter(AlertRecord.is_resolved == is_resolved)
    
    alerts = query.order_by(AlertRecord.created_at.desc()).limit(limit).all()
    return alerts


@router.post("/check/{stock_code}")
async def check_stock_alerts(stock_code: str, db: Session = Depends(get_db)):
    """检查股票预警"""
    # 获取股票
    stock = db.query(Stock).filter(Stock.code == stock_code).first()
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    
    # 获取最新财务指标
    from app.models import FinancialIndicator
    indicator = db.query(FinancialIndicator).filter(
        FinancialIndicator.stock_id == stock.id
    ).order_by(FinancialIndicator.report_date.desc()).first()
    
    if not indicator:
        return {"message": "暂无财务数据", "alerts": []}
    
    alerts = []
    
    # 检查 PE
    if indicator.pe and indicator.pe > 50:
        alerts.append({
            "type": "high_pe",
            "severity": "yellow",
            "message": f"市盈率偏高 ({indicator.pe:.1f})",
            "value": indicator.pe,
            "threshold": 50
        })
    
    # 检查 ROE
    if indicator.roe and indicator.roe < 5:
        alerts.append({
            "type": "low_roe",
            "severity": "red",
            "message": f"净资产收益率偏低 ({indicator.roe:.1f}%)",
            "value": indicator.roe,
            "threshold": 5
        })
    
    # 检查净利润下降
    if indicator.profit_growth and indicator.profit_growth < -50:
        alerts.append({
            "type": "profit_drop",
            "severity": "red",
            "message": f"净利润大幅下降 ({indicator.profit_growth:.1f}%)",
            "value": indicator.profit_growth,
            "threshold": -50
        })
    
    return {"stock_code": stock_code, "alerts": alerts}


@router.patch("/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """标记预警为已读"""
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    alert.is_read = True
    db.commit()
    return {"message": "已标记为已读"}


@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """解决预警"""
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": "预警已解决"}
