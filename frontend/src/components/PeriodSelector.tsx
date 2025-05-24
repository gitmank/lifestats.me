'use client';

interface PeriodSelectorProps {
  selectedPeriod: 'weekly' | 'monthly' | 'yearly';
  onPeriodChange: (period: 'weekly' | 'monthly' | 'yearly') => void;
}

const periods = [
  { value: 'weekly' as const, label: 'Week', days: 7 },
  { value: 'monthly' as const, label: 'Month', days: 30 },
  { value: 'yearly' as const, label: 'Year', days: 365 },
];

export default function PeriodSelector({ selectedPeriod, onPeriodChange }: PeriodSelectorProps) {
  return (
    <div className="flex space-x-0.5 sm:space-x-1 bg-green-50 p-0.5 sm:p-1 rounded-lg border border-green-200">
      {periods.map((period) => (
        <button
          key={period.value}
          onClick={() => onPeriodChange(period.value)}
          className={`px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm font-medium rounded-md transition-all duration-200 ${
            selectedPeriod === period.value
              ? 'bg-green-500 text-white shadow-sm'
              : 'text-green-700 hover:bg-green-100'
          }`}
        >
          {period.label}
        </button>
      ))}
    </div>
  );
} 