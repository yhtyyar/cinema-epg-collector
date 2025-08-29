// components/movies/MovieDayViewNew.tsx
import React from 'react';
import { Movie } from '../../types/movie-new';
import { MovieCard } from './MovieCardNew';

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
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {formatDate(date)}
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          {movies.length} фильм{movies.length > 4 ? 'ов' : movies.length > 1 ? 'а' : ''} доступно для просмотра
        </p>
      </div>

      {/* Adaptive Grid - Adjusts to poster aspect ratios */}
      <div className="grid gap-6" style={{
        gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
        gridAutoRows: 'auto'
      }}>
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onClick={() => onMovieClick(movie)}
          />
        ))}
      </div>
    </div>
  );
};
