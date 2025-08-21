import { useQuery } from '@tanstack/react-query'
import { fetchMovie, fetchMovies, fetchGenres } from '../services/api'

export function useMovies(params: { page?: number; size?: number; genre?: string | number; year?: string | number; rating?: string | number; q?: string }) {
  return useQuery({
    queryKey: ['movies', params],
    queryFn: ({ signal }) => fetchMovies(params, signal),
    placeholderData: (prev) => prev
  })
}

export function useMovie(id: string) {
  return useQuery({ queryKey: ['movie', id], queryFn: ({ signal }) => fetchMovie(id, signal), enabled: !!id })
}

export function useGenres() {
  return useQuery({ queryKey: ['genres'], queryFn: ({ signal }) => fetchGenres(signal) })
}
