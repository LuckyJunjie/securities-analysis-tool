# 证券分析工具 - 第二次代码评审

**项目:** securities-analysis-tool  
**日期:** 2026-02-24  
**评审范围:** 后端 API + 前端

---

## 📊 当前架构

```
securities-analysis-tool/
├── src/backend/
│   ├── main.py              # FastAPI 入口
│   ├── models.py            # 数据库模型 (6张表)
│   ├── database.py          # 数据库连接
│   ├── data_fetcher.py      # AkShare 数据采集
│   ├── import_holdings.py   # 持仓导入脚本
│   ├── data/holdings_data.py  # 持仓数据
│   └── api/
│       ├── stocks.py        # 股票 CRUD
│       ├── holdings.py      # 持仓管理
│       ├── analysis.py     # 分析接口
│       ├── macro.py        # 宏观数据
│       └── alerts.py        # 预警系统
└── src/frontend/
    └── src/
        ├── pages/           # 6个页面
        └── services/api.ts  # API 客户端
```

---

## 🔴 严重问题

### 1. 分析 API 依赖本地数据
```python
# 问题: 没有本地数据时直接报错
indicators = db.query(FinancialIndicator).filter(...)
if not indicators:
    raise HTTPException(status_code=404, detail="暂无财务数据")
```

**建议:** 支持从 AkShare 实时获取数据
```python
async def analyze_stock(code: str, db: Session):
    # 先查本地
    indicators = db.query(...).all()
    
    # 本地没有则从线上获取
    if not indicators:
        indicators = await fetch_from_akshare(code)
        # 存入本地缓存
        save_to_local(indicators)
```

### 2. 缺少错误处理
```python
# 问题: 静默失败
except Exception as e:
    logger.error(...)  # 只记录日志
    return None       # 返回 None 导致前端崩溃
```

**建议:** 返回明确的错误信息
```python
except DataNotFoundError:
    raise HTTPException(status_code=404, detail="数据不存在")
except ExternalServiceError:
    raise HTTPException(status_code=503, detail="外部服务不可用")
```

### 3. 前端缺少加载状态
```typescript
// 问题: 请求失败时没有错误提示
const res = await holdingApi.getSummary();
setSummary(res.data);  // 如果失败会崩溃
```

**建议:**
```typescript
try {
  const res = await holdingApi.getSummary();
  setSummary(res.data);
} catch (error) {
  setError('加载失败: ' + error.message);
}
```

---

## 🟡 功能缺失

### 高优先级

| 功能 | 问题 | 建议 |
|------|------|------|
| **实时行情** | 当前价格固定 | 集成实时价格 API |
| **持仓分析报告** | 无 | 添加持仓健康度分析 |
| **港股数据** | 无财务数据 | 支持港股 AkShare |
| **数据同步** | 手动导入 | 定时任务自动更新 |

### 中优先级

| 功能 | 问题 | 建议 |
|------|------|------|
| **财务指标图表** | 纯数字 | 添加历史趋势图 |
| **排序筛选** | 无 | 添加排序/筛选功能 |
| **导出功能** | 无 | 导出 Excel/PDF |
| **搜索功能** | 简单 | 支持模糊搜索 |

---

## 🟢 代码质量问题

### 1. 硬编码
```python
# 问题
HKD_TO_CNY = 0.85  # 写死汇率

# 建议: 从 API 获取
HKD_TO_CNY = await fetch_exchange_rate("HKD/CNY")
```

### 2. 重复代码
```python
# holdings.py 和 analysis.py 都有计算逻辑
# 建议: 提取为工具函数
def calculate_profit_loss(holding): ...
def calculate_market_value(holding): ...
```

### 3. 缺少验证
```python
# 问题: 直接使用用户输入
stock_code: str  # 任何字符串都可以

# 建议: 添加 Pydantic 验证
class StockCode(str):
    @classmethod
    def __validate__(cls, v):
        if not re.match(r'^\d{5}(\.(HK|SH|SZ|US))?$', v):
            raise ValueError("无效股票代码")
```

---

## 📝 改进计划

### Phase 2 (本周)
1. ⬜ 实时行情获取 (免费 API)
2. ⬜ 持仓分析报告增强
3. ⬜ 错误处理完善
4. ⬜ 加载状态优化

### Phase 3 (下周)
1. ⬜ 财务数据自动同步
2. ⬜ 港股财务数据支持
3. ⬜ 导出功能
4. ⬜ 图表可视化

### Phase 4 (后续)
1. ⬜ 美股支持
2. ⬜ 回测功能
3. ⬜ 组合优化
4. ⬜ 移动端适配

---

## ✅ 已有优点

1. **架构清晰** - 模块化设计，易于扩展
2. **类型完整** - Pydantic 模型完整
3. **港股支持** - 市场类型字段已添加
4. **持仓管理** - CRUD 功能完整
5. **前端美观** - UI 设计合理

---

## 🎯 立即行动项

1. **添加实时行情 API**
   - 免费方案: Tushare (需要 token) 或 新浪/腾讯接口
   
2. **完善错误处理**
   - 所有 API 添加 try-catch
   - 返回友好错误信息

3. **前端加载状态**
   - 添加 loading/spinner
   - 添加 error 提示

4. **数据自动同步**
   - 使用 APScheduler 定时任务
   - 每天凌晨更新财务数据
