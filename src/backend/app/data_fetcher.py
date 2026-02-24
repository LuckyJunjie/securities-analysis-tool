"""
数据采集模块
Data Fetcher - AkShare Integration
"""
import akshare as ak
from datetime import datetime, timedelta
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """数据采集器"""
    
    @staticmethod
    def get_stock_list() -> list[dict]:
        """获取A股股票列表"""
        try:
            df = ak.stock_info_a_code_name()
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    @staticmethod
    def get_stock_financial(code: str, indicator: str = "main") -> Optional[dict]:
        """
        获取股票财务指标
        
        Args:
            code: 股票代码 (如: 000001)
            indicator: 指标类型 (main/profit/growth/balance/cash)
        """
        try:
            df = ak.stock_financial_abstract_ths(symbol=code, indicator=indicator)
            return df.to_dict('records') if not df.empty else None
        except Exception as e:
            logger.error(f"获取财务数据失败 {code}: {e}")
            return None
    
    @staticmethod
    def get_macro_power() -> Optional[dict]:
        """获取发电量数据"""
        try:
            df = ak.macro_china_power_generation()
            return df.to_dict('records') if not df.empty else None
        except Exception as e:
            logger.error(f"获取发电量数据失败: {e}")
            return None
    
    @staticmethod
    def get_macro_ppi() -> Optional[dict]:
        """获取PPI数据"""
        try:
            df = ak.macro_china_ppi()
            return df.to_dict('records') if not df.empty else None
        except Exception as e:
            logger.error(f"获取PPI数据失败: {e}")
            return None
    
    @staticmethod
    def get_macro_cpi() -> Optional[dict]:
        """获取CPI数据"""
        try:
            df = ak.macro_china_cpi()
            return df.to_dict('records') if not df.empty else None
        except Exception as e:
            logger.error(f"获取CPI数据失败: {e}")
            return None
    
    @staticmethod
    def get_stock_valuation(code: str) -> Optional[dict]:
        """获取股票估值数据"""
        try:
            df = ak.stock_individual_info_em(symbol=code)
            return df.to_dict('records') if not df.empty else None
        except Exception as e:
            logger.error(f"获取估值数据失败 {code}: {e}")
            return None


# 测试
if __name__ == "__main__":
    fetcher = DataFetcher()
    
    print("=== 测试数据采集 ===")
    
    # 测试股票列表
    stocks = fetcher.get_stock_list()
    print(f"股票数量: {len(stocks)}")
    if stocks:
        print(f"示例: {stocks[0]}")
    
    # 测试宏观数据
    power = fetcher.get_macro_power()
    if power:
        print(f"发电量数据: {power[0]}")
