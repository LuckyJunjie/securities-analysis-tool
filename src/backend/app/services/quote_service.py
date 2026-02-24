"""
实时行情服务
Real-time Quote Service

支持多种数据源:
1. AkShare (免费)
2. 新浪财经 (免费)
3. 腾讯财经 (免费)
"""
import httpx
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QuoteService:
    """实时行情服务"""
    
    @staticmethod
    async def get_quote_akshare(code: str) -> Optional[dict]:
        """使用 AkShare 获取行情 (需要安装 akshare)"""
        try:
            import akshare as ak
            from datetime import datetime
            
            # 格式化代码
            if code.endswith('.HK'):
                symbol = code.replace('.HK', '')
                df = ak.stock_zh_a_spot_em() if symbol.isdigit() else None
            elif code.endswith('.SH') or code.endswith('.SZ'):
                symbol = code.replace('.SH', '').replace('.SZ', '')
                df = ak.stock_zh_a_spot_em()
                
                if df is not None:
                    row = df[df['代码'] == symbol]
                    if not row.empty:
                        return {
                            "code": code,
                            "name": row.iloc[0]['名称'],
                            "price": float(row.iloc[0]['最新价']),
                            "change": float(row.iloc[0]['涨跌幅']),
                            "change_pct": float(row.iloc[0]['涨跌幅']),
                            "volume": float(row.iloc[0]['成交量']),
                            "amount": float(row.iloc[0]['成交额']),
                            "timestamp": datetime.now().isoformat()
                        }
            return None
        except Exception as e:
            logger.warning(f"AkShare quote failed for {code}: {e}")
            return None

    @staticmethod
    async def get_quote_sina(code: str) -> Optional[dict]:
        """使用新浪财经获取行情 (HTTP 请求)"""
        try:
            # 格式化代码
            if code.endswith('.SH'):
                symbol = f"sh{code.replace('.SH', '')}"
            elif code.endswith('.SZ'):
                symbol = f"sz{code.replace('.SZ', '')}"
            elif code.endswith('.HK'):
                symbol = f"hk{code.replace('.HK', '')}"
            else:
                return None
            
            url = f"https://hq.sinajs.cn/list={symbol}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
            if response.status_code == 200:
                content = response.text
                # 解析返回数据
                match = re.search(r'"(.*)"', content)
                if match:
                    data = match.group(1).split(',')
                    if len(data) >= 10:
                        return {
                            "code": code,
                            "name": data[0],
                            "price": float(data[1]) if data[1] else 0,
                            "change": float(data[2]) if data[2] else 0,
                            "change_pct": float(data[3]) if data[3] else 0,
                            "volume": float(data[4]) if data[4] else 0,
                            "amount": float(data[5]) if data[5] else 0,
                        }
            return None
        except Exception as e:
            logger.warning(f"Sina quote failed for {code}: {e}")
            return None

    @staticmethod
    async def get_quote_tencent(code: str) -> Optional[dict]:
        """使用腾讯财经获取行情"""
        try:
            # 格式化代码
            if code.endswith('.SH'):
                symbol = f"sh{code.replace('.SH', '')}"
            elif code.endswith('.SZ'):
                symbol = f"sz{code.replace('.SZ', '')}"
            elif code.endswith('.HK'):
                symbol = f"hk{code.replace('.HK', '')}"
            else:
                return None
            
            url = f"https://qt.gtimg.cn/q={symbol}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
            if response.status_code == 200:
                content = response.text
                # 腾讯返回格式: sh600519="..." 
                match = re.search(r'"([^"]+)"', content)
                if match:
                    data = match.group(1).split('~')
                    if len(data) >= 50:
                        return {
                            "code": code,
                            "name": data[1],
                            "price": float(data[3]) if data[3] else 0,
                            "change": float(data[4]) if data[4] else 0,
                            "change_pct": float(data[5]) if data[5] else 0,
                            "volume": float(data[6]) if data[6] else 0,
                            "amount": float(data[7]) if data[7] else 0,
                            "high": float(data[33]) if data[33] else 0,
                            "low": float(data[34]) if data[34] else 0,
                            "open": float(data[5]) if data[5] else 0,
                        }
            return None
        except Exception as e:
            logger.warning(f"Tencent quote failed for {code}: {e}")
            return None

    @staticmethod
    async def get_quote(code: str) -> Optional[dict]:
        """获取实时行情 (尝试多个数据源)"""
        # 优先尝试腾讯财经 (较快)
        quote = await QuoteService.get_quote_tencent(code)
        if quote:
            return quote
        
        # 备选新浪财经
        quote = await QuoteService.get_quote_sina(code)
        if quote:
            return quote
        
        return None

    @staticmethod
    async def batch_get_quotes(codes: list[str]) -> dict:
        """批量获取行情"""
        results = {}
        for code in codes:
            quote = await QuoteService.get_quote(code)
            if quote:
                results[code] = quote
            else:
                results[code] = {"error": "Failed to fetch quote"}
        return results


# 测试
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试 A 股
        quote = await QuoteService.get_quote("600519.SH")
        print("茅台:", quote)
        
        # 测试港股
        quote = await QuoteService.get_quote("0700.HK")
        print("腾讯:", quote)
    
    asyncio.run(test())
