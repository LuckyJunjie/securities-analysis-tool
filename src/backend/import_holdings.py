"""
导入持仓数据到数据库
"""
import sys
sys.path.insert(0, '/home/pi/.openclaw/workspace/securities-analysis-tool/src/backend')

from main import app
from app.database import SessionLocal
from app.models import Stock, Holding, MarketType
from data.holdings_data import HOLDINGS_DATA
from datetime import datetime

HKD_TO_CNY = 0.85


def import_holdings():
    """导入持仓数据"""
    db = SessionLocal()
    
    try:
        # 导入每只股票
        for h in HOLDINGS_DATA:
            code = h["stock_code"]
            name = h["stock_name"]
            shares = h["shares"]
            avg_cost = h["avg_cost"]
            current_price = h.get("current_price", avg_cost)
            
            # 判断市场类型
            if code.endswith(".HK"):
                market_type = MarketType.HK_STOCK
                market = "HK"
            elif code.endswith(".SH"):
                market_type = MarketType.A_SHARE
                market = "SH"
            elif code.endswith(".SZ"):
                market_type = MarketType.A_SHARE
                market = "SZ"
            else:
                market_type = MarketType.A_SHARE
                market = "SZ"
            
            # 查找或创建股票
            stock = db.query(Stock).filter(Stock.code == code).first()
            if not stock:
                stock = Stock(
                    code=code,
                    name=name,
                    market=market,
                    market_type=market_type,
                    original_code=code.replace(".HK", "").replace(".SH", "").replace(".SZ", "")
                )
                db.add(stock)
                db.commit()
                db.refresh(stock)
                print(f"✓ 添加股票: {code} {name}")
            else:
                print(f"  股票已存在: {code}")
            
            # 检查是否已有持仓
            existing = db.query(Holding).filter(Holding.stock_id == stock.id).first()
            if existing:
                print(f"  持仓已存在: {code}")
                continue
            
            # 创建持仓
            avg_cost_cny = avg_cost * (HKD_TO_CNY if market_type == MarketType.HK_STOCK else 1)
            current_price_cny = current_price * (HKD_TO_CNY if market_type == MarketType.HK_STOCK else 1)
            
            holding = Holding(
                stock_id=stock.id,
                shares=shares,
                avg_cost=avg_cost,
                avg_cost_cny=avg_cost_cny,
                current_price=current_price,
                current_price_cny=current_price_cny,
                purchase_date=datetime(2026, 2, 14)
            )
            db.add(holding)
            print(f"✓ 添加持仓: {code} x {shares}")
        
        db.commit()
        print("\n=== 导入完成 ===")
        
        # 显示汇总
        holdings = db.query(Holding).all()
        total_mv = 0
        total_cost = 0
        
        for h in holdings:
            stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
            if stock:
                mv = h.current_price * h.shares
                cost = h.avg_cost * h.shares
                total_mv += mv
                total_cost += cost
                print(f"  {stock.code} {stock.name}: {h.shares} x {h.current_price} = {mv:,.0f}")
        
        print(f"\n总市值: {total_mv:,.0f}")
        print(f"总成本: {total_cost:,.0f}")
        print(f"盈亏: {total_mv - total_cost:,.0f}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import_holdings()
