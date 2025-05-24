'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface GoalCompletionChartProps {
  completed: number;
  total: number;
  metricName: string;
  size?: number;
}

const COLORS = {
  completed: '#10B981', // Emerald green (neon green)
  remaining: '#D1FAE5', // Light green
};

export default function GoalCompletionChart({ 
  completed, 
  total, 
  metricName, 
  size = 120 
}: GoalCompletionChartProps) {
  const remaining = Math.max(0, total - completed);
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  const data = [
    { name: 'Completed', value: completed, color: COLORS.completed },
    { name: 'Remaining', value: remaining, color: COLORS.remaining },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="bg-white p-2 border border-green-200 rounded-lg shadow-lg">
          <p className="text-sm text-gray-700">
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
          <span className="text-2xl font-bold text-green-700">{percentage}%</span>
          <span className="text-xs text-gray-500 text-center leading-tight">
            {completed}/{total}
          </span>
        </div>
      </div>
      <h3 className="text-sm font-medium text-gray-700 capitalize text-center">
        {metricName}
      </h3>
    </div>
  );
} 