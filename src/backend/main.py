"""
证券分析工具 - 主应用入口
Securities Analysis Tool - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import stocks, analysis, macro, alerts, holdings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时清理资源
    pass


# 创建 FastAPI 应用
app = FastAPI(
    title="证券分析工具 API",
    description="基于价值投资理念的量化证券分析系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(stocks.router, prefix="/api/stocks", tags=["股票"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["分析"])
app.include_router(macro.router, prefix="/api/macro", tags=["宏观"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["预警"])
app.include_router(holdings.router, prefix="/api/holdings", tags=["持仓管理"])


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": "证券分析工具 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
