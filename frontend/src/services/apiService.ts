import { api, ApiError } from './api'
import type { 
  MoviesApiResponse, 
  ApiMovie, 
  ApiChannelsResponse, 
  ApiChannelData, 
  ApiStats,
  MovieFilters,
  SearchParams 
} from '../types/api'
import type { Movie, PagedResponse, Genre } from '../types/movie'
import type { ChannelItem, ChannelData } from '../types/channel'

/**
 * Сервисный слой для работы с API
 * Предоставляет типизированные методы для всех операций с данными
 */
export class ApiService {
  
  /**
   * Получение списка фильмов с фильтрацией
   */
  async getMovies(filters: MovieFilters = {}, signal?: AbortSignal): Promise<PagedResponse<Movie>> {
    try {
      const params = this.normalizeMovieFilters(filters)
      const { data } = await api.get<MoviesApiResponse>('/movies', { params, signal })
      
      return this.transformMoviesResponse(data, filters)
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при загрузке фильмов')
    }
  }

  /**
   * Поиск фильмов по запросу
   */
  async searchMovies(searchParams: SearchParams, signal?: AbortSignal): Promise<PagedResponse<Movie>> {
    try {
      const params = {
        q: searchParams.q.trim(),
        page: searchParams.page || 1,
        per_page: searchParams.per_page || 20
      }
      
      const { data } = await api.get<MoviesApiResponse>('/movies/search', { params, signal })
      
      return this.transformMoviesResponse(data, searchParams)
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при поиске фильмов')
    }
  }

  /**
   * Получение конкретного фильма по ID
   */
  async getMovie(id: string, signal?: AbortSignal): Promise<Movie> {
    try {
      const { data } = await api.get<ApiMovie>(`/movies/${encodeURIComponent(id)}`, { signal })
      
      return this.transformMovie(data)
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при загрузке фильма')
    }
  }

  /**
   * Получение списка жанров
   */
  async getGenres(signal?: AbortSignal): Promise<Genre[]> {
    try {
      // Получаем фильмы и извлекаем жанры
      const { data } = await api.get<MoviesApiResponse>('/movies', { 
        params: { page: 1, per_page: 200 }, 
        signal 
      })
      
      const genreSet = new Set<string>()
      
      data.movies.forEach(movie => {
        const genres = movie.kinopoisk_data?.genres || []
        genres.forEach(genre => {
          if (genre && typeof genre === 'string') {
            genreSet.add(genre.trim())
          }
        })
      })
      
      return Array.from(genreSet)
        .sort()
        .map((name, index) => ({ id: index + 1, name }))
    } catch (error) {
      console.warn('Не удалось загрузить жанры:', error)
      return []
    }
  }

  /**
   * Получение каналов по типу
   */
  async getChannels(type: 'movies' | 'cartoons', signal?: AbortSignal): Promise<ChannelItem[]> {
    try {
      const endpoint = type === 'movies' ? '/channels/movies' : '/channels/cartoons'
      const { data } = await api.get<ApiChannelsResponse>(endpoint, { signal })
      
      return data.channels.map(channel => ({
        id: channel.id,
        count: channel.count
      }))
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при загрузке каналов')
    }
  }

  /**
   * Получение данных конкретного канала
   */
  async getChannelData(
    type: 'movies' | 'cartoons', 
    channelId: string, 
    signal?: AbortSignal
  ): Promise<ChannelData> {
    try {
      const endpoint = type === 'movies' 
        ? `/channels/movies/${encodeURIComponent(channelId)}`
        : `/channels/cartoons/${encodeURIComponent(channelId)}`
      
      const { data } = await api.get<ApiChannelData>(endpoint, { signal })
      
      return {
        our_id: data.our_id,
        count: data.count,
        items: data.items.map(movie => this.transformMovie(movie))
      }
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при загрузке данных канала')
    }
  }

  /**
   * Получение статистики
   */
  async getStats(signal?: AbortSignal): Promise<ApiStats> {
    try {
      const { data } = await api.get<ApiStats>('/stats', { signal })
      return data
    } catch (error) {
      throw this.handleApiError(error, 'Ошибка при загрузке статистики')
    }
  }

  /**
   * Проверка здоровья API
   */
  async healthCheck(signal?: AbortSignal): Promise<{ status: string; service: string }> {
    try {
      const { data } = await api.get('/health', { signal })
      return data
    } catch (error) {
      throw this.handleApiError(error, 'API недоступен')
    }
  }

  // Приватные методы для трансформации данных

  private normalizeMovieFilters(filters: MovieFilters): Record<string, any> {
    const params: Record<string, any> = {}
    
    if (filters.page) params.page = Math.max(1, filters.page)
    if (filters.per_page) params.per_page = Math.min(200, Math.max(1, filters.per_page))
    if (filters.genre) params.genre = filters.genre
    if (filters.year) params.year = filters.year
    if (filters.rating_gte) params.rating_gte = filters.rating_gte
    if (filters.source) params.source = filters.source
    if (filters.q) params.q = filters.q.trim()
    
    return params
  }

  private transformMoviesResponse(data: MoviesApiResponse, originalParams: any): PagedResponse<Movie> {
    const movies = data.movies.map(movie => this.transformMovie(movie))
    
    return {
      items: movies,
      total: data.pagination.total,
      page: data.pagination.page,
      size: data.pagination.per_page
    }
  }

  private transformMovie(apiMovie: ApiMovie): Movie {
    const kp = apiMovie.kinopoisk_data || {}
    const epg = apiMovie.epg_data || {}
    const metadata = apiMovie.metadata || {}

    return {
      id: apiMovie.id,
      title: kp.title || epg.title || 'Без названия',
      original_title: kp.original_title,
      overview: kp.description || epg.description,
      year: kp.year,
      rating: kp.rating,
      duration: kp.duration,
      genres: (kp.genres || []).map((name, index) => ({ id: index + 1, name })),
      poster_url: kp.poster_url || epg.preview_image,
      source: metadata.source,
      broadcast_time: epg.broadcast_time
    }
  }

  private handleApiError(error: any, defaultMessage: string): ApiError {
    if (error instanceof Error && 'status' in error) {
      return error as ApiError
    }
    
    const apiError: ApiError = Object.assign(new Error(defaultMessage), {
      status: 500,
      details: error
    })
    
    return apiError
  }
}

// Экспортируем синглтон сервиса
export const apiService = new ApiService()

// Экспортируем отдельные функции для обратной совместимости
export const fetchMovies = (params: any, signal?: AbortSignal) => 
  apiService.getMovies(params, signal)

export const fetchMovie = (id: string, signal?: AbortSignal) => 
  apiService.getMovie(id, signal)

export const fetchGenres = (signal?: AbortSignal) => 
  apiService.getGenres(signal)

export const fetchMovieChannels = (kind: 'movies' | 'cartoons', signal?: AbortSignal) => 
  apiService.getChannels(kind, signal)

export const fetchChannelData = (kind: 'movies' | 'cartoons', channelId: string, signal?: AbortSignal) => 
  apiService.getChannelData(kind, channelId, signal)
