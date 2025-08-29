// components/movies/MovieCardNew.tsx
import React from 'react';
import { Movie } from '../../types/movie-new';

interface MovieCardProps {
  movie: Movie;
  onClick: (movie: Movie) => void;
  compact?: boolean;
}

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  onClick,
  compact = false
}) => {
  const formatTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRatingColor = (rating?: number) => {
    if (!rating) return 'text-gray-400';
    if (rating >= 7) return 'text-green-500';
    if (rating >= 5) return 'text-yellow-500';
    return 'text-red-500';
  };

  const cardClasses = compact
    ? "bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
    : "bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1";

  const imageClasses = compact
    ? "w-full h-48 object-cover"
    : "w-full h-64 object-cover";

  const contentClasses = compact
    ? "p-3"
    : "p-4";

  return (
    <div className={cardClasses} onClick={() => onClick(movie)}>
      {/* Poster Image */}
      <div className="relative">
        {movie.tmdb_data?.poster_url ? (
          <img
            src={movie.tmdb_data.poster_url}
            alt={movie.epg_data.title}
            className={imageClasses}
          />
        ) : movie.epg_data.preview_image ? (
          <img
            src={movie.epg_data.preview_image}
            alt={movie.epg_data.title}
            className={imageClasses}
          />
        ) : (
          <div className={`${imageClasses} bg-gray-200 dark:bg-gray-700 flex items-center justify-center`}>
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Rating Badge */}
        {movie.tmdb_data?.rating && (
          <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-sm font-medium flex items-center space-x-1">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
            <span>{movie.tmdb_data.rating.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className={contentClasses}>
        <h3 className={`font-semibold text-gray-900 dark:text-white mb-1 ${compact ? 'text-sm' : 'text-lg'}`}>
          {movie.epg_data.title}
        </h3>

        {!compact && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
            {movie.epg_data.description}
          </p>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1 text-sm text-gray-500 dark:text-gray-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{formatTime(movie.epg_data.broadcast_time)}</span>
          </div>

          {movie.tmdb_data?.genres && movie.tmdb_data.genres.length > 0 && !compact && (
            <div className="flex flex-wrap gap-1">
              {movie.tmdb_data.genres.slice(0, 2).map((genre: string, index: number) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                >
                  {genre}
                </span>
              ))}
            </div>
          )}
        </div>

        {movie.tmdb_data?.year && !compact && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            {movie.tmdb_data.year}
          </div>
        )}
      </div>
    </div>
  );
};
