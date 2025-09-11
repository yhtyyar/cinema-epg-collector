import { memo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import type { Movie } from '../../types/movie';
import ResponsivePoster from './ResponsivePoster';
import { formatTimeMSK } from '../../utils/format';
import { cn } from '../../lib/utils';
import { RATING_THRESHOLDS } from '../../lib/constants';

interface MovieCardProps {
  movie: Movie;
}

function MovieCardComponent({ movie }: MovieCardProps) {
  const navigate = useNavigate();
  const timeStr = formatTimeMSK(movie.broadcast_time);
  const firstCategory = movie.genres?.[0]?.name;

  const handleGenreClick = (e: React.MouseEvent, genre: string) => {
    e.preventDefault();
    e.stopPropagation();
    navigate(`/?genre=${encodeURIComponent(genre)}`);
  };

  const getRatingColor = (rating?: number) => {
    if (typeof rating !== 'number') return 'rgba(239, 68, 68, 0.95)';

    if (rating >= RATING_THRESHOLDS.HIGH) {
      return 'linear-gradient(135deg, rgba(34, 197, 94, 0.95), rgba(22, 163, 74, 0.95))';
    }

    if (rating >= RATING_THRESHOLDS.MEDIUM) {
      return 'linear-gradient(135deg, rgba(251, 191, 36, 0.95), rgba(245, 158, 11, 0.95))';
    }

    return 'linear-gradient(135deg, rgba(239, 68, 68, 0.95), rgba(220, 38, 38, 0.95))';
  };

  return (
    <Link
      to={`/movie/${movie.id}`}
      className="group block rounded-xl overflow-hidden card-hover"
      style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)'
      }}
    >
      <div className="relative">
        <ResponsivePoster
          src={movie.poster_url}
          alt={movie.title}
          priority="normal"
          className="transition-transform duration-300 group-hover:scale-[1.02]"
        >
          {/* Enhanced badge container - элегантное позиционирование */}
          <div className="flex justify-between items-start h-full">
            {/* Left side - Age rating */}
            <div className="self-start">
              <div className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg border border-white/20"
                style={{
                  background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95), rgba(124, 58, 237, 0.95))',
                  color: 'white',
                  backdropFilter: 'blur(12px)'
                }}>
                {movie.age_rating || '18+'}
              </div>
            </div>

            {/* Right side - TMDB rating */}
            <div className="self-start">
              {typeof movie.rating === 'number' && (
                <div className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg flex items-center gap-1.5 border border-white/20"
                  style={{
                    background: getRatingColor(movie.rating),
                    color: 'white',
                    backdropFilter: 'blur(12px)'
                  }}>
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                  {movie.rating.toFixed(1)}
                </div>
              )}
            </div>

            {/* Bottom left - Broadcast time */}
            {timeStr && (
              <div className="absolute bottom-3 left-3">
                <div className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-semibold shadow-lg"
                  style={{
                    background: 'rgba(0, 0, 0, 0.9)',
                    color: 'white',
                    backdropFilter: 'blur(8px)'
                  }}>
                  {timeStr}
                </div>
              </div>
            )}
          </div>
        </ResponsivePoster>
      </div>

      {/* Enhanced content section */}
      <div className="p-4 space-y-3">
        <h3 className="font-bold text-lg leading-tight line-clamp-2 group-hover:gradient-text transition-all duration-200"
          style={{ color: 'var(--text-primary)' }}>
          {movie.title}
        </h3>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <span style={{ color: 'var(--text-secondary)' }}>
              {movie.year || '—'}
            </span>
            {movie.duration && (
              <>
                <span style={{ color: 'var(--text-muted)' }}>•</span>
                <span style={{ color: 'var(--text-secondary)' }} className="text-xs">
                  {movie.duration} мин
                </span>
              </>
            )}
          </div>

          {firstCategory && (
            <button
              type="button"
              onClick={(e) => handleGenreClick(e, firstCategory)}
              className="px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 hover:scale-105 focus-ring"
              style={{
                background: 'linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary))',
                color: 'var(--accent-primary)',
                border: '1px solid var(--border-color)'
              }}
            >
              {firstCategory}
            </button>
          )}
        </div>

        {/* Hover indicator */}
        <div className="flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <span className="text-xs font-medium flex items-center gap-1" style={{ color: 'var(--accent-primary)' }}>
            Подробнее
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </Link>
  );
}

export const MovieCard = memo(MovieCardComponent);