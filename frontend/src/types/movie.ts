export type Genre = { id: number; name: string }

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
  // Доп. метаданные из backend
  source?: string
  broadcast_time?: string
}

export type PagedResponse<T> = {
  items: T[]
  total: number
  page: number
  size: number
}
