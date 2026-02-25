"""
同步管理 API - 手动触发数据同步
Sync Management API - Manual sync triggers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.sync_service import sync_service

router = APIRouter()


class SyncResponse(BaseModel):
    """同步响应"""
    success: bool
    message: str
    timestamp: str
    details: dict = {}


@router.post("/prices", response_model=SyncResponse)
async def sync_portfolio_prices(db: Session = Depends(get_db)):
    """同步所有持仓的实时价格"""
    try:
        count = await sync_service.sync_portfolio_prices(db)
        return SyncResponse(
            success=True,
            message=f"成功同步 {count} 个持仓的价格",
            timestamp=datetime.utcnow().isoformat(),
            details={"holdings_updated": count}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/stock/{stock_code}", response_model=SyncResponse)
async def sync_stock_price(stock_code: str, db: Session = Depends(get_db)):
    """同步指定股票的价格"""
    try:
        success = await sync_service.sync_stock_price(stock_code, db)
        if success:
            return SyncResponse(
                success=True,
                message=f"成功同步 {stock_code} 的价格",
                timestamp=datetime.utcnow().isoformat(),
                details={"stock_code": stock_code}
            )
        else:
            raise HTTPException(status_code=404, detail=f"无法获取 {stock_code} 的价格")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/financials", response_model=SyncResponse)
async def sync_all_financials(db: Session = Depends(get_db)):
    """同步所有股票的财务数据"""
    try:
        count = await sync_service.sync_all_stocks(db)
        return SyncResponse(
            success=True,
            message=f"成功同步 {count} 只股票的财务数据",
            timestamp=datetime.utcnow().isoformat(),
            details={"stocks_updated": count}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/status")
async def get_sync_status():
    """获取同步服务状态"""
    return {
        "status": "running",
        "message": "数据同步服务正常运行",
        "timestamp": datetime.utcnow().isoformat()
    }
