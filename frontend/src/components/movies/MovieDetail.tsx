import type { Movie } from '../../types/movie'
import ResponsivePoster from './ResponsivePoster'
import { formatTimeMSK, readableSource } from '../../utils/format'
import ScheduleCarousel from './ScheduleCarousel'
import { Link } from 'react-router-dom'

export default function MovieDetail({ movie }: { movie: Movie }) {
  const categories = movie.genres ?? []
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
          {typeof movie.rating === 'number' ? (
            <span className={(movie.rating >= 7 ? 'bg-green-600 text-white' : movie.rating >= 5 ? 'bg-amber-500 text-black' : 'bg-red-600 text-white') + ' inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium'}>
              ★ {movie.rating}
            </span>
          ) : (
            <span className={'inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium bg-purple-600 text-white'}>
              16+
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

        {categories.length > 0 && (
          <div className="space-y-1">
            <div className="text-xs text-gray-500">Категории</div>
            <div className="flex gap-2 flex-wrap">
              {categories.map(g => (
                <Link
                  key={g.id}
                  to={`/?genre=${encodeURIComponent(g.name)}`}
                  className="text-xs rounded-full px-2 py-1 bg-gray-200 hover:bg-gray-300 dark:bg-white/10 dark:hover:bg-white/20"
                >
                  {g.name}
                </Link>
              ))}
            </div>
          </div>
        )}

        {movie.overview && <p className="leading-relaxed text-gray-700 dark:text-gray-300">{movie.overview}</p>}

        {/* Карусель расписания показов */}
        <ScheduleCarousel items={movie.broadcast_time ? [{ start: movie.broadcast_time }] : []} />
      </div>
    </div>
  )
}
