import axios from 'axios';

// Use local Next.js API routes instead of external backend
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:3000';

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

// Add response interceptor to handle errors properly
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail) {
      // Extract the error message from the backend response
      const message = error.response.data.detail;
      throw new Error(message);
    }
    // Fallback for other error types
    throw new Error(error.message || 'An error occurred');
  }
);

export interface MetricConfig {
  key: string;
  name: string;
  unit: string;
  type: string; // "min" or "max"
  default_goal?: number;
  goal?: number;
  is_active?: boolean;
}

export interface UserMetricsConfig {
  id: number;
  user_id: number;
  metric_key: string;
  metric_name: string;
  unit: string;
  type: string;
  goal?: number;
  default_goal?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserMetricsConfigCreate {
  metric_key: string;
  metric_name: string;
  unit: string;
  type: string;
  goal?: number;
  default_goal?: number;
  is_active?: boolean;
}

export interface UserMetricsConfigUpdate {
  metric_name?: string;
  unit?: string;
  type?: string;
  goal?: number;
  is_active?: boolean;
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

export interface UserInfo {
  id: number;
  username: string;
  created_at?: string;
}

export interface APIKeyInfo {
  id: number;
  created_at: string;
  key_preview: string;
}

export interface NewAPIKey {
  token: string;
  hint: string;
}

export const apiClient = {
  // Authentication
  async signup(username: string): Promise<User> {
    const response = await api.post('/api/signup', { username });
    return response.data;
  },

  async getCurrentUser(): Promise<UserInfo> {
    const response = await api.get('/api/me');
    return response.data;
  },

  // API Key Management
  async listAPIKeys(username: string): Promise<APIKeyInfo[]> {
    const response = await api.get(`/api/keys/${username}`);
    return response.data;
  },

  async createAPIKey(username: string): Promise<NewAPIKey> {
    const response = await api.post(`/api/keys/${username}`);
    return response.data;
  },

  async deleteAPIKey(username: string, token: string): Promise<void> {
    await api.delete(`/api/keys/${username}`, {
      data: { token }
    });
  },

  async deleteAPIKeyById(username: string, keyId: number): Promise<void> {
    await api.delete(`/api/keys/${username}/${keyId}`);
  },

  // User Management
  async deleteAccount(username: string): Promise<void> {
    await api.delete(`/api/user/${username}`);
  },

  // Metrics
  async getMetricsConfig(): Promise<MetricConfig[]> {
    const response = await api.get('/api/metrics/config');
    return response.data;
  },

  async createMetricsConfig(config: UserMetricsConfigCreate): Promise<UserMetricsConfig> {
    const response = await api.post('/api/metrics/config', config);
    return response.data;
  },

  async updateMetricsConfig(metricKey: string, updates: UserMetricsConfigUpdate): Promise<UserMetricsConfig> {
    const response = await api.put(`/api/metrics/config/${metricKey}`, updates);
    return response.data;
  },

  async deleteMetricsConfig(metricKey: string): Promise<void> {
    await api.delete(`/api/metrics/config/${metricKey}`);
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

  async getRecentEntries() {
    const response = await api.get('/api/metrics/recent');
    return response.data;
  },

  async deleteMetricEntry(entryId: number) {
    await api.delete(`/api/metrics/${entryId}`);
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