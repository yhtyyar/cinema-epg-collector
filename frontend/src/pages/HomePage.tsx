import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMovies, useMoviesByDate } from '../hooks/useMoviesNew';
import { DateSelector } from '../components/date-picker/DateSelector';
import { MovieDayView } from '../components/movies/MovieDayViewNew';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { Movie } from '../types/movie-new';

export default function HomePage() {
  const navigate = useNavigate();
  const { movies, loading, error } = useMovies();
  const { moviesByDate, dateOptions } = useMoviesByDate(movies);
  const [selectedDate, setSelectedDate] = useState<string>('');

  // Set default date to today or first available date
  React.useEffect(() => {
    if (dateOptions.length > 0 && !selectedDate) {
      const today = new Date().toISOString().split('T')[0];
      const todayOption = dateOptions.find(option => option.date === today);
      setSelectedDate(todayOption?.date || dateOptions[0].date);
    }
  }, [dateOptions, selectedDate]);

  const handleMovieClick = (movie: Movie) => {
    navigate(`/movie/${movie.id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800">
        <div className="flex justify-center items-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <ErrorMessage message={error} />
        </div>
      </div>
    );
  }

  const selectedMovies = selectedDate ? moviesByDate[selectedDate] || [] : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header with Date Selection */}
      <div className="sticky top-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                IPTV Кинотеатр
              </h1>
              <p className="text-lg text-gray-600 dark:text-gray-400 mt-2">
                Откройте для себя лучшие фильмы из IPTV программ
              </p>
            </div>
            
            <DateSelector
              dateOptions={dateOptions}
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {selectedMovies.length > 0 ? (
          <MovieDayView
            date={selectedDate}
            movies={selectedMovies}
            onMovieClick={handleMovieClick}
          />
        ) : (
          <div className="text-center py-20">
            <div className="text-gray-400 dark:text-gray-600 mb-6">
              <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 4v16l13-8L7 4z" />
              </svg>
            </div>
            <h3 className="text-2xl font-medium text-gray-900 dark:text-white mb-4">
              Нет фильмов на выбранную дату
            </h3>
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              Выберите другую дату для просмотра доступных фильмов
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
