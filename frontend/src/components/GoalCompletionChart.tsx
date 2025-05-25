'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface GoalCompletionChartProps {
  completed: number;
  total: number;
  metricName: string;
  size?: number;
  showRawValues?: boolean;
  metricType?: string; // "min" or "max"
}

const COLORS = {
  completed: '#10B981', // Emerald green (neon green)
  remaining: '#D1FAE5', // Light green
  exceeded: '#FCA5A5', // Light red for when max goals are exceeded
  exceededRemaining: '#FEE2E2', // Very light red
};

export default function GoalCompletionChart({ 
  completed, 
  total, 
  metricName, 
  size = 120,
  showRawValues = false,
  metricType = "min"
}: GoalCompletionChartProps) {
  // For max goals, if completed > total, we've exceeded the limit
  const isMaxGoalExceeded = metricType === "max" && completed > total;
  
  let data, percentage;
  
  if (isMaxGoalExceeded) {
    // For exceeded max goals, show the excess in red
    const withinLimit = total;
    const excess = completed - total;
    percentage = 100; // Always 100% since we exceeded
    data = [
      { name: 'Within Limit', value: withinLimit, color: COLORS.completed },
      { name: 'Exceeded', value: excess, color: COLORS.exceeded },
    ];
  } else {
    const remaining = Math.max(0, total - completed);
    percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    data = [
      { name: 'Completed', value: completed, color: COLORS.completed },
      { name: 'Remaining', value: remaining, color: COLORS.remaining },
    ];
  }

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number }> }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-2 border border-green-200 rounded-lg shadow-lg">
          <p className="text-xs sm:text-sm text-gray-700">
            {data.name}: {data.value} day{data.value !== 1 ? 's' : ''}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className="relative" style={{ width: size, height: size }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={size * 0.35}
              outerRadius={size * 0.45}
              startAngle={90}
              endAngle={-270}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {showRawValues ? (
            <span className="text-xl sm:text-2xl font-bold text-green-700">{completed}</span>
          ) : (
            <span className="text-xl sm:text-2xl font-bold text-green-700">{percentage}%</span>
          )}
          <span className="text-xs text-gray-500 text-center leading-tight">
            {showRawValues ? `out of ${total}` : `${completed}/${total}`}
          </span>
        </div>
      </div>
      <h3 className="text-xs sm:text-sm font-medium text-gray-700 capitalize text-center">
        {metricName}
      </h3>
    </div>
  );
} 