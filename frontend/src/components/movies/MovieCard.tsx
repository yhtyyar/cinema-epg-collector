import { Link } from 'react-router-dom'
import { LazyLoadImage } from 'react-lazy-load-image-component'
import 'react-lazy-load-image-component/src/effects/blur.css'
import type { Movie } from '../../types/movie'

export default function MovieCard({ movie }: { movie: Movie }) {
  return (
    <Link to={`/movie/${movie.id}`} className="group rounded-lg overflow-hidden border border-gray-200/10 hover:shadow-soft transition bg-white/50 dark:bg-white/5">
      <div className="aspect-[2/3] bg-gray-100 dark:bg-white/5">
        {movie.poster_url ? (
          <LazyLoadImage
            src={movie.poster_url}
            alt={movie.title}
            effect="blur"
            className="h-full w-full object-cover"
            onError={(e: any) => {
              // Скрываем сломанное изображение и оставляем плейсхолдер
              if (e?.currentTarget) {
                e.currentTarget.style.display = 'none'
              }
            }}
          />
        ) : (
          <div className="h-full w-full flex items-center justify-center text-gray-400">Нет постера</div>
        )}
      </div>
      <div className="p-3 space-y-1">
        <div className="font-medium leading-tight line-clamp-2 group-hover:text-accent transition-colors">{movie.title}</div>
        <div className="text-xs text-gray-500">
          <span>{movie.year ?? '—'}</span>
          {movie.rating != null && <span className="ml-2">★ {movie.rating}</span>}
        </div>
      </div>
    </Link>
  )
}
