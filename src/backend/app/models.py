"""
数据库模型定义
Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class StockStatus(enum.Enum):
    """股票状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"


class Stock(Base):
    """股票基本信息"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, comment="股票代码")
    name = Column(String(100), comment="股票名称")
    market = Column(String(20), comment="市场 (SH/SZ/BJ)")
    industry = Column(String(100), comment="所属行业")
    listing_date = Column(DateTime, comment="上市日期")
    status = Column(Enum(StockStatus), default=StockStatus.ACTIVE)
    
    # 关系
    financial_indicators = relationship("FinancialIndicator", back_populates="stock")
    alerts = relationship("AlertRecord", back_populates="stock")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialIndicator(Base):
    """财务指标"""
    __tablename__ = "financial_indicators"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    
    # 报告期
    report_date = Column(DateTime, comment="报告期")
    report_type = Column(String(20), comment="报告类型 (Q1/Q2/Q3/Q4)")
    
    # 盈利能力
    revenue = Column(Float, comment="营业收入(万元)")
    net_profit = Column(Float, comment="净利润(万元)")
    roe = Column(Float, comment="净资产收益率(%)")
    gross_margin = Column(Float, comment="毛利率(%)")
    net_margin = Column(Float, comment="净利率(%)")
    
    # 估值指标
    pe = Column(Float, comment="市盈率")
    pb = Column(Float, comment="市净率")
    
    # 成长性
    revenue_growth = Column(Float, comment="营收增长率(%)")
    profit_growth = Column(Float, comment="净利润增长率(%)")
    
    # 财务健康
    debt_ratio = Column(Float, comment="资产负债率(%)")
    current_ratio = Column(Float, comment="流动比率")
    quick_ratio = Column(Float, comment="速动比率")
    
    # 运营效率
    turnover_rate = Column(Float, comment="周转率(%)")
    
    # 关系
    stock = relationship("Stock", back_populates="financial_indicators")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class MacroIndicator(Base):
    """宏观指标"""
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, index=True)
    
    # 指标类型
    indicator_type = Column(String(50), index=True, comment="指标类型 (GDP/PPI/CPI/Power/Electricity)")
    
    # 数值
    value = Column(Float, comment="数值")
    unit = Column(String(20), comment="单位")
    yoy = Column(Float, comment="同比增长率(%)")
    
    # 时间
    data_date = Column(DateTime, index=True, comment="数据日期")
    data_period = Column(String(20), comment="期间 (月度/季度/年度)")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertRule(Base):
    """预警规则"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, comment="规则名称")
    description = Column(Text, comment="规则描述")
    
    # 条件配置
    indicator = Column(String(50), comment="指标名称")
    operator = Column(String(10), comment="操作符 (>/<//>=/<=/=)")
    threshold = Column(Float, comment="阈值")
    
    # 严重程度
    severity = Column(String(20), comment="严重程度 (green/yellow/red)")
    enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AlertRecord(Base):
    """预警记录"""
    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), index=True)
    
    # 预警信息
    alert_type = Column(String(50), comment="预警类型")
    message = Column(Text, comment="预警消息")
    severity = Column(String(20), comment="严重程度")
    value = Column(Float, comment="触发值")
    threshold = Column(Float, comment="阈值")
    
    # 状态
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # 关系
    stock = relationship("Stock", back_populates="alerts")
    rule = relationship("AlertRule")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Portfolio(Base):
    """持仓记录"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    
    # 持仓信息
    shares = Column(Integer, comment="持股数量")
    avg_cost = Column(Float, comment="平均成本")
    current_price = Column(Float, comment="当前价格")
    
    # 时间
    purchase_date = Column(DateTime, comment="买入日期")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
