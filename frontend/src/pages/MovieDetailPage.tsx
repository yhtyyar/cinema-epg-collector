import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useMovie, useMovies } from '../hooks/useMovies'
import ErrorMessage from '../components/common/ErrorMessage'
import MovieDetail from '../components/movies/MovieDetail'
import MovieCarousel from '../components/movies/MovieCarousel'
import { SkeletonDetail } from '../components/common/Skeletons'

export default function MovieDetailPage() {
  const { id = '' } = useParams()
  const { data: movie, isLoading, isError } = useMovie(id)
  
  // Получаем рекомендации - фильмы того же жанра
  const { data: recommendationsData } = useMovies({
    page: 1,
    size: 12,
    genre: movie?.genres?.[0]?.name
  })

  if (isLoading) return <SkeletonDetail />
  if (isError || !movie) return <ErrorMessage message="Фильм не найден" />

  // Фильтруем рекомендации, исключая текущий фильм
  const recommendations = recommendationsData?.items?.filter(item => item.id !== movie.id) || []

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <Helmet>
        <title>{movie.title} · Cinema EPG</title>
        <meta name="description" content={movie.overview?.slice(0, 150)} />
      </Helmet>
      
      <main className="py-8">
        <div className="container mx-auto px-4 space-y-12">
          {/* Детали фильма */}
          <MovieDetail movie={movie} />
          
          {/* Рекомендации */}
          {recommendations.length > 0 && (
            <MovieCarousel
              movies={recommendations}
              title={`Похожие фильмы ${movie.genres?.[0]?.name ? `в жанре "${movie.genres[0].name}"` : ''}`}
              className="mt-16"
            />
          )}
        </div>
      </main>
    </div>
  )
}
