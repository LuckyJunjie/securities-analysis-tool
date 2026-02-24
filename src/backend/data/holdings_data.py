"""
初始化用户持仓数据
Import User Holdings
"""
from datetime import datetime

# 用户持仓数据 (2026-02-14)
HOLDINGS_DATA = [
    # 港股
    {"stock_code": "0700.HK", "stock_name": "腾讯控股", "shares": 600, "avg_cost": 532.0, "current_price": 532.0},
    {"stock_code": "1810.HK", "stock_name": "小米集团", "shares": 6400, "avg_cost": 36.84, "current_price": 36.84},
    {"stock_code": "9988.HK", "stock_name": "阿里巴巴-W", "shares": 600, "avg_cost": 155.4, "current_price": 155.4},
    {"stock_code": "2318.HK", "stock_name": "中国平安", "shares": 4000, "avg_cost": 65.29, "current_price": 65.29},
    {"stock_code": "0941.HK", "stock_name": "中国移动", "shares": 100, "avg_cost": 92.61, "current_price": 92.61},
    
    # A股
    {"stock_code": "000651.SZ", "stock_name": "格力电器", "shares": 4900, "avg_cost": 38.37, "current_price": 38.37},
    {"stock_code": "600519.SH", "stock_name": "贵州茅台", "shares": 100, "avg_cost": 1485.3, "current_price": 1485.3},
    {"stock_code": "000858.SZ", "stock_name": "五粮液", "shares": 1000, "avg_cost": 106.06, "current_price": 106.06},
    {"stock_code": "601888.SH", "stock_name": "中国中免", "shares": 1100, "avg_cost": 94.64, "current_price": 94.64},
    {"stock_code": "600887.SH", "stock_name": "伊利股份", "shares": 1800, "avg_cost": 26.48, "current_price": 26.48},
    {"stock_code": "000333.SZ", "stock_name": "美的集团", "shares": 600, "avg_cost": 79.05, "current_price": 79.05},
    {"stock_code": "600900.SH", "stock_name": "长江电力", "shares": 1600, "avg_cost": 26.0, "current_price": 26.0},
    {"stock_code": "002714.SZ", "stock_name": "牧原股份", "shares": 900, "avg_cost": 45.35, "current_price": 45.35},
    {"stock_code": "600566.SH", "stock_name": "济川药业", "shares": 1100, "avg_cost": 27.18, "current_price": 27.18},
    {"stock_code": "600036.SH", "stock_name": "招商银行", "shares": 300, "avg_cost": 38.71, "current_price": 38.71},
    {"stock_code": "601088.SH", "stock_name": "中国神华", "shares": 300, "avg_cost": 41.45, "current_price": 41.45},
    {"stock_code": "601919.SH", "stock_name": "中远海控", "shares": 800, "avg_cost": 14.31, "current_price": 14.31},
    {"stock_code": "601006.SH", "stock_name": "大秦铁路", "shares": 2000, "avg_cost": 5.04, "current_price": 5.04},
]


def get_holdings():
    """获取持仓数据"""
    return HOLDINGS_DATA


if __name__ == "__main__":
    print("=== 用户持仓数据 ===")
    print(f"总持仓: {len(HOLDINGS_DATA)} 只")
    
    # 计算总市值
    total = sum(h["shares"] * h["current_price"] for h in HOLDINGS_DATA)
    print(f"总市值: ¥{total:,.2f}")
    
    # 按市场分组
    hk_stocks = [h for h in HOLDINGS_DATA if h["stock_code"].endswith(".HK")]
    a_stocks = [h for h in HOLDINGS_DATA if h["stock_code"].endswith((".SH", ".SZ"))]
    
    hk_total = sum(h["shares"] * h["current_price"] for h in hk_stocks)
    a_total = sum(h["shares"] * h["current_price"] for h in a_stocks)
    
    print(f"\n港股: {len(hk_stocks)} 只, 市值 ¥{hk_total:,.2f} ({hk_total/total*100:.1f}%)")
    print(f"A股: {len(a_stocks)} 只, 市值 ¥{a_total:,.2f} ({a_total/total*100:.1f}%)")
