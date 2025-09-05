import type { Movie } from '../../types/movie'
import MovieCard from './MovieCard'

export default function MovieGrid({ movies }: { movies: Movie[] }) {
  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
      {movies.map(m => (
        <MovieCard key={m.id} movie={m} />
      ))}
    </div>
  )
}
