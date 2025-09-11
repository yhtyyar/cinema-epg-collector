import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { fetchMovie, fetchMovies, fetchGenres } from '../services/api';
import { Movie, PagedResponse, Genre } from '../types/movie';
import { QUERY_KEYS, DEFAULTS } from '../lib/constants';
import { ApiError } from '../lib/errors';

interface UseMoviesParams {
  page?: number;
  size?: number;
  genre?: string | number;
  year?: string | number;
  rating?: string | number;
  q?: string;
}

/**
 * Хук для получения списка фильмов с поддержкой фильтрации, поиска и пагинации
 * Использует React Query для кэширования и оптимизации запросов
 */
export function useMovies(
  params: UseMoviesParams,
  options?: UseQueryOptions<PagedResponse<Movie>, ApiError>
) {
  return useQuery<PagedResponse<Movie>, ApiError>({
    queryKey: [QUERY_KEYS.MOVIES, params],
    queryFn: ({ signal }) => fetchMovies(params, signal),
    // Сохраняем предыдущие данные при загрузке новых для плавного UX
    placeholderData: (prev) => prev,
    // Кэшируем данные на 5 минут
    staleTime: DEFAULTS.CACHE_TIMES.MOVIES,
    // Повторяем запрос при ошибке максимум 2 раза
    retry: 2,
    ...options
  });
}

interface UseMovieParams {
  id: string;
  enabled?: boolean;
}

/**
 * Хук для получения детальной информации о конкретном фильме
 */
export function useMovie(
  { id, enabled = true }: UseMovieParams,
  options?: UseQueryOptions<Movie, ApiError>
) {
  return useQuery<Movie, ApiError>({
    queryKey: [QUERY_KEYS.MOVIE, id],
    queryFn: ({ signal }) => fetchMovie(id, signal),
    // Запрос выполняется только если передан валидный ID и enabled=true
    enabled: !!id && id.trim() !== '' && enabled,
    // Кэшируем данные фильма на 10 минут (они меняются реже)
    staleTime: DEFAULTS.CACHE_TIMES.MOVIE,
    retry: 2,
    ...options
  });
}

/**
 * Хук для получения списка всех доступных жанров
 * Используется для формирования фильтров
 */
export function useGenres(
  options?: UseQueryOptions<Genre[], ApiError>
) {
  return useQuery<Genre[], ApiError>({
    queryKey: [QUERY_KEYS.GENRES],
    queryFn: ({ signal }) => fetchGenres(signal),
    // Жанры кэшируем на 30 минут (они меняются очень редко)
    staleTime: DEFAULTS.CACHE_TIMES.GENRES,
    // Данные считаем свежими в течение часа (gcTime в новых версиях React Query)
    gcTime: 60 * 60 * 1000,
    retry: 1,
    ...options
  });
}