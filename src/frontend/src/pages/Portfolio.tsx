import { useState, useEffect } from 'react';
import { holdingApi, type PortfolioSummary } from '../services/api';

export default function Portfolio() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await holdingApi.getSummary();
      setSummary(res.data);
    } catch (err: any) {
      console.error('Failed to load portfolio:', err);
      setError(err.response?.data?.detail || '加载持仓数据失败，请检查后端服务是否运行');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await holdingApi.refreshPrices();
      await loadData();
    } catch (err: any) {
      console.error('Failed to refresh:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const getProfitLossClass = (value?: number) => {
    if (!value) return '';
    if (value > 0) return 'profit-positive';
    if (value < 0) return 'profit-negative';
    return '';
  };

  const formatMoney = (value?: number) => {
    if (value === undefined || value === null) return '-';
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPct = (value?: number) => {
    if (value === undefined || value === null) return '-';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载持仓数据...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={loadData}>
          重试
        </button>
        <p className="hint">
          启动后端: <code>cd src/backend && uvicorn main:app --reload</code>
        </p>
      </div>
    );
  }

  if (!summary || summary.holdings.length === 0) {
    return (
      <div className="empty-container">
        <div className="empty-icon">📊</div>
        <h3>暂无持仓数据</h3>
        <p>请先添加持仓或导入数据</p>
      </div>
    );
  }

  const holdings = summary.holdings;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h1>💼 我的持仓</h1>
        <button 
          className="btn btn-primary" 
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? '刷新中...' : '🔄 刷新价格'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-4">
        <div className="card">
          <div className="stat">
            <div className="stat-value">{summary.total_holdings}</div>
            <div className="stat-label">持仓股票</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value">{formatMoney(summary.total_market_value_cny)}</div>
            <div className="stat-label">总市值 (CNY)</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value" style={{ color: summary.total_profit_loss >= 0 ? '#4caf50' : '#f44336' }}>
              {formatMoney(summary.total_profit_loss)}
            </div>
            <div className="stat-label">总盈亏</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value" style={{ color: summary.today_change >= 0 ? '#4caf50' : '#f44336' }}>
              {formatMoney(summary.today_change)}
            </div>
            <div className="stat-label">今日涨跌 {formatPct(summary.today_change_pct)}</div>
          </div>
        </div>
      </div>

      {/* Distribution */}
      <div className="grid grid-2" style={{ marginTop: '1.5rem' }}>
        <div className="card">
          <div className="card-title">📊 行业分布</div>
          {summary.industry_distribution && Object.keys(summary.industry_distribution).length > 0 ? (
            <div className="distribution-list">
              {Object.entries(summary.industry_distribution).map(([industry, pct]) => (
                <div key={industry} className="distribution-item">
                  <span className="distribution-label">{industry}</span>
                  <div className="distribution-bar-container">
                    <div className="distribution-bar" style={{ width: `${pct}%` }}></div>
                  </div>
                  <span className="distribution-value">{pct}%</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">暂无数据</p>
          )}
        </div>

        <div className="card">
          <div className="card-title">🌏 市场分布</div>
          {summary.market_distribution && Object.keys(summary.market_distribution).length > 0 ? (
            <div className="distribution-list">
              {Object.entries(summary.market_distribution).map(([market, pct]) => (
                <div key={market} className="distribution-item">
                  <span className="distribution-label">{market}</span>
                  <div className="distribution-bar-container">
                    <div className="distribution-bar" style={{ width: `${pct}%` }}></div>
                  </div>
                  <span className="distribution-value">{pct}%</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">暂无数据</p>
          )}
        </div>
      </div>

      {/* Holdings Table */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-title">📋 持仓明细</div>
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>市场</th>
                <th>股数</th>
                <th>成本</th>
                <th>现价</th>
                <th>涨跌</th>
                <th>市值</th>
                <th>盈亏</th>
                <th>盈亏%</th>
              </tr>
            </thead>
            <tbody>
              {holdings.map((h, i) => (
                <tr key={i}>
                  <td>{h.stock_code}</td>
                  <td>{h.stock_name}</td>
                  <td>
                    <span className={`badge ${h.market_type === '港股' ? 'badge-hk' : 'badge-a'}`}>
                      {h.market_type}
                    </span>
                  </td>
                  <td>{h.shares.toLocaleString()}</td>
                  <td>{formatMoney(h.avg_cost)}</td>
                  <td>{formatMoney(h.current_price)}</td>
                  <td className={getProfitLossClass(h.price_change_pct)}>
                    {formatPct(h.price_change_pct)}
                  </td>
                  <td>{formatMoney(h.market_value)}</td>
                  <td className={getProfitLossClass(h.profit_loss)}>
                    {formatMoney(h.profit_loss)}
                  </td>
                  <td className={getProfitLossClass(h.profit_loss_pct)}>
                    {formatPct(h.profit_loss_pct)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
