import type { Movie } from '../../types/movie'

export default function MovieDetail({ movie }: { movie: Movie }) {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <div className="aspect-[2/3] overflow-hidden rounded-lg border border-gray-200/10 bg-gray-100 dark:bg-white/5">
          {movie.poster_url ? (
            <img src={movie.poster_url} alt={movie.title} className="h-full w-full object-cover" loading="lazy" />
          ) : (
            <div className="h-full w-full flex items-center justify-center text-gray-400">Нет постера</div>
          )}
        </div>
      </div>
      <div className="md:col-span-2 space-y-4">
        <h1 className="text-2xl font-semibold">{movie.title}</h1>
        {movie.original_title && <div className="text-gray-500">{movie.original_title}</div>}
        <div className="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400">
          {movie.year && <span>Год: {movie.year}</span>}
          {movie.rating != null && <span>Рейтинг: ★ {movie.rating}</span>}
          {movie.duration && <span>Длительность: {movie.duration} мин</span>}
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
