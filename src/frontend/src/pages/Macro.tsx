import { useState, useEffect } from 'react';
import { macroApi, type MacroIndicator } from '../services/api';

export default function Macro() {
  const [indicators, setIndicators] = useState<MacroIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<any>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [indRes, sumRes] = await Promise.all([
        macroApi.getIndicators({ limit: 24 }),
        macroApi.getSummary(),
      ]);
      setIndicators(indRes.data);
      setSummary(sumRes.data);
    } catch (error) {
      console.error('Failed to load macro data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">加载宏观数据...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>🌐 宏观数据</h1>

      {/* Summary Cards */}
      <div className="grid grid-4">
        {summary.gdp && (
          <div className="card">
            <div className="stat">
              <div className="stat-value">{summary.gdp.value?.toFixed(1)}%</div>
              <div className="stat-label">GDP 同比</div>
              <div style={{ color: summary.gdp.yoy && summary.gdp.yoy > 0 ? '#4caf50' : '#f44336' }}>
                {summary.gdp.yoy?.toFixed(1)}%
              </div>
            </div>
          </div>
        )}
        
        {summary.ppi && (
          <div className="card">
            <div className="stat">
              <div className="stat-value">{summary.ppi.value?.toFixed(1)}%</div>
              <div className="stat-label">PPI 同比</div>
              <div style={{ color: summary.ppi.yoy && summary.ppi.yoy > 0 ? '#4caf50' : '#f44336' }}>
                {summary.ppi.yoy?.toFixed(1)}%
              </div>
            </div>
          </div>
        )}
        
        {summary.cpi && (
          <div className="card">
            <div className="stat">
              <div className="stat-value">{summary.cpi.value?.toFixed(1)}%</div>
              <div className="stat-label">CPI 同比</div>
              <div style={{ color: summary.cpi.yoy && summary.cpi.yoy > 0 ? '#4caf50' : '#f44336' }}>
                {summary.cpi.yoy?.toFixed(1)}%
              </div>
            </div>
          </div>
        )}
        
        {summary.electricity && (
          <div className="card">
            <div className="stat">
              <div className="stat-value">{summary.electricity.value?.toFixed(1)}%</div>
              <div className="stat-label">发电量同比</div>
              <div style={{ color: summary.electricity.yoy && summary.electricity.yoy > 0 ? '#4caf50' : '#f44336' }}>
                {summary.electricity.yoy?.toFixed(1)}%
              </div>
            </div>
          </div>
        )}
      </div>

      {/* No Data Message */}
      {Object.keys(summary).length === 0 && (
        <div className="card">
          <div className="error">暂无宏观数据</div>
          <p style={{ marginTop: '1rem', color: '#666' }}>
            请确保后端服务运行中，并已配置 AkShare 数据源。
          </p>
          <p style={{ color: '#666' }}>
            启动命令: <code>cd src/backend && uvicorn main:app --reload</code>
          </p>
        </div>
      )}

      {/* Historical Data */}
      {indicators.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="card-title">📊 历史数据</div>
          <table className="table">
            <thead>
              <tr>
                <th>指标类型</th>
                <th>数值</th>
                <th>单位</th>
                <th>同比</th>
                <th>日期</th>
              </tr>
            </thead>
            <tbody>
              {indicators.slice(0, 20).map((ind, i) => (
                <tr key={i}>
                  <td>{ind.indicator_type}</td>
                  <td>{ind.value?.toFixed(2) || '-'}</td>
                  <td>{ind.unit || '-'}</td>
                  <td style={{ color: ind.yoy && ind.yoy > 0 ? '#4caf50' : '#f44336' }}>
                    {ind.yoy?.toFixed(2) || '-'}%
                  </td>
                  <td>{ind.data_date?.split('T')[0] || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
