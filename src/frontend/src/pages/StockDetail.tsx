import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { analysisApi, alertApi, type Analysis } from '../services/api';

export default function StockDetail() {
  const { code } = useParams<{ code: string }>();
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (code) {
      loadAnalysis(code);
    }
  }, [code]);

  const loadAnalysis = async (stockCode: string) => {
    setLoading(true);
    setError('');
    
    try {
      const [analysisRes, alertsRes] = await Promise.all([
        analysisApi.analyze(stockCode),
        alertApi.checkAlerts(stockCode).catch(() => ({ data: { alerts: [] } })),
      ]);
      
      setAnalysis(analysisRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败，请确保后端服务运行中');
    } finally {
      setLoading(false);
    }
  };

  const getScoreClass = (score: number) => {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
  };

  const getRatingClass = (rating: string) => {
    return `rating rating-${rating.toLowerCase()}`;
  };

  if (loading) {
    return <div className="loading">分析中...</div>;
  }

  if (error) {
    return (
      <div>
        <Link to="/stocks" className="btn" style={{ marginBottom: '1rem' }}>← 返回</Link>
        <div className="error">{error}</div>
        <p style={{ marginTop: '1rem', color: '#666' }}>
          请确保后端服务已启动: <code>cd src/backend && uvicorn main:app --reload</code>
        </p>
      </div>
    );
  }

  if (!analysis) {
    return <div className="error">未找到数据</div>;
  }

  return (
    <div>
      <Link to="/stocks" className="btn" style={{ marginBottom: '1rem' }}>← 返回股票列表</Link>
      
      <h1 style={{ marginBottom: '0.5rem' }}>{analysis.name} ({analysis.code})</h1>
      <p style={{ color: '#666', marginBottom: '1.5rem' }}>价值投资分析报告</p>

      {/* Health Score */}
      <div className="card">
        <div className="card-title">🎯 健康评分</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span className={`score ${getScoreClass(analysis.health_score)}`}>
            {analysis.health_score}
          </span>
          <div>
            <div style={{ fontWeight: 'bold', fontSize: '1.25rem' }}>{analysis.recommendation}</div>
            <div style={{ color: '#666' }}>综合评估</div>
          </div>
        </div>
      </div>

      {/* Valuation */}
      <div className="grid grid-2" style={{ marginTop: '1.5rem' }}>
        <div className="card">
          <div className="card-title">💰 估值分析</div>
          <table className="table">
            <tbody>
              <tr>
                <th>市盈率 (PE)</th>
                <td>{analysis.valuation.pe?.toFixed(2) || '-'}</td>
              </tr>
              <tr>
                <th>市净率 (PB)</th>
                <td>{analysis.valuation.pb?.toFixed(2) || '-'}</td>
              </tr>
              <tr>
                <th>格雷厄姆数字</th>
                <td>{analysis.valuation.graham_number?.toFixed(2) || '-'}</td>
              </tr>
              <tr>
                <th>安全边际</th>
                <td style={{ color: analysis.valuation.safety_margin && analysis.valuation.safety_margin > 0 ? '#4caf50' : '#f44336' }}>
                  {analysis.valuation.safety_margin?.toFixed(2) || '-'}%
                </td>
              </tr>
              <tr>
                <th>格雷厄姆评级</th>
                <td><span className={getRatingClass(analysis.valuation.rating)}>{analysis.valuation.rating}</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="card-title">📈 成长性分析</div>
          <table className="table">
            <tbody>
              <tr>
                <th>营收CAGR (4年)</th>
                <td style={{ color: analysis.growth.revenue_cagr && analysis.growth.revenue_cagr > 0 ? '#4caf50' : '#f44336' }}>
                  {analysis.growth.revenue_cagr?.toFixed(2) || '-'}%
                </td>
              </tr>
              <tr>
                <th>净利CAGR (4年)</th>
                <td style={{ color: analysis.growth.profit_cagr && analysis.growth.profit_cagr > 0 ? '#4caf50' : '#f44336' }}>
                  {analysis.growth.profit_cagr?.toFixed(2) || '-'}%
                </td>
              </tr>
              <tr>
                <th>趋势判断</th>
                <td>{analysis.growth.trend}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div className="card-title">⚠️ 预警信号</div>
          {alerts.map((alert, i) => (
            <div key={i} className={`alert-item alert-${alert.severity}`}>
              <strong>{alert.message}</strong>
              <div style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                阈值: {alert.threshold} | 当前: {alert.value?.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Investment Advice */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-title">💡 投资建议</div>
        <div style={{ padding: '1rem', background: '#f5f5f5', borderRadius: '4px' }}>
          {analysis.health_score >= 80 && analysis.valuation.rating === 'A' && (
            <p>✅ 该股票具有较高的投资价值，建议重点关注。注意分散投资风险。</p>
          )}
          {analysis.health_score >= 60 && analysis.health_score < 80 && (
            <p>⚠️ 该股票具有一定的投资价值，但需关注风险因素。建议进一步研究。</p>
          )}
          {analysis.health_score < 60 && (
            <p>❌ 该股票风险较高，建议谨慎考虑或选择其他标的。</p>
          )}
        </div>
      </div>
    </div>
  );
}
