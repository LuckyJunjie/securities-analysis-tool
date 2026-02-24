// API Service - Phase 2 Enhanced
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

// Stock types
export interface Stock {
  id: number;
  code: string;
  name: string;
  market?: string;
  market_type: string;
  industry?: string;
  sector?: string;
  status: string;
}

export interface Holding {
  id: number;
  stock_id: number;
  stock_code: string;
  stock_name: string;
  market_type: string;
  shares: number;
  avg_cost: number;
  avg_cost_cny: number;
  current_price?: number;
  current_price_cny?: number;
  market_value?: number;
  market_value_cny?: number;
  profit_loss?: number;
  profit_loss_pct?: number;
  price_change?: number;      // 今日涨跌额
  price_change_pct?: number;  // 今日涨跌幅
  purchase_date?: string;
  last_updated?: string;
}

export interface PortfolioSummary {
  total_holdings: number;
  total_market_value: number;
  total_market_value_cny: number;
  total_cost: number;
  total_profit_loss: number;
  total_profit_loss_pct: number;
  today_change: number;       // 今日盈亏
  today_change_pct: number;  // 今日涨跌幅
  holdings: Holding[];
  industry_distribution: Record<string, number>;
  market_distribution: Record<string, number>;
}

export interface Quote {
  code: string;
  name?: string;
  price?: number;
  change?: number;
  change_pct?: number;
  volume?: number;
  amount?: number;
  high?: number;
  low?: number;
  open?: number;
  timestamp?: string;
}

export interface FinancialIndicator {
  id: number;
  report_date?: string;
  report_type?: string;
  revenue?: number;
  net_profit?: number;
  roe?: number;
  pe?: number;
  pb?: number;
}

export interface Valuation {
  pe?: number;
  pb?: number;
  graham_number?: number;
  safety_margin?: number;
  rating: string;
}

export interface Growth {
  revenue_cagr?: number;
  profit_cagr?: number;
  trend: string;
}

export interface Analysis {
  code: string;
  name: string;
  valuation: Valuation;
  growth: Growth;
  health_score: number;
  recommendation: string;
}

export interface MacroIndicator {
  id: number;
  indicator_type: string;
  value?: number;
  unit?: string;
  yoy?: number;
  data_date?: string;
}

export interface Alert {
  id: number;
  stock_id?: number;
  alert_type?: string;
  message?: string;
  severity: string;
  value?: number;
  is_read: boolean;
  is_resolved: boolean;
  created_at?: string;
}

// API functions
export const stockApi = {
  getStocks: (params?: { market?: string; industry?: string; limit?: number }) =>
    api.get<Stock[]>('/stocks/', { params }),
  
  getStock: (code: string) =>
    api.get<Stock>(`/stocks/${code}`),
};

export const holdingApi = {
  getHoldings: () =>
    api.get<Holding[]>('/holdings/'),
  
  getSummary: () =>
    api.get<PortfolioSummary>('/holdings/summary'),
  
  refreshPrices: () =>
    api.post('/holdings/refresh'),
  
  create: (holding: any) =>
    api.post<Holding>('/holdings/', holding),
  
  update: (id: number, holding: any) =>
    api.patch<Holding>(`/holdings/${id}`, holding),
  
  delete: (id: number) =>
    api.delete(`/holdings/${id}`),
  
  importBatch: (holdings: any[]) =>
    api.post('/holdings/batch', holdings),
};

export const quoteApi = {
  getQuote: (code: string) =>
    api.get<Quote>(`/quotes/${code}`),
  
  getBatchQuotes: (codes: string[]) =>
    api.post<Record<string, Quote>>('/quotes/batch', codes),
};

export const analysisApi = {
  analyze: (code: string) =>
    api.get<Analysis>(`/analysis/${code}`),
  
  batchAnalyze: (codes: string[]) =>
    api.post<Analysis[]>('/analysis/batch', codes),
};

export const macroApi = {
  getIndicators: (params?: { indicator_type?: string; limit?: number }) =>
    api.get<MacroIndicator[]>('/macro/', { params }),
  
  getSummary: () =>
    api.get('/macro/summary'),
};

export const alertApi = {
  getAlerts: (params?: { severity?: string; is_read?: boolean }) =>
    api.get<Alert[]>('/alerts/', { params }),
  
  checkAlerts: (code: string) =>
    api.post(`/alerts/check/${code}`),
  
  markRead: (id: number) =>
    api.patch(`/alerts/${id}/read`),
};

export default api;
