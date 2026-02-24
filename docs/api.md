# API接口文档

**版本:** 1.0  
**日期:** 2026-02-24

---

## 认证

### POST /api/auth/register
注册新用户

**请求体:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

### POST /api/auth/login
用户登录

**请求体:**
```json
{
  "email": "string",
  "password": "string"
}
```

**响应:**
```json
{
  "token": "jwt_token",
  "user": {
    "id": 1,
    "username": "string"
  }
}
```

---

## 股票

### GET /api/stocks
获取股票列表

**查询参数:**
- `industry` (optional): 行业筛选
- `page`: 页码
- `page_size`: 每页数量

**响应:**
```json
{
  "items": [
    {
      "code": "600519.SH",
      "name": "贵州茅台",
      "industry": "白酒",
      "current_price": 1485.3
    }
  ],
  "total": 5000,
  "page": 1
}
```

### GET /api/stocks/{code}
获取股票基本信息

**响应:**
```json
{
  "code": "600519.SH",
  "name": "贵州茅台",
  "industry": "白酒",
  "sector": "消费",
  "listed_date": "2001-08-27",
  "market_cap": 1860000000000
}
```

### GET /api/stocks/{code}/financials
获取财务数据 (十年)

**查询参数:**
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应:**
```json
{
  "code": "600519.SH",
  "indicators": [
    {
      "report_date": "2025-12-31",
      "revenue": 120000000000,
      "net_profit": 60000000000,
      "gross_margin": 0.52,
      "net_margin": 0.50,
      "roe": 0.30,
      "revenue_yoy": 0.15,
      "profit_yoy": 0.18
    }
  ]
}
```

---

## 分析

### GET /api/analysis/{code}
综合分析报告

**响应:**
```json
{
  "code": "600519.SH",
  "name": "贵州茅台",
  "summary": {
    "grade": "A",
    "safety_margin": 0.35,
    "risk_level": "低"
  },
  "financial": {
    "revenue_trend": "上升",
    "profit_trend": "上升",
    "roe_avg_10y": 0.28
  },
  "valuation": {
    "pe": 25,
    "pb": 8,
    "intrinsic_value": 2000,
    "safety_margin": 0.35,
    "recommendation": "买入"
  },
  "alerts": [
    {
      "type": "财务",
      "severity": "低",
      "message": "毛利率保持稳定"
    }
  ]
}
```

### GET /api/valuation/{code}
估值分析

**响应:**
```json
{
  "code": "600519.SH",
  "current_price": 1485.3,
  "graham_value": 1800,
  "dcf_value": 1650,
  "safety_margin": 0.21,
  "grade": "B",
  "analysis": "估值合理，安全边际适中"
}
```

### GET /api/trend/{code}
趋势分析

**响应:**
```json
{
  "code": "600519.SH",
  "revenue_trend": "上升",
  "profit_trend": "上升",
  "margins_trend": "平稳",
  "拐点": []
}
```

---

## 预警

### GET /api/alerts
获取预警列表

**查询参数:**
- `stock_code` (optional): 股票筛选
- `severity` (optional): 严重程度
- `is_read` (optional): 已读/未读

**响应:**
```json
{
  "items": [
    {
      "id": 1,
      "stock_code": "601888.SH",
      "stock_name": "中国中免",
      "rule_name": "营收双降",
      "severity": "高",
      "message": "营收同比连续两季下降",
      "alert_time": "2026-01-15T10:00:00Z",
      "is_read": false
    }
  ],
  "total": 10
}
```

### POST /api/alerts/rules
创建预警规则

**请求体:**
```json
{
  "rule_name": "营收下降预警",
  "rule_type": "财务",
  "condition": "revenue_yoy < 0 AND revenue_yoy_lag < 0",
  "severity": "高"
}
```

**响应:**
```json
{
  "id": 1,
  "rule_name": "营收下降预警",
  "status": "active"
}
```

### PUT /api/alerts/{id}/read
标记已读

**响应:**
```json
{
  "success": true
}
```

---

## 宏观数据

### GET /api/macro/indicators
宏观指标列表

**查询参数:**
- `indicator`: 指标 (electricity/ppi/cpi/rate)
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应:**
```json
{
  "indicator": "ppi",
  "data": [
    {
      "date": "2026-01-31",
      "value": -0.5,
      "yoy": -2.1
    }
  ]
}
```

---

## 持仓管理

### GET /api/holdings
持仓列表

**响应:**
```json
{
  "items": [
    {
      "code": "600519.SH",
      "name": "贵州茅台",
      "shares": 100,
      "avg_cost": 1200,
      "current_price": 1485.3,
      "profit": 28530,
      "profit_pct": 0.238
    }
  ]
}
```

### POST /api/holdings
添加持仓

**请求体:**
```json
{
  "code": "600519.SH",
  "shares": 100,
  "cost": 120000
}
```

---

## 错误响应

所有API错误返回统一格式:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "股票代码不存在"
  }
}
```

**常见错误码:**
- `400` - 请求参数错误
- `401` - 未授权
- `404` - 资源不存在
- `500` - 服务器错误
