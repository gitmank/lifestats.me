import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface MetricConfig {
  key: string;
  name: string;
  unit: string;
  default_goal: number;
  goal: number;
}

export interface GoalReached {
  [metricKey: string]: number;
}

export interface AggregatedPeriod {
  average_values: { [metricKey: string]: number };
  goalReached: GoalReached;
  daily_totals?: { [metricKey: string]: number[] };
}

export interface AggregatedMetrics {
  daily: AggregatedPeriod;
  weekly: AggregatedPeriod;
  monthly: AggregatedPeriod;
  quarterly: AggregatedPeriod;
  yearly: AggregatedPeriod;
}

export interface User {
  username: string;
  token: string;
}

export const apiClient = {
  // Authentication
  async signup(username: string): Promise<User> {
    const response = await api.post('/api/signup', { username });
    return response.data;
  },

  async getCurrentUser(): Promise<{ username: string }> {
    const response = await api.get('/api/me');
    return response.data;
  },

  // Metrics
  async getMetricsConfig(): Promise<MetricConfig[]> {
    const response = await api.get('/api/metrics/config');
    return response.data;
  },

  async getMetrics(): Promise<AggregatedMetrics> {
    const response = await api.get('/api/metrics');
    return response.data;
  },

  async addMetricEntry(metricKey: string, value: number, timestamp?: string) {
    const response = await api.post('/api/metrics', {
      metric_key: metricKey,
      value,
      timestamp,
    });
    return response.data;
  },

  // Goals
  async updateGoal(metricKey: string, targetValue: number) {
    const response = await api.post('/api/goals', {
      metric_key: metricKey,
      target_value: targetValue,
    });
    return response.data;
  },
};

export default apiClient; 