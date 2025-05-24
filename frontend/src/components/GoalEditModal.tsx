'use client';

import { useState } from 'react';
import { X, Save } from 'lucide-react';

interface GoalEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (newGoal: number) => Promise<void>;
  metricName: string;
  metricUnit: string;
  currentGoal: number;
}

export default function GoalEditModal({
  isOpen,
  onClose,
  onSave,
  metricName,
  metricUnit,
  currentGoal
}: GoalEditModalProps) {
  const [goalValue, setGoalValue] = useState(currentGoal.toString());
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSave = async () => {
    const numValue = parseFloat(goalValue);
    if (isNaN(numValue) || numValue <= 0) {
      setError('Please enter a valid positive number');
      return;
    }

    setIsSaving(true);
    setError('');
    
    try {
      await onSave(numValue);
      onClose();
    } catch (err) {
      setError('Failed to save goal. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    setGoalValue(currentGoal.toString());
    setError('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-md">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">
            Edit Goal for {metricName}
          </h2>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Goal Value ({metricUnit})
            </label>
            <input
              type="number"
              value={goalValue}
              onChange={(e) => setGoalValue(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900"
              placeholder="Enter goal value"
              step="0.1"
              min="0"
              disabled={isSaving}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <button
              onClick={handleClose}
              disabled={isSaving}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex-1 flex items-center justify-center space-x-2 bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>{isSaving ? 'Saving...' : 'Save Goal'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 