import axios from 'axios'
import type { Genre, Movie, PagedResponse } from '../types/movie'

import type { ChannelItem, ChannelsResponse, ChannelData } from '../types/channel'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: { Accept: 'application/json' }
})

// Перехватчики: нормализация ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status ?? 0
    const message = error?.response?.data?.detail || error?.response?.data?.message || error?.message || 'Network error'
    const details = error?.response?.data
    return Promise.reject(Object.assign(new Error(message), { status, details }))
  }
)

// Адаптер фильма из формата бэкенда к фронтовому типу
function adaptMovie(dto: any): Movie {
  const kp = dto?.kinopoisk_data ?? {}
  const epg = dto?.epg_data ?? {}
  const title = kp.title || epg.title || 'Без названия'
  const overview = kp.description || epg.description || ''
  const poster_url = kp.poster_url || epg.preview_image || ''
  const year = kp.year ?? undefined
  const rating = kp.rating ?? undefined
  const duration = kp.duration ?? undefined
  const genresSrc: string[] = Array.isArray(kp.genres) ? kp.genres : []
  const genres: Genre[] = genresSrc.map((name, idx) => ({ id: idx + 1, name }))
  const source: string | undefined = dto?.metadata?.source || undefined
  const broadcast_time: string | undefined = epg?.broadcast_time || undefined
  return {
    id: String(dto?.id ?? ''),
    title,
    original_title: kp.original_title ?? undefined,
    overview,
    year,
    rating,
    duration,
    genres,
    poster_url,
    source,
    broadcast_time,
  }
}

export async function fetchMovies(
  params: { page?: number; size?: number; genre?: number | string; year?: number | string; rating?: number | string; q?: string },
  signal?: AbortSignal
) {
  const { page = 1, size = 20, genre, year, rating, q } = params
  const path = q ? '/movies/search' : '/movies'
  const requestParams = q
    ? { q, page, per_page: size }
    : { page, per_page: size, genre, year, rating_gte: rating }

  const { data } = await api.get<any>(path, { params: requestParams, signal })
  const movies = Array.isArray(data?.movies) ? data.movies.map(adaptMovie) : []
  const pagination = data?.pagination || { total: movies.length, page, per_page: size, pages: 1 }
  const mapped: PagedResponse<Movie> = {
    items: movies,
    total: Number(pagination.total ?? movies.length),
    page: Number(pagination.page ?? page),
    size: Number(pagination.per_page ?? size),
  }
  return mapped
}

export async function fetchMovie(id: string | number, signal?: AbortSignal) {
  const { data } = await api.get<any>(`/movies/${id}`, { signal })
  return adaptMovie(data)
}

export async function fetchGenres(signal?: AbortSignal) {
  try {
    // Получаем расширенную первую страницу и собираем жанры
    const { data } = await api.get<any>('/movies', { params: { page: 1, per_page: 200 }, signal })
    const movies: any[] = Array.isArray(data?.movies) ? data.movies : []
    const set = new Set<string>()
    for (const m of movies) {
      const kpGenres: string[] = m?.kinopoisk_data?.genres || []
      kpGenres.forEach((g) => g && set.add(g))
    }
    const result: Genre[] = Array.from(set).map((name, idx) => ({ id: idx + 1, name }))
    return result
  } catch {
    // Фолбэк: пустой список
    return []
  }
}

// --- Channels (per-channel JSON) ---
export async function fetchMovieChannels(kind: 'movies' | 'cartoons', signal?: AbortSignal) {
  const path = kind === 'movies' ? '/channels/movies' : '/channels/cartoons'
  const { data } = await api.get<ChannelsResponse>(path, { signal })
  const channels: ChannelItem[] = Array.isArray((data as any)?.channels) ? (data as any).channels : []
  return channels
}

export async function fetchChannelData(kind: 'movies' | 'cartoons', channelId: string, signal?: AbortSignal) {
  const path = kind === 'movies' ? `/channels/movies/${channelId}` : `/channels/cartoons/${channelId}`
  const { data } = await api.get<ChannelData>(path, { signal })
  return data
}
