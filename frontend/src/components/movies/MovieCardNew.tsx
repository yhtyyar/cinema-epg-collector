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
    ? "bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer group"
    : "bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 cursor-pointer transform hover:-translate-y-2 group";

  return (
    <div className={cardClasses} onClick={() => onClick(movie)}>
      {/* Poster Image Container - Maintains aspect ratio */}
      <div className="relative overflow-hidden">
        {movie.tmdb_data?.poster_url ? (
          <img
            src={movie.tmdb_data.poster_url}
            alt={movie.epg_data.title}
            className="w-full h-auto object-contain bg-gray-100 dark:bg-gray-700 transition-transform duration-300 group-hover:scale-105"
            style={{ aspectRatio: '2/3' }}
          />
        ) : movie.epg_data.preview_image ? (
          <img
            src={movie.epg_data.preview_image}
            alt={movie.epg_data.title}
            className="w-full h-auto object-contain bg-gray-100 dark:bg-gray-700 transition-transform duration-300 group-hover:scale-105"
            style={{ aspectRatio: '2/3' }}
          />
        ) : (
          <div 
            className="w-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center"
            style={{ aspectRatio: '2/3' }}
          >
            <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 4v16l13-8L7 4z" />
            </svg>
          </div>
        )}

        {/* Time Badge */}
        <div className="absolute top-3 right-3 bg-black/80 text-white px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm">
          {formatTime(movie.epg_data.broadcast_time)}
        </div>

        {/* Rating Badge */}
        {movie.tmdb_data?.rating && (
          <div className="absolute top-3 left-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-3 py-1 rounded-full text-sm font-bold flex items-center space-x-1 shadow-lg">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            <span>{movie.tmdb_data.rating.toFixed(1)}</span>
          </div>
        )}

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>

      {/* Content */}
      <div className={compact ? "p-3" : "p-4"}>
        <h3 className={`font-bold text-gray-900 dark:text-white mb-2 leading-tight ${compact ? 'text-sm' : 'text-lg'}`}>
          {movie.epg_data.title}
        </h3>

        {!compact && movie.epg_data.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2 leading-relaxed">
            {movie.epg_data.description}
          </p>
        )}

        {/* Genres */}
        {movie.tmdb_data?.genres && movie.tmdb_data.genres.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {movie.tmdb_data.genres.slice(0, compact ? 1 : 3).map((genre: string, index: number) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 text-xs rounded-md font-medium"
              >
                {genre}
              </span>
            ))}
          </div>
        )}

        {/* Year and Additional Info */}
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          {movie.tmdb_data?.year && (
            <span className="font-medium">{movie.tmdb_data.year}</span>
          )}
          <span className="text-blue-600 dark:text-blue-400 font-medium group-hover:text-blue-700 dark:group-hover:text-blue-300">
            Подробнее →
          </span>
        </div>
      </div>
    </div>
  );
};
