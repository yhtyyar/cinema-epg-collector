// Типы для работы с жанрами фильмов
export type Genre = {
  id: number
  name: string
}

// Тип для опций даты
export type DateOption = {
  date: string
  displayDate: string
  isToday: boolean
  count: number
}

// Основной тип фильма для фронтенда
export type Movie = {
  id: string
  title: string
  original_title?: string
  overview?: string
  year?: number
  rating?: number
  duration?: number
  genres?: Genre[]
  poster_url?: string
  // Дополнительные метаданные из бэкенда
  source?: string
  broadcast_time?: string
  // Возрастной рейтинг фильма
  age_rating?: string
}

// Тип для пагинированного ответа от API
export type PagedResponse<T> = {
  items: T[]
  total: number
  page: number
  size: number
}

// Типы для работы с бэкенд API (соответствуют структуре бэкенда)
export type EPGData = {
  title?: string
  description?: string
  broadcast_time?: string
  preview_image?: string
}

export type TMDBData = {
  title?: string
  original_title?: string
  year?: number
  rating?: number
  description?: string
  poster_url?: string
  genres?: string[]
  duration?: number
}

export type Metadata = {
  created_at?: string
  updated_at?: string
  source?: string
}

// Тип фильма как приходит с бэкенда
export type MovieDTO = {
  id: string
  epg_data: EPGData
  tmdb_data?: TMDBData
  metadata: Metadata
}

// Тип пагинации как приходит с бэкенда
export type PaginationDTO = {
  page: number
  per_page: number
  total: number
  pages: number
}

// Тип ответа списка фильмов с бэкенда
export type MoviesResponseDTO = {
  movies: MovieDTO[]
  pagination: PaginationDTO
}
