// pages/MovieDetailPageNew.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Movie } from '../types/movie-new';
import { useMovies, useMoviesByDate } from '../hooks/useMoviesNew';
import { MovieCarousel } from '../components/movie-carousel/MovieCarouselNew';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

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

  const getCarouselTitle = () => {
    const movieDate = currentMovie.epg_data.broadcast_time.split('T')[0];
    const today = new Date().toISOString().split('T')[0];
    
    if (movieDate === today) {
      return 'Другие фильмы сегодня';
    } else {
      const date = new Date(movieDate);
      const formattedDate = date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        weekday: 'long'
      });
      return `Другие фильмы на ${formattedDate}`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Back Button */}
        <button
          onClick={() => navigate('/')}
          className="mb-6 flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span>Назад к фильмам</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-12">
          {/* Movie Poster */}
          <div className="flex justify-center lg:justify-start">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden max-w-sm">
              {currentMovie.tmdb_data?.poster_url ? (
                <img
                  src={currentMovie.tmdb_data.poster_url}
                  alt={currentMovie.epg_data.title}
                  className="w-full h-auto object-contain"
                  style={{ aspectRatio: '2/3', maxHeight: '600px' }}
                />
              ) : currentMovie.epg_data.preview_image ? (
                <img
                  src={currentMovie.epg_data.preview_image}
                  alt={currentMovie.epg_data.title}
                  className="w-full h-auto object-contain"
                  style={{ aspectRatio: '2/3', maxHeight: '600px' }}
                />
              ) : (
                <div 
                  className="w-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center"
                  style={{ aspectRatio: '2/3', maxHeight: '600px' }}
                >
                  <svg className="w-20 h-20 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 4v16l13-8L7 4z" />
                  </svg>
                </div>
              )}
            </div>
          </div>

          {/* Movie Info */}
          <div className="space-y-6">
            {/* Title and Basic Info */}
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
                {currentMovie.epg_data.title}
              </h1>

              <div className="flex flex-wrap items-center gap-6 mb-6">
                {/* Broadcast Time */}
                <div className="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 px-4 py-2 rounded-lg">
                  <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-blue-800 dark:text-blue-300 font-medium">
                    {formatTime(currentMovie.epg_data.broadcast_time)}
                  </span>
                </div>

                {/* Rating */}
                {currentMovie.tmdb_data?.rating && (
                  <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-2 rounded-lg shadow-lg">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                    <span className="font-bold text-lg">
                      {currentMovie.tmdb_data.rating.toFixed(1)}
                    </span>
                  </div>
                )}

                {/* Year */}
                {currentMovie.tmdb_data?.year && (
                  <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
                    <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300 font-medium">
                      {currentMovie.tmdb_data.year}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Genres */}
            {currentMovie.tmdb_data?.genres && currentMovie.tmdb_data.genres.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Жанры</h3>
                <div className="flex flex-wrap gap-2">
                  {currentMovie.tmdb_data.genres.map((genre: string, index: number) => (
                    <span
                      key={index}
                      className="px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/50 dark:to-purple-900/50 text-blue-800 dark:text-blue-200 text-sm rounded-full font-medium border border-blue-200 dark:border-blue-700"
                    >
                      {genre}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Описание</h3>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                  {currentMovie.epg_data.description || currentMovie.tmdb_data?.description || 'Описание недоступно'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Related Movies Carousel */}
        <div className="mt-16">
          <MovieCarousel
            title={getCarouselTitle()}
            movies={sameDayMovies}
            onMovieClick={handleMovieClick}
          />
        </div>
      </div>
    </div>
  );
}
