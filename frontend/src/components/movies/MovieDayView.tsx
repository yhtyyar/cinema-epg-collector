// components/movies/MovieDayView.tsx
import React from 'react';
import { Movie } from '../../types/movie';
import { MovieCard } from './MovieCard';

interface MovieDayViewProps {
  date: string;
  movies: Movie[];
  onMovieClick: (movie: Movie) => void;
}

export const MovieDayView: React.FC<MovieDayViewProps> = ({
  date,
  movies,
  onMovieClick,
}) => {
  const formatTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Завтра';
    } else {
      return date.toLocaleDateString('ru-RU', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
          {formatDate(date)}
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {movies.length} фильм{movies.length !== 1 ? 'ов' : ''}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {movies.map((movie) => (
          <div key={movie.id} className="relative">
            <MovieCard
              movie={movie}
              onClick={() => onMovieClick(movie)}
            />
            <div className="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs font-medium">
              {formatTime(movie.epg_data.broadcast_time)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
