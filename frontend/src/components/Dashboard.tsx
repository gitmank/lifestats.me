'use client';

import { useState, useEffect } from 'react';
import { LogOut, TrendingUp, Copy, Check, Edit2, Plus } from 'lucide-react';
import GoalCompletionChart from './GoalCompletionChart';
import PeriodSelector from './PeriodSelector';
import GoalEditModal from './GoalEditModal';
import AddMetricModal from './AddMetricModal';
import { MetricConfig, AggregatedMetrics, apiClient } from '@/lib/api';

interface DashboardProps {
  username: string;
  onLogout: () => void;
}

const periodDays = {
  weekly: 7,
  monthly: 30,
  yearly: 365,
};

export default function Dashboard({ username, onLogout }: DashboardProps) {
  const [selectedPeriod, setSelectedPeriod] = useState<'weekly' | 'monthly' | 'yearly'>('weekly');
  const [metrics, setMetrics] = useState<AggregatedMetrics | null>(null);
  const [config, setConfig] = useState<MetricConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [editingGoal, setEditingGoal] = useState<{ metric: MetricConfig; isOpen: boolean } | null>(null);
  const [addingMetric, setAddingMetric] = useState<{ metric: MetricConfig; isOpen: boolean } | null>(null);

  const copyApiKey = async () => {
    const apiKey = localStorage.getItem('authToken');
    if (apiKey) {
      try {
        await navigator.clipboard.writeText(apiKey);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy API key:', err);
      }
    }
  };

  const handleEditGoal = (metric: MetricConfig) => {
    setEditingGoal({ metric, isOpen: true });
  };

  const handleAddMetric = (metric: MetricConfig) => {
    setAddingMetric({ metric, isOpen: true });
  };

  const handleSaveGoal = async (newGoal: number) => {
    if (!editingGoal) return;
    
    try {
      await apiClient.updateGoal(editingGoal.metric.key, newGoal);
      
      // Update the local config state
      setConfig(prevConfig => 
        prevConfig.map(metric => 
          metric.key === editingGoal.metric.key 
            ? { ...metric, goal: newGoal }
            : metric
        )
      );
      
      // Refresh metrics data to update the charts
      await fetchData();
    } catch (err) {
      console.error('Failed to update goal:', err);
      throw err;
    }
  };

  const handleSaveMetric = async (value: number, timestamp?: string) => {
    if (!addingMetric) return;
    
    try {
      await apiClient.addMetricEntry(addingMetric.metric.key, value, timestamp);
      
      // Refresh metrics data to update the charts
      await fetchData();
    } catch (err) {
      console.error('Failed to add metric entry:', err);
      throw err;
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [metricsResponse, configResponse] = await Promise.all([
        fetch('/api/metrics', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          },
        }),
        fetch('/api/metrics/config'),
      ]);

      if (!metricsResponse.ok || !configResponse.ok) {
        throw new Error('Failed to fetch data');
      }

      const [metricsData, configData] = await Promise.all([
        metricsResponse.json(),
        configResponse.json(),
      ]);

      setMetrics(metricsData);
      setConfig(configData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading your stats...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center">
          <div className="text-red-500 mb-4">
            <TrendingUp className="w-12 h-12 mx-auto" />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Unable to load data</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={onLogout}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Return to Login
          </button>
        </div>
      </div>
    );
  }

  const currentPeriodData = metrics?.[selectedPeriod];
  const totalDays = periodDays[selectedPeriod];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-green-200">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Life Stats Dashboard</h1>
            <p className="text-gray-600">Welcome back, {username}</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-1">Your API Key (click to copy):</p>
              <button
                onClick={copyApiKey}
                className="flex items-center space-x-1 bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition-colors"
              >
                <code className="text-xs text-gray-700">
                  {localStorage.getItem('authToken')?.substring(0, 12)}...
                </code>
                {copied ? (
                  <Check className="w-3 h-3 text-green-500" />
                ) : (
                  <Copy className="w-3 h-3 text-gray-500" />
                )}
              </button>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Period Selector */}
        <div className="flex justify-center mb-8">
          <PeriodSelector 
            selectedPeriod={selectedPeriod} 
            onPeriodChange={setSelectedPeriod}
          />
        </div>

        {/* Period Info */}
        <div className="text-center mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Goal Completion for the Last {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1, -2)}
          </h2>
          <p className="text-gray-600">
            Days completed out of {totalDays} possible days
          </p>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8 justify-items-center">
          {config.map((metric) => {
            const completed = currentPeriodData?.goalReached?.[metric.key] || 0;
            return (
              <div key={metric.key} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow relative">
                {/* Plus button in top right corner */}
                <button
                  onClick={() => handleAddMetric(metric)}
                  className="absolute top-3 right-3 p-1.5 hover:bg-green-100 rounded-full transition-colors"
                  title="Log metric"
                >
                  <Plus className="w-4 h-4 text-green-600 hover:text-green-700" />
                </button>
                
                <GoalCompletionChart
                  completed={completed}
                  total={totalDays}
                  metricName={metric.name}
                  size={140}
                />
                <div className="mt-4 text-center">
                  <div className="flex items-center justify-center space-x-2">
                    <p className="text-xs text-gray-500">
                      Goal: <span className="font-bold text-gray-700">{metric.goal || 'Not set'}</span> {metric.unit}
                    </p>
                    <button
                      onClick={() => handleEditGoal(metric)}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                      title="Edit goal"
                    >
                      <Edit2 className="w-3 h-3 text-gray-400 hover:text-gray-600" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary Stats */}
        <div className="mt-12 bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
            {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1, -2)} Summary
          </h3>
          
          {selectedPeriod === 'weekly' ? (
            /* Weekly Daily Totals Grid */
            <div className="space-y-6">
              {/* Day Labels */}
              <div className="flex justify-center">
                <div className="grid grid-cols-7 gap-2 text-xs text-gray-500 font-medium">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                    <div key={day} className="w-8 text-center">
                      {day}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                {config.map((metric) => {
                  const dailyTotals = currentPeriodData?.daily_totals?.[metric.key] || [];
                  const goal = metric.goal;
                  
                  return (
                    <div key={metric.key} className="text-center">
                      <div className="text-sm font-medium text-gray-700 capitalize mb-3">
                        {metric.name}
                      </div>
                      <div className="flex justify-center space-x-2 mb-2">
                        {dailyTotals.map((value: number, dayIndex: number) => {
                          const isGoalMet = value >= goal;
                          const intensity = Math.min(value / goal, 1); // Cap at 100%
                          const opacity = Math.max(0.2, intensity); // Minimum 20% opacity
                          
                          return (
                            <div
                              key={dayIndex}
                              className={`w-8 h-8 rounded border flex items-center justify-center text-xs font-medium cursor-help ${
                                isGoalMet 
                                  ? 'bg-green-500 text-white shadow-sm border-green-200' 
                                  : 'bg-red-100 text-red-700 border-red-200'
                              }`}
                              style={{
                                backgroundColor: isGoalMet 
                                  ? '#10B981' 
                                  : `rgba(239, 68, 68, ${opacity * 0.3 + 0.1})`, // Light red with opacity
                                color: isGoalMet ? 'white' : '#DC2626'
                              }}
                              title={`Day ${dayIndex + 1}: ${value} ${metric.unit} (Goal: ${goal})`}
                            >
                              {Math.round(value)}
                            </div>
                          );
                        })}
                      </div>
                      <div className="text-xs text-gray-500">
                        Goal: <span className="font-bold text-gray-700">{goal || 'Not set'}</span> {metric.unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Monthly/Yearly Average Values Grid */
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {config.map((metric) => {
                const average = currentPeriodData?.average_values?.[metric.key] || 0;
                const goal = metric.goal;
                const isGoalMet = average >= goal;
                
                return (
                  <div key={metric.key} className="text-center">
                    <div className="text-sm font-medium text-gray-700 capitalize mb-3">
                      {metric.name}
                    </div>
                    <div className="flex justify-center mb-2">
                      <div
                        className={`w-16 h-16 rounded-lg border flex items-center justify-center text-sm font-medium cursor-help ${
                          isGoalMet 
                            ? 'bg-green-500 text-white shadow-sm border-green-200' 
                            : 'bg-red-100 text-red-700 border-red-200'
                        }`}
                        title={`Average: ${average.toFixed(1)} ${metric.unit} (Goal: ${goal})`}
                      >
                        {average.toFixed(1)}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      Goal: <span className="font-bold text-gray-700">{goal || 'Not set'}</span> {metric.unit}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Goal Edit Modal */}
      {editingGoal && (
        <GoalEditModal
          isOpen={editingGoal.isOpen}
          onClose={() => setEditingGoal(null)}
          onSave={handleSaveGoal}
          metricName={editingGoal.metric.name}
          metricUnit={editingGoal.metric.unit}
          currentGoal={editingGoal.metric.goal || 0}
        />
      )}

      {/* Add Metric Modal */}
      {addingMetric && (
        <AddMetricModal
          isOpen={addingMetric.isOpen}
          onClose={() => setAddingMetric(null)}
          onSave={handleSaveMetric}
          metricName={addingMetric.metric.name}
          metricUnit={addingMetric.metric.unit}
          goalValue={addingMetric.metric.goal || 0}
        />
      )}
    </div>
  );
} 