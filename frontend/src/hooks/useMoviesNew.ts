// hooks/useMoviesNew.ts
import { useState, useEffect, useCallback } from 'react';
import { Movie, MoviesByDate, DateOption } from '../types/movie-new';

const API_BASE_URL = import.meta.env.DEV
  ? 'http://localhost:8000/api'
  : '/api';

export const useMovies = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMovies = useCallback(async (page = 1, perPage = 100) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_BASE_URL}/movies?page=${page}&per_page=${perPage}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMovies(data.movies);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  return { movies, loading, error, refetch: fetchMovies };
};

export const useMoviesByDate = (movies: Movie[]) => {
  const [moviesByDate, setMoviesByDate] = useState<MoviesByDate>({});
  const [dateOptions, setDateOptions] = useState<DateOption[]>([]);

  useEffect(() => {
    const grouped = movies.reduce((acc, movie) => {
      const date = movie.epg_data.broadcast_time.split('T')[0];
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(movie);
      return acc;
    }, {} as MoviesByDate);

    // Sort movies within each date by broadcast time
    Object.keys(grouped).forEach(date => {
      grouped[date].sort((a, b) =>
        a.epg_data.broadcast_time.localeCompare(b.epg_data.broadcast_time)
      );
    });

    setMoviesByDate(grouped);

    // Create date options
    const today = new Date().toISOString().split('T')[0];
    const options: DateOption[] = Object.keys(grouped)
      .sort()
      .map(date => ({
        date,
        displayDate: formatDate(date),
        isToday: date === today,
        count: grouped[date].length
      }));

    setDateOptions(options);
  }, [movies]);

  return { moviesByDate, dateOptions };
};

const formatDate = (dateString: string): string => {
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
