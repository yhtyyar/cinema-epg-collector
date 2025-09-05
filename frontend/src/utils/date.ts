import type { Movie } from '../types/movie'

function startOfDay(d: Date) {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x
}

function dateKey(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function parseBroadcastTime(s?: string): Date | null {
  if (!s) return null
  // Пытаемся распарсить ISO/обычную дату
  const d = new Date(s)
  if (isNaN(d.getTime())) return null
  return d
}

export type MovieDaySection = {
  key: string
  label: string
  date: Date | null
  items: Movie[]
}

export function getDayLabel(target: Date | null, now = new Date()): string {
  if (!target) return 'Без даты'
  const t = startOfDay(target).getTime()
  const n = startOfDay(now).getTime()
  const one = 24 * 60 * 60 * 1000
  const diff = Math.round((t - n) / one)
  if (diff === 0) return 'Сегодня'
  if (diff === 1) return 'Завтра'
  if (diff === -1) return 'Вчера'
  return new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'long' }).format(target)
}

export function groupMoviesByDay(movies: Movie[], now = new Date()): MovieDaySection[] {
  const map = new Map<string, MovieDaySection>()

  for (const m of movies) {
    const d = parseBroadcastTime(m.broadcast_time)
    const key = d ? dateKey(d) : 'no-date'
    if (!map.has(key)) {
      map.set(key, {
        key,
        label: getDayLabel(d, now),
        date: d ? startOfDay(d) : null,
        items: []
      })
    }
    map.get(key)!.items.push(m)
  }

  const sections = Array.from(map.values())
  // Сортировка: Сегодня, Завтра, будущие по возрастанию, Вчера, прошлые по убыванию, затем "Без даты"
  const dayDiff = (d: Date | null) => {
    if (!d) return Number.POSITIVE_INFINITY
    const one = 24 * 60 * 60 * 1000
    const t = startOfDay(d).getTime()
    const n = startOfDay(now).getTime()
    return Math.round((t - n) / one)
  }
  const weight = (s: MovieDaySection) => {
    const diff = dayDiff(s.date)
    if (diff === 0) return -100 // Сегодня
    if (diff === 1) return -90  // Завтра
    if (diff > 1) return diff   // Будущее по возрастанию
    if (diff === -1) return 100 // Вчера
    if (diff < -1) return 100 - diff // Чем глубже прошлое, тем дальше
    return Number.POSITIVE_INFINITY  // Без даты в конце
  }
  sections.sort((a, b) => weight(a) - weight(b))

  return sections
}
