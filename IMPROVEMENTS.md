# 证券分析工具 - 代码改进建议

**项目:** securities-analysis-tool  
**日期:** 2026-02-24  
**版本:** 1.0

---

## 📋 当前代码问题分析

### 1. 数据模型问题

#### 1.1 股票代码格式不一致
**问题:** 当前只支持 A 股格式，但用户持仓包含港股
```python
# 当前代码
code = Column(String(10), ...)  # 只能存 600519.SH

# 持仓数据
0700.HK  # 腾讯控股 (港股)
2318.HK  # 中国平安 (港股)
```

**建议:**
- 扩展 code 字段长度: `String(20)`
- 添加市场类型字段: `market_type: Enum(A股, 港股, 美股)`
- 支持多种代码格式解析

#### 1.2 缺少持仓表关联
**问题:** 用户需要管理持仓，但没有持仓管理功能

**建议:**
- 完善 Portfolio 表 (已定义但未使用)
- 添加成本价、市盈率持仓计算

---

### 2. API 设计问题

#### 2.1 分析接口依赖本地数据
**问题:** 分析需要先有本地数据，但系统无法自动采集
```python
# 当前 - 需要手动导入数据
indicators = db.query(FinancialIndicator).filter(...)

# 建议 - 支持实时数据获取
if not indicators:
    indicators = await fetch_from_akshare(code)
```

#### 2.2 缺少港股支持
**问题:** 分析 API 不支持港股代码

**建议:**
- 添加港股代码解析 (0700.HK → 00700)
- 支持港股财务数据获取

---

### 3. 功能缺失

#### 3.1 紧急需要的功能
| 功能 | 优先级 | 说明 |
|------|--------|------|
| 持仓管理 | P0 | 添加/编辑/删除持仓 |
| 实时行情 | P0 | 当前价格获取 |
| 持仓分析 | P0 | 个股/组合分析 |
| 港股支持 | P0 | 港股数据获取 |
| 预警规则 | P1 | 自定义预警 |
| 数据同步 | P1 | 定时更新财务数据 |

#### 3.2 缺失的财务指标
- 自由现金流 (FCF)
- 股息率
- peg_ratio (PE/增长率)
- 营业周期
- 存货周转天数

---

### 4. 代码质量问题

#### 4.1 错误处理不足
```python
# 当前 - 静默失败
except Exception as e:
    logger.error(...)
    return None

# 建议 - 返回明确错误
except DataFetchError as e:
    raise HTTPException(status_code=503, detail=f"数据服务不可用: {e}")
```

#### 4.2 缺少数据验证
```python
# 建议 - 添加 Pydantic 验证
class StockCode(str):
    @classmethod
    def __validate__(cls, v):
        if not re.match(r'^\d{6}(\.(SH|SZ|HK))?$', v):
            raise ValueError("无效的股票代码")
        return v
```

#### 4.3 缺少缓存机制
**问题:** 频繁请求 AkShare 可能被限流

**建议:**
- 添加 Redis 缓存
- 本地缓存财务数据 24 小时

---

### 5. 前端改进建议

#### 5.1 持仓管理页面
```typescript
// 需要的页面
- /portfolio (持仓列表)
- /portfolio/add (添加持仓)
- /portfolio/:id/edit (编辑)
```

#### 5.2 组合分析功能
- 行业分布饼图
- 风险评估
- 建议调仓

#### 5.3 港股显示支持
- 汇率转换 (HKD → CNY)
- 港股代码显示 (0700.HK)

---

## 🎯 改进计划

### Phase 1: 紧急 (1-2周)
1. ✅ 港股代码支持
2. ✅ 持仓管理功能
3. ✅ 实时行情获取
4. ✅ 持仓分析报告

### Phase 2: 重要 (3-4周)
1. ⬜ 数据采集自动化
2. ⬜ 预警规则引擎
3. ⬜ 数据缓存
4. ⬜ 更多财务指标

### Phase 3: 完善 (5-8周)
1. ⬜ 美股支持
2. ⬜ 回测功能
3. ⬜ 组合优化
4. ⬜ 导出报告

---

## 📝 具体代码改动示例

### 1. 扩展股票代码支持
```python
# models.py
class Stock(Base):
    code = Column(String(20), unique=True, index=True)  # 扩展长度
    market_type = Column(String(10), default="A股")  # A股/港股/美股
    original_code = Column(String(20))  # 原始代码 0700.HK
```

### 2. 添加持仓分析
```python
# api/portfolio.py
@router.get("/analysis")
async def analyze_portfolio(portfolio_id: int):
    # 计算持仓市值
    # 计算盈亏
    # 行业分布
    # 风险指标
    return analysis_result
```

### 3. 港股数据获取
```python
# data_fetcher.py
def get_hk_stock_financial(code: str):
    """获取港股财务数据"""
    # 使用 akshare 或其他港股数据源
    pass
```

---

## ✅ 总结

当前系统基础框架良好，但需要以下改进:

1. **支持港股** - 用户 20% 持仓是港股
2. **持仓管理** - 核心功能缺失
3. **实时行情** - 需要当前价格
4. **数据采集** - 自动化财务数据获取

**建议优先级:** P0 = 港股支持 + 持仓管理
