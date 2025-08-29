// components/movie-carousel/MovieCarouselNew.tsx
import React from 'react';
import { Movie } from '../../types/movie-new';
import { MovieCard } from '../movies/MovieCardNew';

interface MovieCarouselProps {
  title: string;
  movies: Movie[];
  onMovieClick: (movie: Movie) => void;
  className?: string;
}

export const MovieCarousel: React.FC<MovieCarouselProps> = ({
  title,
  movies,
  onMovieClick,
  className = '',
}) => {
  const scrollRef = React.useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = React.useState(false);
  const [canScrollRight, setCanScrollRight] = React.useState(true);

  const checkScrollButtons = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  React.useEffect(() => {
    checkScrollButtons();
    const element = scrollRef.current;
    if (element) {
      element.addEventListener('scroll', checkScrollButtons);
      return () => element.removeEventListener('scroll', checkScrollButtons);
    }
  }, [movies]);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const cardWidth = 280; // card width + margin
      const scrollAmount = cardWidth * 2; // scroll 2 cards at a time
      const currentScroll = scrollRef.current.scrollLeft;
      const newScroll = direction === 'left'
        ? Math.max(0, currentScroll - scrollAmount)
        : currentScroll + scrollAmount;

      scrollRef.current.scrollTo({
        left: newScroll,
        behavior: 'smooth'
      });
    }
  };

  if (movies.length === 0) {
    return null;
  }

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
          {title}
        </h3>
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {movies.length} фильм{movies.length > 4 ? 'ов' : movies.length > 1 ? 'а' : ''}
          </span>
          <div className="flex space-x-2">
            <button
              onClick={() => scroll('left')}
              disabled={!canScrollLeft}
              className={`p-3 rounded-full shadow-lg transition-all duration-200 border ${
                canScrollLeft
                  ? 'bg-white dark:bg-gray-800 hover:shadow-xl hover:scale-110 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400'
                  : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-400 cursor-not-allowed'
              }`}
              aria-label="Предыдущие фильмы"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={() => scroll('right')}
              disabled={!canScrollRight}
              className={`p-3 rounded-full shadow-lg transition-all duration-200 border ${
                canScrollRight
                  ? 'bg-white dark:bg-gray-800 hover:shadow-xl hover:scale-110 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400'
                  : 'bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-400 cursor-not-allowed'
              }`}
              aria-label="Следующие фильмы"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex space-x-6 overflow-x-auto scrollbar-hide pb-4"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {movies.map((movie) => (
          <div
            key={movie.id}
            className="flex-shrink-0 w-64 transform transition-transform duration-200 hover:scale-105"
          >
            <MovieCard
              movie={movie}
              onClick={() => onMovieClick(movie)}
              compact={true}
            />
          </div>
        ))}
      </div>

      <style>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
};
