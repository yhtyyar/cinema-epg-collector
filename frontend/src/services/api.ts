import axios, { AxiosError, AxiosResponse } from 'axios'
import type { Genre, Movie, PagedResponse } from '../types/movie'
import type { ChannelItem, ChannelsResponse, ChannelData } from '../types/channel'

// Правильный baseURL для нашего API
const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api'

// Создаем экземпляр axios с улучшенной конфигурацией
export const api = axios.create({
  baseURL,
  timeout: 30000, // Увеличиваем таймаут для медленных запросов
  headers: { 
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

// Интерфейс для стандартизированных ошибок API
export interface ApiError extends Error {
  status: number
  details?: any
  code?: string
}

// Улучшенный перехватчик ответов с детальной обработкой ошибок
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Логируем успешные запросы в dev режиме
    if (import.meta.env.DEV) {
      console.log(`✅ API Success: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data
      })
    }
    return response
  },
  (error: AxiosError) => {
    const status = error?.response?.status ?? 0
    const responseData = error?.response?.data as any
    
    // Определяем сообщение об ошибке с приоритетом
    let message = 'Произошла ошибка при загрузке данных'
    if (responseData?.detail) {
      message = responseData.detail
    } else if (responseData?.message) {
      message = responseData.message
    } else if (error.message) {
      message = error.message
    }

    // Специфичные сообщения для разных статусов
    switch (status) {
      case 404:
        message = 'Запрашиваемые данные не найдены'
        break
      case 500:
        message = 'Внутренняя ошибка сервера'
        break
      case 503:
        message = 'Сервис временно недоступен'
        break
      case 0:
        message = 'Нет соединения с сервером'
        break
    }

    // Логируем ошибки в dev режиме
    if (import.meta.env.DEV) {
      console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
        status,
        message,
        details: responseData
      })
    }

    const apiError: ApiError = Object.assign(new Error(message), {
      status,
      details: responseData,
      code: responseData?.code
    })

    return Promise.reject(apiError)
  }
)

// Перехватчик запросов для добавления метаданных
api.interceptors.request.use(
  (config) => {
    // Добавляем timestamp для предотвращения кеширования
    if (config.method === 'get') {
      config.params = { ...config.params, _t: Date.now() }
    }
    
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params)
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Утилиты для безопасной работы с данными
const safeString = (value: any, fallback = ''): string => {
  if (typeof value === 'string') return value
  if (value != null) return String(value)
  return fallback
}

const safeNumber = (value: any): number | undefined => {
  if (typeof value === 'number' && !isNaN(value)) return value
  if (typeof value === 'string') {
    const parsed = parseFloat(value)
    return !isNaN(parsed) ? parsed : undefined
  }
  return undefined
}

const safeArray = <T>(value: any): T[] => {
  return Array.isArray(value) ? value : []
}

// Улучшенный адаптер фильма с валидацией и обработкой ошибок
function adaptMovie(dto: any): Movie {
  if (!dto || typeof dto !== 'object') {
    throw new Error('Invalid movie data received from API')
  }

  const kp = dto?.kinopoisk_data ?? {}
  const epg = dto?.epg_data ?? {}
  const metadata = dto?.metadata ?? {}

  // Безопасное извлечение данных с fallback'ами
  const title = safeString(kp.title || epg.title, 'Без названия')
  const overview = safeString(kp.description || epg.description)
  const poster_url = safeString(kp.poster_url || epg.preview_image)
  const original_title = safeString(kp.original_title)
  const year = safeNumber(kp.year)
  const rating = safeNumber(kp.rating)
  const duration = safeNumber(kp.duration)
  const source = safeString(metadata.source)
  const broadcast_time = safeString(epg.broadcast_time)

  // Обработка жанров с валидацией
  const genresSrc = safeArray<string>(kp.genres).filter(g => typeof g === 'string' && g.trim())
  const genres: Genre[] = genresSrc.map((name, idx) => ({ 
    id: idx + 1, 
    name: name.trim() 
  }))

  return {
    id: safeString(dto.id, 'unknown'),
    title,
    original_title: original_title || undefined,
    overview: overview || undefined,
    year,
    rating,
    duration,
    genres,
    poster_url: poster_url || undefined,
    source: source || undefined,
    broadcast_time: broadcast_time || undefined,
  }
}

// Retry логика для устойчивости к сетевым ошибкам
async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries = 3,
  delay = 1000
): Promise<T> {
  let lastError: any
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation()
    } catch (error) {
      lastError = error
      
      // Не ретраим для клиентских ошибок (4xx)
      const status = (error as ApiError)?.status
      if (status >= 400 && status < 500) {
        throw error
      }
      
      if (attempt === maxRetries) {
        throw error
      }
      
      // Экспоненциальная задержка
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)))
    }
  }
  
  throw lastError
}

// Улучшенная функция получения фильмов с валидацией параметров
export async function fetchMovies(
  params: { 
    page?: number
    size?: number
    genre?: number | string
    year?: number | string
    rating?: number | string
    q?: string 
  },
  signal?: AbortSignal
): Promise<PagedResponse<Movie>> {
  return withRetry(async () => {
    // Валидация и нормализация параметров
    const page = Math.max(1, params.page || 1)
    const size = Math.min(200, Math.max(1, params.size || 20))
    const { genre, year, rating, q } = params

    const path = q ? '/movies/search' : '/movies'
    const requestParams = q
      ? { q: q.trim(), page, per_page: size }
      : { 
          page, 
          per_page: size, 
          ...(genre && { genre }),
          ...(year && { year }),
          ...(rating && { rating_gte: rating })
        }

    const { data } = await api.get<any>(path, { params: requestParams, signal })
    
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid response format from API')
    }

    const movies = safeArray(data.movies)
      .map(movie => {
        try {
          return adaptMovie(movie)
        } catch (error) {
          console.warn('Failed to adapt movie:', movie, error)
          return null
        }
      })
      .filter(Boolean) as Movie[]

    const pagination = data.pagination || {}
    
    return {
      items: movies,
      total: safeNumber(pagination.total) || movies.length,
      page: safeNumber(pagination.page) || page,
      size: safeNumber(pagination.per_page) || size,
    }
  })
}

export async function fetchMovie(id: string | number, signal?: AbortSignal): Promise<Movie> {
  if (!id) {
    throw new Error('Movie ID is required')
  }

  return withRetry(async () => {
    const { data } = await api.get<any>(`/movies/${encodeURIComponent(id)}`, { signal })
    return adaptMovie(data)
  })
}

export async function fetchGenres(signal?: AbortSignal): Promise<Genre[]> {
  return withRetry(async () => {
    try {
      const { data } = await api.get<any>('/movies', { 
        params: { page: 1, per_page: 200 }, 
        signal 
      })
      
      const movies = safeArray(data?.movies)
      const genreSet = new Set<string>()
      
      movies.forEach((movie: any) => {
        const genres = safeArray<string>(movie?.kinopoisk_data?.genres)
        genres.forEach(genre => {
          if (typeof genre === 'string' && genre.trim()) {
            genreSet.add(genre.trim())
          }
        })
      })
      
      return Array.from(genreSet)
        .sort()
        .map((name, idx) => ({ id: idx + 1, name }))
    } catch (error) {
      console.warn('Failed to fetch genres:', error)
      return []
    }
  })
}

// Улучшенные функции для работы с каналами
export async function fetchMovieChannels(
  kind: 'movies' | 'cartoons', 
  signal?: AbortSignal
): Promise<ChannelItem[]> {
  return withRetry(async () => {
    const path = kind === 'movies' ? '/channels/movies' : '/channels/cartoons'
    const { data } = await api.get<ChannelsResponse>(path, { signal })
    
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid channels response format')
    }
    
    return safeArray<ChannelItem>(data.channels).filter(channel => 
      channel && typeof channel === 'object' && channel.id
    )
  })
}

export async function fetchChannelData(
  kind: 'movies' | 'cartoons', 
  channelId: string, 
  signal?: AbortSignal
): Promise<ChannelData> {
  if (!channelId) {
    throw new Error('Channel ID is required')
  }

  return withRetry(async () => {
    const path = kind === 'movies' 
      ? `/channels/movies/${encodeURIComponent(channelId)}` 
      : `/channels/cartoons/${encodeURIComponent(channelId)}`
    
    const { data } = await api.get<ChannelData>(path, { signal })
    
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid channel data format')
    }
    
    return data
  })
}
