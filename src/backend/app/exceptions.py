"""
自定义异常类
Custom Exceptions
"""
from fastapi import HTTPException, status


class StockNotFoundError(HTTPException):
    """股票不存在"""
    def __init__(self, code: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"股票 {code} 不存在"
        )


class DataNotFoundError(HTTPException):
    """数据不存在"""
    def __init__(self, message: str = "数据不存在"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )


class ExternalServiceError(HTTPException):
    """外部服务错误"""
    def __init__(self, service: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"外部服务 {service} 不可用"
        )


class ValidationError(HTTPException):
    """验证错误"""
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )


class UnauthorizedError(HTTPException):
    """未授权"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
