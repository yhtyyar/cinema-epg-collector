import { useQuery } from '@tanstack/react-query'
import { fetchMovie, fetchMovies, fetchGenres } from '../services/api'
import type { Movie, PagedResponse, Genre } from '../types/movie'

/**
 * Хук для получения списка фильмов с поддержкой фильтрации, поиска и пагинации
 * Использует React Query для кэширования и оптимизации запросов
 */
export function useMovies(params: { 
  page?: number
  size?: number
  genre?: string | number
  year?: string | number
  rating?: string | number
  q?: string 
}) {
  return useQuery<PagedResponse<Movie>, Error>({
    queryKey: ['movies', params],
    queryFn: ({ signal }) => fetchMovies(params, signal),
    // Сохраняем предыдущие данные при загрузке новых для плавного UX
    placeholderData: (prev) => prev,
    // Кэшируем данные на 5 минут
    staleTime: 5 * 60 * 1000,
    // Повторяем запрос при ошибке максимум 2 раза
    retry: 2
  })
}

/**
 * Хук для получения детальной информации о конкретном фильме
 */
export function useMovie(id: string) {
  return useQuery<Movie, Error>({
    queryKey: ['movie', id],
    queryFn: ({ signal }) => fetchMovie(id, signal),
    // Запрос выполняется только если передан валидный ID
    enabled: !!id && id.trim() !== '',
    // Кэшируем данные фильма на 10 минут (они меняются реже)
    staleTime: 10 * 60 * 1000,
    retry: 2
  })
}

/**
 * Хук для получения списка всех доступных жанров
 * Используется для формирования фильтров
 */
export function useGenres() {
  return useQuery<Genre[], Error>({
    queryKey: ['genres'],
    queryFn: ({ signal }) => fetchGenres(signal),
    // Жанры кэшируем на 30 минут (они меняются очень редко)
    staleTime: 30 * 60 * 1000,
    // Данные считаем свежими в течение часа (gcTime в новых версиях React Query)
    gcTime: 60 * 60 * 1000,
    retry: 1
  })
}
