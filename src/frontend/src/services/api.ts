// API Service
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
  industry?: string;
  status: string;
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
