import type { Movie } from '../../types/movie'
import MovieCard from './MovieCard'

export default function MovieGrid({ movies }: { movies: Movie[] }) {
  return (
    <div className="grid gap-4 sm:gap-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {movies.map(m => (
        <MovieCard key={m.id} movie={m} />
      ))}
    </div>
  )
}
