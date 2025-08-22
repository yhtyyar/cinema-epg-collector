import type { Movie } from '../../types/movie'
import { groupMoviesByDay } from '../../utils/date'
import MovieCard from './MovieCard'

export default function MovieSections({ movies }: { movies: Movie[] }) {
  const sections = groupMoviesByDay(movies)
  return (
    <div className="space-y-6">
      {sections.map((s) => (
        <section key={s.key} aria-label={s.label} className="space-y-3">
          <h2 className="text-base font-semibold text-gray-800 dark:text-gray-100">
            {s.label}
          </h2>
          <div className="grid gap-4 sm:gap-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {s.items.map((m) => (
              <MovieCard key={m.id} movie={m} />
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
