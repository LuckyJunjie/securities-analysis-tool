# 证券分析工具 (Securities Analysis Tool)

基于价值投资理念的量化证券分析系统

[![GitHub stars](https://img.shields.io/github/stars/LuckyJunjie/securities-analysis-tool)](https://github.com/LuckyJunjie/securities-analysis-tool/stargazers)
[![License](https://img.shields.io/github/license/LuckyJunjie/securities-analysis-tool)](https://github.com/LuckyJunjie/securities-analysis-tool)

---

## 核心理念

整合三大投资哲学，构建可量化、可验证的证券分析系统：

- 🔵 **本杰明·格雷厄姆** - 安全边际、价值投资
- 🟢 **菲利普·费雪** - 成长股洞察、管理层评估  
- 🔴 **肖星** - 财报三张表分析框架

---

## 功能特性

### 📊 财务分析
- 十年财务指标数据库
- 成长性趋势分析 (CAGR)
- 盈利能力评估 (ROE、毛利率、净利率)
- 运营效率分析 (周转率)
- 财务健康度检测

### 📈 估值分析
- PE/PB/DC估值
- 安全边际计算
- 期望 vs 实际增长偏离检测
- 戴维斯双杀预警
- 格雷厄姆评级 (A/B/C)

### 🌐 宏观监控
- 发电量、PPI、CPI监控
- 利率政策追踪
- 消费信心指数
- 宏观预警信号

### ⚠️ 预警系统
- 业绩双降预警
- 成长逻辑破坏检测
- 宏观环境预警
- 组合信号评估

### 💼 持仓管理
- 持股数据库
- 季度自动更新
- 一键分析报告
- 行动指引建议

---

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/LuckyJunjie/securities-analysis-tool.git
cd securities-analysis-tool

# 安装依赖 (后端)
cd src/backend
pip install -r requirements.txt

# 安装依赖 (前端)
cd ../frontend
npm install
```

### 运行

```bash
# 启动后端
cd src/backend
python main.py

# 启动前端
cd src/frontend
npm run dev
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React + TypeScript + ECharts |
| 后端 | Python FastAPI |
| 数据库 | PostgreSQL / SQLite |
| 数据源 | AkShare (免费开源) |

---

## 项目结构

```
securities-analysis-tool/
├── docs/           # 项目文档
│   └── GDD.md      # 需求规格文档
├── src/            # 源代码
│   ├── backend/    # Python后端
│   └── frontend/  # React前端
├── tests/          # 测试
├── data/           # 数据文件
└── docker/         # Docker配置
```

---

## 文档

- [需求文档 (GDD)](docs/GDD.md)
- [API文档](docs/api.md) (规划中)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 许可证

MIT License
