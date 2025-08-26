// Базовые типы для API ответов
export interface ApiResponse<T = any> {
  data?: T
  error?: string
  message?: string
}

// Типы для пагинации
export interface PaginationInfo {
  page: number
  per_page: number
  total: number
  pages: number
}

// Расширенные типы для фильмов
export interface MovieEpgData {
  title?: string
  description?: string
  preview_image?: string
  broadcast_time?: string
  channel_id?: string
  start_time?: string
  end_time?: string
}

export interface MovieKinopoiskData {
  title?: string
  original_title?: string
  description?: string
  poster_url?: string
  year?: number
  rating?: number
  duration?: number
  genres?: string[]
  countries?: string[]
  directors?: string[]
  actors?: string[]
}

export interface MovieMetadata {
  source?: 'kinopoisk' | 'tmdb' | 'epg'
  enriched_at?: string
  poster_downloaded?: boolean
  poster_path?: string
}

// Основной тип фильма из API
export interface ApiMovie {
  id: string
  epg_data?: MovieEpgData
  kinopoisk_data?: MovieKinopoiskData
  metadata?: MovieMetadata
}

// Ответ API для списка фильмов
export interface MoviesApiResponse {
  movies: ApiMovie[]
  pagination: PaginationInfo
}

// Типы для каналов
export interface ApiChannelItem {
  id: string
  count: number
  name?: string
}

export interface ApiChannelsResponse {
  channels: ApiChannelItem[]
}

export interface ApiChannelData {
  our_id: string
  name?: string
  count: number
  items: ApiMovie[]
}

// Типы для статистики
export interface ApiStats {
  total_movies: number
  movies_channels: number
  cartoons_channels: number
  total_channels: number
}

// Параметры запросов
export interface MovieFilters {
  page?: number
  per_page?: number
  genre?: string
  year?: number
  rating_gte?: number
  source?: string
  q?: string
}

export interface SearchParams {
  q: string
  page?: number
  per_page?: number
}

// Типы ошибок API
export interface ApiErrorDetails {
  code?: string
  field?: string
  message?: string
}

export interface ApiErrorResponse {
  detail: string
  errors?: ApiErrorDetails[]
  status_code?: number
}
