"""
缓存服务
Cache Service - 本地内存缓存
"""
import time
from typing import Optional, Any
from datetime import datetime


class CacheService:
    """简单的内存缓存服务"""
    
    def __init__(self):
        self._cache: dict[str, dict] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            entry = self._cache[key]
            # 检查是否过期
            if time.time() - entry['timestamp'] < entry['ttl']:
                return entry['value']
            else:
                # 过期删除
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存 (默认5分钟)"""
        self._cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            'total_keys': len(self._cache),
            'keys': list(self._cache.keys())
        }


# 全局缓存实例
cache = CacheService()


# 缓存装饰器
def cached(key_prefix: str, ttl: int = 300):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存key
            cache_key = f"{key_prefix}:{':'.join(map(str, args))}"
            
            # 尝试获取缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# 使用示例
async def get_cached_quote(code: str) -> dict:
    """获取缓存的价格"""
    cache_key = f"quote:{code}"
    
    # 尝试从缓存获取
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # 从外部获取
    from app.services.quote_service import QuoteService
    quote = await QuoteService.get_quote(code)
    
    if quote:
        # 存入缓存 (5分钟)
        cache.set(cache_key, quote, 300)
    
    return quote


async def refresh_quote(code: str) -> dict:
    """强制刷新价格 (清除缓存后重新获取)"""
    cache_key = f"quote:{code}"
    cache.delete(cache_key)
    return await get_cached_quote(code)
