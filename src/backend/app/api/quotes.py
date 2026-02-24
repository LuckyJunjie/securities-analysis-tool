"""
行情 API 路由
Quote API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.quote_service import QuoteService

router = APIRouter()


class QuoteResponse(BaseModel):
    """行情响应"""
    code: str
    name: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    timestamp: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/{code}", response_model=QuoteResponse)
async def get_quote(code: str):
    """获取单只股票行情"""
    quote = await QuoteService.get_quote(code)
    
    if not quote:
        raise HTTPException(
            status_code=404, 
            detail=f"无法获取 {code} 的行情数据"
        )
    
    return quote


@router.post("/batch")
async def get_batch_quotes(codes: List[str]):
    """批量获取股票行情"""
    results = await QuoteService.batch_get_quotes(codes)
    
    # 统计成功/失败
    success = sum(1 for v in results.values() if "error" not in v)
    failed = len(results) - success
    
    return {
        "total": len(codes),
        "success": success,
        "failed": failed,
        "quotes": results
    }


@router.get("/")
async def get_multiple_quotes(codes: str):
    """获取多只股票行情 (逗号分隔)"""
    code_list = [c.strip() for c in codes.split(",")]
    return await get_batch_quotes(code_list)
