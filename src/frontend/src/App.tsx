import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import StockList from './pages/StockList';
import StockDetail from './pages/StockDetail';
import Portfolio from './pages/Portfolio';
import Macro from './pages/Macro';
import Alerts from './pages/Alerts';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">📈 证券分析工具</div>
          <div className="nav-links">
            <Link to="/">仪表盘</Link>
            <Link to="/portfolio">持仓</Link>
            <Link to="/stocks">股票</Link>
            <Link to="/macro">宏观</Link>
            <Link to="/alerts">预警</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/stocks" element={<StockList />} />
            <Route path="/stocks/:code" element={<StockDetail />} />
            <Route path="/macro" element={<Macro />} />
            <Route path="/alerts" element={<Alerts />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
