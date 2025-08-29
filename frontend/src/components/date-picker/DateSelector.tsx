// components/date-picker/DateSelector.tsx
import React from 'react';
import { DateOption } from '../../types/movie';

interface DateSelectorProps {
  dateOptions: DateOption[];
  selectedDate: string;
  onDateChange: (date: string) => void;
}

export const DateSelector: React.FC<DateSelectorProps> = ({
  dateOptions,
  selectedDate,
  onDateChange,
}) => {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Выберите дату
        </h2>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {dateOptions.find(d => d.date === selectedDate)?.count || 0} фильмов
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {dateOptions.map((option) => (
          <button
            key={option.date}
            onClick={() => onDateChange(option.date)}
            className={`
              px-4 py-2 rounded-lg font-medium transition-all duration-200
              ${selectedDate === option.date
                ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600'
              }
            `}
          >
            <div className="text-center">
              <div className="text-sm">{option.displayDate}</div>
              <div className="text-xs opacity-75 mt-1">
                {option.count} фильм{option.count !== 1 ? 'ов' : ''}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
