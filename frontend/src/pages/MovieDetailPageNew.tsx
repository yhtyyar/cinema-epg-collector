// pages/MovieDetailPageNew.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Movie } from '../types/movie';
import { useMovies, useMoviesByDate } from '../hooks/useMovies';
import { MovieCarousel } from '../components/movie-carousel/MovieCarousel';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';

export default function MovieDetailPageNew() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { movies, loading, error } = useMovies();
  const { moviesByDate } = useMoviesByDate(movies);
  const [currentMovie, setCurrentMovie] = useState<Movie | null>(null);
  const [sameDayMovies, setSameDayMovies] = useState<Movie[]>([]);

  useEffect(() => {
    if (movies.length > 0 && id) {
      const movie = movies.find(m => m.id === id);
      if (movie) {
        setCurrentMovie(movie);

        // Find movies from the same day
        const movieDate = movie.epg_data.broadcast_time.split('T')[0];
        const dayMovies = moviesByDate[movieDate] || [];
        const otherMovies = dayMovies.filter(m => m.id !== id);
        setSameDayMovies(otherMovies);
      }
    }
  }, [movies, id, moviesByDate]);

  const handleMovieClick = (movie: Movie) => {
    navigate(`/movie/${movie.id}`);
    window.scrollTo(0, 0);
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

  if (!currentMovie) {
    return (
      <ErrorMessage message="Фильм не найден" />
    );
  }

  const formatTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString('ru-RU', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
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

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Movie Poster and Info */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="aspect-w-16 aspect-h-9 bg-gray-200 dark:bg-gray-700">
              {currentMovie.tmdb_data?.poster_url ? (
                <img
                  src={currentMovie.tmdb_data.poster_url}
                  alt={currentMovie.epg_data.title}
                  className="w-full h-96 object-cover"
                />
              ) : (
                <div className="w-full h-96 flex items-center justify-center text-gray-400">
                  <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              )}
            </div>

            <div className="p-6">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                {currentMovie.epg_data.title}
              </h1>

              <div className="flex items-center space-x-4 mb-4">
                <div className="flex items-center space-x-1">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {formatTime(currentMovie.epg_data.broadcast_time)}
                  </span>
                </div>

                {currentMovie.tmdb_data?.rating && (
                  <div className={`flex items-center space-x-1 ${getRatingColor(currentMovie.tmdb_data.rating)}`}>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                    <span className="font-medium">
                      {currentMovie.tmdb_data.rating.toFixed(1)}
                    </span>
                  </div>
                )}
              </div>

              {currentMovie.tmdb_data?.genres && currentMovie.tmdb_data.genres.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-2">
                    {currentMovie.tmdb_data.genres.map((genre, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="prose dark:prose-invert max-w-none">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                  {currentMovie.epg_data.description || currentMovie.tmdb_data?.description || 'Описание недоступно'}
                </p>
              </div>

              {currentMovie.tmdb_data?.year && (
                <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                  Год выпуска: {currentMovie.tmdb_data.year}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Related Movies Carousel */}
        <div className="lg:col-span-1">
          <div className="sticky top-4">
            <MovieCarousel
              title="Другие фильмы сегодня"
              movies={sameDayMovies.slice(0, 6)}
              onMovieClick={handleMovieClick}
              className="space-y-4"
            />
          </div>
        </div>
      </div>

      {/* Additional Carousel for More Movies */}
      {sameDayMovies.length > 6 && (
        <div className="mt-12">
          <MovieCarousel
            title="Ещё фильмы на сегодня"
            movies={sameDayMovies.slice(6)}
            onMovieClick={handleMovieClick}
          />
        </div>
      )}
    </div>
  );
}
