'use client';

import { useState, useEffect } from 'react';
import { Settings, TrendingUp, Edit2, Plus, Info } from 'lucide-react';
import GoalCompletionChart from './GoalCompletionChart';
import PeriodSelector from './PeriodSelector';
import GoalEditModal from './GoalEditModal';
import AddMetricModal from './AddMetricModal';
import Profile from './Profile';
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
  const [editingGoal, setEditingGoal] = useState<{ metric: MetricConfig; isOpen: boolean } | null>(null);
  const [addingMetric, setAddingMetric] = useState<{ metric: MetricConfig; isOpen: boolean } | null>(null);
  const [showProfile, setShowProfile] = useState(false);
  const [tooltip, setTooltip] = useState<{ show: boolean; content: string; x: number; y: number }>({
    show: false,
    content: '',
    x: 0,
    y: 0
  });

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

  const handleTooltipShow = (event: React.MouseEvent, content: string) => {
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltip({
      show: true,
      content,
      x: rect.left + rect.width / 2,
      y: rect.top - 10
    });
  };

  const handleTooltipHide = () => {
    setTooltip({ show: false, content: '', x: 0, y: 0 });
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [metricsData, configData] = await Promise.all([
        apiClient.getMetrics(),
        apiClient.getMetricsConfig(),
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

  if (showProfile) {
    return (
      <Profile
        username={username}
        onBack={() => setShowProfile(false)}
        onLogout={onLogout}
      />
    );
  }

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
      <div className="bg-white shadow-sm border-b border-green-100">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-green-100 rounded-full flex items-center justify-center">
                <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-gray-800">Life Stats Dashboard</h1>
                <p className="text-xs sm:text-sm text-gray-600">Welcome back, {username}!</p>
              </div>
            </div>

            <div className="flex items-center space-x-2 sm:space-x-3">
              <button
                onClick={() => setShowProfile(true)}
                className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span className="hidden sm:inline">Manage</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-3 sm:px-4 lg:px-6 py-4 sm:py-8">
        {/* Period Selector */}
        <div className="flex justify-center mb-6 sm:mb-8">
          <PeriodSelector 
            selectedPeriod={selectedPeriod} 
            onPeriodChange={setSelectedPeriod}
          />
        </div>

        {/* Period Info */}
        <div className="text-center mb-6 sm:mb-8">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-2">
            Goal Completion for the Last {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1, -2)}
          </h2>
          <p className="text-sm sm:text-base text-gray-600">
            Days completed out of {totalDays} possible days
          </p>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 sm:gap-6 lg:gap-8 justify-items-center">
          {config.map((metric) => {
            const completed = currentPeriodData?.goalReached?.[metric.key] || 0;
            return (
              <div key={metric.key} className="bg-white rounded-xl shadow-lg p-4 sm:p-6 hover:shadow-xl transition-shadow relative w-full max-w-[200px]">
                {/* Plus button in top right corner */}
                <button
                  onClick={() => handleAddMetric(metric)}
                  className="absolute top-2 right-2 sm:top-3 sm:right-3 p-1 sm:p-1.5 hover:bg-green-100 rounded-full transition-colors"
                  title="Log metric"
                >
                  <Plus className="w-3 h-3 sm:w-4 sm:h-4 text-green-600 hover:text-green-700" />
                </button>
                
                <GoalCompletionChart
                  completed={completed}
                  total={totalDays}
                  metricName={metric.name}
                  size={120}
                />
                <div className="mt-3 sm:mt-4 text-center">
                  <div className="flex items-center justify-center space-x-1 sm:space-x-2">
                    <p className="text-xs text-gray-500">
                      {metric.type === 'max' ? 'Limit' : 'Goal'}: <span className="font-bold text-gray-700">{metric.goal || 'Not set'}</span> {metric.unit}
                    </p>
                    <button
                      onClick={() => handleEditGoal(metric)}
                      className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                      title={`Edit ${metric.type === 'max' ? 'limit' : 'goal'}`}
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
        <div className="mt-8 sm:mt-12 bg-white rounded-xl shadow-lg p-4 sm:p-6">
          <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-4 text-center">
            {selectedPeriod.charAt(0).toUpperCase() + selectedPeriod.slice(1, -2)} Summary
          </h3>
          
          {selectedPeriod === 'weekly' ? (
            /* Weekly Daily Totals Grid */
            <div className="space-y-4 sm:space-y-6">
              {/* Day Labels */}
              <div className="flex justify-center">
                <div className="grid grid-cols-7 gap-1 sm:gap-2 text-xs text-gray-500 font-medium">
                  {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                    <div key={day} className="w-7 sm:w-9 text-center">
                      {day}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 sm:gap-6">
                {config.map((metric) => {
                  const dailyTotals = currentPeriodData?.daily_totals?.[metric.key] || [];
                  const goal = metric.goal;
                  
                  return (
                    <div key={metric.key} className="text-center">
                      <div className="text-sm font-medium text-gray-700 capitalize mb-2 sm:mb-3">
                        {metric.name}
                      </div>
                      <div className="flex justify-center space-x-1 sm:space-x-2 mb-2">
                        {dailyTotals.map((value: number, dayIndex: number) => {
                          const isGoalMet = metric.type === 'max' ? value <= goal : value >= goal;
                          const roundedValue = Math.round(value);
                          const valueStr = roundedValue.toString();
                          const hasLargeNumber = valueStr.length > 3;
                          
                          return (
                            <div
                              key={dayIndex}
                              className={`w-7 h-7 sm:w-9 sm:h-9 rounded border flex items-center justify-center font-medium cursor-help ${
                                isGoalMet 
                                  ? 'bg-green-500 text-white shadow-sm border-green-200' 
                                  : 'bg-red-100 text-red-700 border-red-200'
                              }`}
                              style={{
                                backgroundColor: isGoalMet 
                                  ? '#10B981' 
                                  : `rgba(239, 68, 68, ${Math.max(0.2, Math.min(value / goal, 1)) * 0.3 + 0.1})`,
                                color: isGoalMet ? 'white' : '#DC2626'
                              }}
                              onMouseEnter={(e) => handleTooltipShow(e, `Day ${dayIndex + 1}: ${value} ${metric.unit} (${metric.type === 'max' ? 'Limit' : 'Goal'}: ${goal})`)}
                              onMouseLeave={handleTooltipHide}
                            >
                              {hasLargeNumber ? (
                                <Info className="w-3 h-3 sm:w-4 sm:h-4" />
                              ) : (
                                <span className={`font-medium ${
                                  valueStr.length === 3 ? 'text-[10px] sm:text-xs' : 
                                  valueStr.length === 2 ? 'text-xs sm:text-sm' : 
                                  'text-xs sm:text-sm'
                                }`}>
                                  {roundedValue}
                                </span>
                              )}
                            </div>
                          );
                        })}
                      </div>
                      <div className="text-xs text-gray-500">
                        {metric.type === 'max' ? 'Limit' : 'Goal'}: <span className="font-bold text-gray-700">{goal || 'Not set'}</span> {metric.unit}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Monthly/Yearly Average Values Grid */
            <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 sm:gap-6">
              {config.map((metric) => {
                const average = currentPeriodData?.average_values?.[metric.key] || 0;
                const goal = metric.goal;
                const isGoalMet = metric.type === 'max' ? average <= goal : average >= goal;
                
                return (
                  <div key={metric.key} className="text-center">
                    <div className="text-sm font-medium text-gray-700 capitalize mb-2 sm:mb-3">
                      {metric.name}
                    </div>
                    <div className="flex justify-center mb-2">
                      <div
                        className={`w-12 h-12 sm:w-16 sm:h-16 rounded-lg border flex items-center justify-center text-xs sm:text-sm font-medium cursor-help ${
                          isGoalMet 
                            ? 'bg-green-500 text-white shadow-sm border-green-200' 
                            : 'bg-red-100 text-red-700 border-red-200'
                        }`}
                        onMouseEnter={(e) => handleTooltipShow(e, `Average: ${average.toFixed(1)} ${metric.unit} (${metric.type === 'max' ? 'Limit' : 'Goal'}: ${goal})`)}
                        onMouseLeave={handleTooltipHide}
                      >
                        {average.toFixed(1)}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {metric.type === 'max' ? 'Limit' : 'Goal'}: <span className="font-bold text-gray-700">{goal || 'Not set'}</span> {metric.unit}
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
          metricType={editingGoal.metric.type}
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
          metricType={addingMetric.metric.type}
          goalValue={addingMetric.metric.goal || 0}
        />
      )}

      {/* Custom Tooltip */}
      {tooltip.show && (
        <div
          className="fixed z-50 bg-gray-800 text-white text-xs px-2 py-1 rounded shadow-lg pointer-events-none transform -translate-x-1/2 -translate-y-full"
          style={{
            left: tooltip.x,
            top: tooltip.y,
          }}
        >
          {tooltip.content}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800"></div>
        </div>
      )}
    </div>
  );
} 