import type { Movie } from '../../types/movie'
import ResponsivePoster from './ResponsivePoster'
import { formatTimeMSK, readableSource } from '../../utils/format'

export default function MovieDetail({ movie }: { movie: Movie }) {
  const category = movie.genres && movie.genres.length > 0 ? movie.genres[0].name : undefined
  const timeStr = formatTimeMSK(movie.broadcast_time, true)
  const sourceLabel = readableSource(movie.source)
  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <ResponsivePoster src={movie.poster_url} alt={movie.title} />
      </div>
      <div className="md:col-span-2 space-y-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">{movie.title}</h1>
          {movie.original_title && <div className="text-gray-500">{movie.original_title}</div>}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {typeof movie.rating === 'number' && (
            <span className={(movie.rating >= 7 ? 'bg-green-600 text-white' : movie.rating >= 5 ? 'bg-amber-500 text-black' : 'bg-red-600 text-white') + ' inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium'}>
              ★ {movie.rating}
            </span>
          )}
          {category && (
            <span className="inline-block rounded-full bg-gray-200 dark:bg-white/10 px-2 py-0.5 text-xs text-gray-700 dark:text-gray-300">
              Категория: {category}
            </span>
          )}
          {movie.duration && (
            <span className="text-xs text-gray-600 dark:text-gray-400">Длительность: {movie.duration} мин</span>
          )}
          {movie.year && (
            <span className="text-xs text-gray-600 dark:text-gray-400">Год: {movie.year}</span>
          )}
          {sourceLabel && (
            <span className="text-xs rounded-md bg-blue-600/10 text-blue-700 dark:text-blue-300 px-2 py-0.5">Источник: {sourceLabel}</span>
          )}
          {timeStr && (
            <span className="text-xs text-gray-600 dark:text-gray-400">В эфире: {timeStr}</span>
          )}
        </div>

        {movie.genres && movie.genres.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            {movie.genres.map(g => (
              <span key={g.id} className="text-xs rounded-full px-2 py-1 bg-gray-200 dark:bg-white/10">{g.name}</span>
            ))}
          </div>
        )}

        {movie.overview && <p className="leading-relaxed text-gray-700 dark:text-gray-300">{movie.overview}</p>}
      </div>
    </div>
  )
}
