export function formatTimeMSK(ts?: string, withDate = false): string | undefined {
  if (!ts) return undefined
  const d = new Date(ts)
  if (Number.isNaN(d.getTime())) return undefined
  const opts: Intl.DateTimeFormatOptions = withDate
    ? { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Europe/Moscow' }
    : { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Europe/Moscow' }
  const formatted = new Intl.DateTimeFormat('ru-RU', opts).format(d)
  return `${formatted} МСК`
}

export function readableSource(src?: string): string | undefined {
  if (!src) return undefined
  if (src === 'enriched') return undefined
  if (src === 'kinopoisk') return 'Кинопоиск'
  if (src === 'tmdb') return 'TMDB'
  if (src === 'preview') return 'Превью'
  return src
}
