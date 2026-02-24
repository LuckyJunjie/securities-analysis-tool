import { useState, useEffect } from 'react';
import { alertApi, type Alert } from '../services/api';

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'resolved'>('all');

  useEffect(() => {
    loadAlerts();
  }, [filter]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filter === 'unread') params.is_read = false;
      if (filter === 'resolved') params.is_resolved = true;
      
      const res = await alertApi.getAlerts(params);
      setAlerts(res.data);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await alertApi.markRead(id);
      loadAlerts();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'red': return 'alert-red';
      case 'yellow': return 'alert-yellow';
      case 'green': return 'alert-green';
      default: return '';
    }
  };

  if (loading) {
    return <div className="loading">加载预警...</div>;
  }

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>⚠️ 预警中心</h1>

      {/* Filters */}
      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <button
            className={`btn ${filter === 'all' ? 'btn-primary' : ''}`}
            onClick={() => setFilter('all')}
          >
            全部
          </button>
          <button
            className={`btn ${filter === 'unread' ? 'btn-primary' : ''}`}
            onClick={() => setFilter('unread')}
          >
            未读
          </button>
          <button
            className={`btn ${filter === 'resolved' ? 'btn-primary' : ''}`}
            onClick={() => setFilter('resolved')}
          >
            已解决
          </button>
        </div>

        {/* Alert Stats */}
        <div className="grid grid-3">
          <div className="stat">
            <div className="stat-value" style={{ color: '#f44336' }}>
              {alerts.filter(a => a.severity === 'red').length}
            </div>
            <div className="stat-label">红色预警</div>
          </div>
          <div className="stat">
            <div className="stat-value" style={{ color: '#ff9800' }}>
              {alerts.filter(a => a.severity === 'yellow').length}
            </div>
            <div className="stat-label">黄色预警</div>
          </div>
          <div className="stat">
            <div className="stat-value" style={{ color: '#4caf50' }}>
              {alerts.filter(a => a.is_resolved).length}
            </div>
            <div className="stat-label">已解决</div>
          </div>
        </div>
      </div>

      {/* Alert List */}
      {alerts.length === 0 ? (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
            ✅ 暂无预警
          </div>
        </div>
      ) : (
        <div style={{ marginTop: '1.5rem' }}>
          {alerts.map((alert) => (
            <div key={alert.id} className={`card alert-item ${getSeverityClass(alert.severity)}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <div style={{ fontWeight: 'bold' }}>{alert.alert_type}</div>
                  <div style={{ marginTop: '0.5rem' }}>{alert.message}</div>
                  <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.5rem' }}>
                    当前值: {alert.value?.toFixed(2)}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#999', marginTop: '0.25rem' }}>
                    {alert.created_at?.split('T')[0] || ''}
                  </div>
                </div>
                {!alert.is_read && (
                  <button
                    className="btn"
                    onClick={() => handleMarkRead(alert.id)}
                    style={{ fontSize: '0.75rem' }}
                  >
                    标记已读
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
