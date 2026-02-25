"""
数据同步服务 - 定时更新股票财务数据
Data Sync Service - Scheduled financial data updates
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# 全局调度器
scheduler: Optional[AsyncIOScheduler] = None


class DataSyncService:
    """数据同步服务"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
    
    async def sync_all_stocks(self, db):
        """同步所有股票的财务数据"""
        from app.models import Stock
        from app.data_fetcher import fetch_stock_financials
        
        stocks = db.query(Stock).all()
        logger.info(f"Starting sync for {len(stocks)} stocks...")
        
        success_count = 0
        for stock in stocks:
            try:
                data = await fetch_stock_financials(stock.code)
                if data:
                    # 更新数据库
                    self._update_stock_data(stock, data, db)
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to sync {stock.code}: {e}")
        
        logger.info(f"Sync completed: {success_count}/{len(stocks)} successful")
        return success_count
    
    def _update_stock_data(self, stock, data, db):
        """更新股票数据"""
        from app.models import FinancialIndicator
        
        # 检查是否已有数据
        existing = db.query(FinancialIndicator).filter(
            FinancialIndicator.stock_id == stock.id
        ).first()
        
        if existing:
            # 更新现有数据
            for key, value in data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
        else:
            # 创建新记录
            indicator = FinancialIndicator(
                stock_id=stock.id,
                **{k: v for k, v in data.items() if hasattr(FinancialIndicator, k)}
            )
            db.add(indicator)
        
        db.commit()
    
    async def sync_stock_price(self, stock_code: str, db):
        """同步单只股票价格"""
        from app.services.quote_service import QuoteService
        from app.models import Holding
        
        quote = await QuoteService.get_quote(stock_code)
        if quote:
            # 更新持仓价格
            holdings = db.query(Holding).filter(Holding.stock_code == stock_code).all()
            for holding in holdings:
                holding.current_price = quote.get('price')
                holding.last_updated = datetime.utcnow()
            db.commit()
            logger.info(f"Price updated for {stock_code}: {quote.get('price')}")
            return True
        return False
    
    async def sync_portfolio_prices(self, db):
        """同步所有持仓的价格"""
        from app.models import Holding
        
        holdings = db.query(Holding).all()
        logger.info(f"Updating prices for {len(holdings)} holdings...")
        
        success_count = 0
        for holding in holdings:
            try:
                quote = await QuoteService.get_quote(holding.stock_code)
                if quote:
                    holding.current_price = quote.get('price')
                    holding.price_change = quote.get('change')
                    holding.price_change_pct = quote.get('change_pct')
                    holding.last_updated = datetime.utcnow()
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to update {holding.stock_code}: {e}")
        
        db.commit()
        logger.info(f"Price sync completed: {success_count}/{len(holdings)} successful")
        return success_count


# 全局服务实例
sync_service = DataSyncService()


def init_scheduler(db):
    """初始化调度器"""
    global scheduler
    
    scheduler = AsyncIOScheduler()
    
    # 每天凌晨 2 点同步财务数据
    scheduler.add_job(
        lambda: sync_service.sync_all_stocks(db),
        CronTrigger(hour=2, minute=0),
        id="sync_financials",
        name="财务数据同步",
        replace_existing=True
    )
    
    # 每 5 分钟同步持仓价格
    scheduler.add_job(
        lambda: sync_service.sync_portfolio_prices(db),
        CronTrigger(minute=*/5),
        id="sync_prices",
        name="持仓价格同步",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """停止调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
