// pages/HomePage.tsx
import React, { useState, useMemo } from 'react';
import { useMovies, useMoviesByDate } from '../hooks/useMovies';
import { DateSelector } from '../components/date-picker/DateSelector';
import { MovieDayView } from '../components/movies/MovieDayView';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Movie } from '../types/movie';

export default function HomePage() {
  const { movies, loading, error } = useMovies();
  const { moviesByDate, dateOptions } = useMoviesByDate(movies);
  const [selectedDate, setSelectedDate] = useState<string>('');

  // Set default date to today or first available date
  React.useEffect(() => {
    if (dateOptions.length > 0 && !selectedDate) {
      const todayOption = dateOptions.find(option => option.isToday);
      setSelectedDate(todayOption?.date || dateOptions[0].date);
    }
  }, [dateOptions, selectedDate]);

  const handleMovieClick = (movie: Movie) => {
    window.location.href = `/movie/${movie.id}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  const selectedMovies = selectedDate ? moviesByDate[selectedDate] || [] : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          IPTV Кинотеатр
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Откройте для себя фильмы из IPTV программ
        </p>
      </div>

      <DateSelector
        dateOptions={dateOptions}
        selectedDate={selectedDate}
        onDateChange={setSelectedDate}
      />

      {selectedMovies.length > 0 ? (
        <MovieDayView
          date={selectedDate}
          movies={selectedMovies}
          onMovieClick={handleMovieClick}
        />
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-400 dark:text-gray-600 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16l13-8L7 4z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Нет фильмов на выбранную дату
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Выберите другую дату для просмотра доступных фильмов
          </p>
        </div>
      )}
    </div>
  );
}
