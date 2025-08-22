import { Link } from 'react-router-dom'
import type { Movie } from '../../types/movie'
import ResponsivePoster from './ResponsivePoster'
import { formatTimeMSK } from '../../utils/format'

export default function MovieCard({ movie }: { movie: Movie }) {
  const timeStr = formatTimeMSK(movie.broadcast_time)
  return (
    <Link to={`/movie/${movie.id}`} className="group rounded-lg overflow-hidden border border-gray-200 dark:border-white/10 hover:shadow-soft transition bg-white dark:bg-white/5">
      <ResponsivePoster src={movie.poster_url} alt={movie.title}>
        {/* Rating badge */}
        {typeof movie.rating === 'number' && (
          <div className="ml-auto">
            <span
              className={
                'pointer-events-auto inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium shadow ' +
                (movie.rating >= 7 ? 'bg-green-600 text-white' : movie.rating >= 5 ? 'bg-amber-500 text-black' : 'bg-red-600 text-white')
              }
              title="Рейтинг"
            >
              ★ {movie.rating}
            </span>
          </div>
        )}
        {/* Broadcast time overlay (bottom-left) */}
        {timeStr && (
          <>
            <div className="absolute inset-x-0 bottom-0 h-14 bg-gradient-to-t from-black/60 to-transparent rounded-md" />
            <div className="absolute left-2 bottom-2">
              <span className="inline-block rounded-md bg-black/60 text-white px-2 py-0.5 text-xs">
                {timeStr}
              </span>
            </div>
          </>
        )}
      </ResponsivePoster>
      <div className="p-3 space-y-1">
        <div className="font-medium leading-tight line-clamp-2 group-hover:text-accent transition-colors">{movie.title}</div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{movie.year ?? '—'}</span>
          {movie.genres && movie.genres.length > 0 && (
            <span className="inline-block rounded-full bg-gray-200 dark:bg-white/10 px-2 py-0.5 text-[10px] text-gray-700 dark:text-gray-300">
              {movie.genres[0].name}
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}
