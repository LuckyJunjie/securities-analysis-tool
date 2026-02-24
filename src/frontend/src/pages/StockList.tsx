import { useState } from 'react';
import { Link } from 'react-router-dom';
import { stockApi, type Stock } from '../services/api';

export default function StockList() {
  const [searchCode, setSearchCode] = useState('');
  const [stock, setStock] = useState<Stock | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchCode.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await stockApi.getStock(searchCode);
      setStock(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '股票不存在');
      setStock(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: '1.5rem' }}>📈 股票查询</h1>
      
      {/* Search */}
      <div className="card">
        <form onSubmit={handleSearch} className="search-bar">
          <input
            type="text"
            className="form-input"
            placeholder="输入股票代码 (如: 000001)"
            value={searchCode}
            onChange={(e) => setSearchCode(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '查询中...' : '查询'}
          </button>
        </form>
        
        {error && <div className="error">{error}</div>}
        
        {stock && (
          <div style={{ marginTop: '1rem' }}>
            <table className="table">
              <tbody>
                <tr>
                  <th>代码</th>
                  <td>{stock.code}</td>
                </tr>
                <tr>
                  <th>名称</th>
                  <td>{stock.name}</td>
                </tr>
                <tr>
                  <th>市场</th>
                  <td>{stock.market || '-'}</td>
                </tr>
                <tr>
                  <th>行业</th>
                  <td>{stock.industry || '-'}</td>
                </tr>
                <tr>
                  <th>状态</th>
                  <td>{stock.status}</td>
                </tr>
              </tbody>
            </table>
            <Link to={`/stocks/${stock.code}`} className="btn btn-primary" style={{ marginTop: '1rem' }}>
              查看详细分析
            </Link>
          </div>
        )}
      </div>

      {/* Sample Stocks */}
      <div className="card" style={{ marginTop: '1.5rem' }}>
        <div className="card-title">📋 常用股票代码</div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['000001', '600519', '000858', '601318', '000333'].map(code => (
            <button
              key={code}
              className="btn btn-primary"
              onClick={() => setSearchCode(code)}
            >
              {code}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
