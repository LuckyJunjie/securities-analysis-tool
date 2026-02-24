import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { alertApi, macroApi } from '../services/api';

interface DashboardStats {
  totalStocks: number;
  avgHealthScore: number;
  activeAlerts: number;
  recommendations: string[];
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalStocks: 0,
    avgHealthScore: 0,
    activeAlerts: 0,
    recommendations: [],
  });
  const [loading, setLoading] = useState(true);
  const [macroSummary, setMacroSummary] = useState<any>({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load alerts
      const alertsRes = await alertApi.getAlerts();
      const alerts = alertsRes.data.filter(a => !a.is_resolved);
      
      // Load macro summary
      try {
        const macroRes = await macroApi.getSummary();
        setMacroSummary(macroRes.data);
      } catch (e) {
        console.log('Macro data not available');
      }

      setStats({
        totalStocks: 0, // Will update when stocks loaded
        avgHealthScore: 65,
        activeAlerts: alerts.length,
        recommendations: ['关注低估优质股', '监控业绩预警'],
      });
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>📊 仪表盘</h1>
      
      {/* Stats Grid */}
      <div className="grid grid-4">
        <div className="card">
          <div className="stat">
            <div className="stat-value">{stats.totalStocks}</div>
            <div className="stat-label">关注股票</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value">{stats.avgHealthScore}</div>
            <div className="stat-label">平均健康分</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value" style={{ color: stats.activeAlerts > 0 ? '#f44336' : '#4caf50' }}>
              {stats.activeAlerts}
            </div>
            <div className="stat-label">活跃预警</div>
          </div>
        </div>
        
        <div className="card">
          <div className="stat">
            <div className="stat-value">{stats.recommendations.length}</div>
            <div className="stat-label">投资建议</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-title">⚡ 快速操作</div>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/stocks" className="btn btn-primary">查看股票</Link>
          <Link to="/alerts" className="btn btn-warning">查看预警</Link>
          <Link to="/macro" className="btn btn-primary">宏观数据</Link>
        </div>
      </div>

      {/* Recommendations */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-title">💡 投资建议</div>
        <ul style={{ paddingLeft: '1.5rem', lineHeight: 2 }}>
          {stats.recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ul>
      </div>

      {/* Macro Summary */}
      {Object.keys(macroSummary).length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="card-title">🌐 宏观概览</div>
          <div className="grid grid-4">
            {macroSummary.gdp && (
              <div className="stat">
                <div className="stat-value">{macroSummary.gdp.value?.toFixed(1)}</div>
                <div className="stat-label">GDP同比 (%)</div>
              </div>
            )}
            {macroSummary.ppi && (
              <div className="stat">
                <div className="stat-value">{macroSummary.ppi.value?.toFixed(1)}</div>
                <div className="stat-label">PPI (%)</div>
              </div>
            )}
            {macroSummary.cpi && (
              <div className="stat">
                <div className="stat-value">{macroSummary.cpi.value?.toFixed(1)}</div>
                <div className="stat-label">CPI (%)</div>
              </div>
            )}
            {macroSummary.electricity && (
              <div className="stat">
                <div className="stat-value">{macroSummary.electricity.value?.toFixed(1)}</div>
                <div className="stat-label">发电量 (%)</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
