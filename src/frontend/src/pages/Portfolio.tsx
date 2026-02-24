import { useState, useEffect } from 'react';
import { holdingApi, type Holding, type PortfolioSummary } from '../services/api';

export default function Portfolio() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await holdingApi.getSummary();
      setSummary(res.data);
      setHoldings(res.data.holdings);
    } catch (error) {
      console.error('Failed to load portfolio:', error);
    } finally {
      setLoading(false);
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
    return <div className="loading">加载持仓数据...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>💼 我的持仓</h1>

      {/* Summary Cards */}
      <div className="grid grid-4">
        <div className="card">
          <div className="stat">
            <div className="stat-value">{summary?.total_holdings || 0}</div>
            <div className="stat-label">持仓股票</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value">{formatMoney(summary?.total_market_value_cny)}</div>
            <div className="stat-label">总市值 (CNY)</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value" style={{ color: (summary?.total_profit_loss || 0) >= 0 ? '#4caf50' : '#f44336' }}>
              {formatMoney(summary?.total_profit_loss)}
            </div>
            <div className="stat-label">盈亏金额</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value" style={{ color: (summary?.total_profit_loss_pct || 0) >= 0 ? '#4caf50' : '#f44336' }}>
              {formatPct(summary?.total_profit_loss_pct)}
            </div>
            <div className="stat-label">盈亏比例</div>
          </div>
        </div>
      </div>

      {/* Distribution */}
      <div className="grid grid-2" style={{ marginTop: '1.5rem' }}>
        {/* Industry Distribution */}
        <div className="card">
          <div className="card-title">📊 行业分布</div>
          {summary?.industry_distribution && Object.keys(summary.industry_distribution).length > 0 ? (
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

        {/* Market Distribution */}
        <div className="card">
          <div className="card-title">🌏 市场分布</div>
          {summary?.market_distribution && Object.keys(summary.market_distribution).length > 0 ? (
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
