// components/date-picker/DateSelector.tsx
import React from 'react';
import { DateOption } from '../../types/movie-new';

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
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 200;
      const currentScroll = scrollRef.current.scrollLeft;
      const newScroll = direction === 'left'
        ? currentScroll - scrollAmount
        : currentScroll + scrollAmount;

      scrollRef.current.scrollTo({
        left: newScroll,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Выберите дату
        </h2>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {dateOptions.find(d => d.date === selectedDate)?.count || 0} фильмов
        </div>
      </div>

      <div className="relative">
        {/* Scroll buttons */}
        {dateOptions.length > 3 && (
          <>
            <button
              onClick={() => scroll('left')}
              className="absolute left-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-shadow border border-gray-200 dark:border-gray-600"
              aria-label="Предыдущие даты"
            >
              <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={() => scroll('right')}
              className="absolute right-0 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg hover:shadow-xl transition-shadow border border-gray-200 dark:border-gray-600"
              aria-label="Следующие даты"
            >
              <svg className="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </>
        )}

        {/* Date options carousel */}
        <div
          ref={scrollRef}
          className="flex space-x-3 overflow-x-auto scrollbar-hide pb-2"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {dateOptions.map((option) => (
            <button
              key={option.date}
              onClick={() => onDateChange(option.date)}
              className={`
                flex-shrink-0 px-6 py-3 rounded-xl font-medium transition-all duration-300 transform
                ${selectedDate === option.date
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-105 ring-2 ring-blue-300'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:shadow-md hover:scale-102'
                }
              `}
            >
              <div className="text-center min-w-[80px]">
                <div className={`text-sm font-semibold ${selectedDate === option.date ? 'text-white' : ''}`}>
                  {option.displayDate}
                </div>
                <div className={`text-xs mt-1 ${selectedDate === option.date ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'}`}>
                  {option.count} фильм{option.count !== 1 ? (option.count > 4 ? 'ов' : 'а') : ''}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <style>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
};
