import { useParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useMovie } from '../hooks/useMovies'
import ErrorMessage from '../components/common/ErrorMessage'
import MovieDetail from '../components/movies/MovieDetail'
import { SkeletonDetail } from '../components/common/Skeletons'

export default function MovieDetailPage() {
  const { id = '' } = useParams()
  const { data, isLoading, isError } = useMovie(id)

  if (isLoading) return <SkeletonDetail />
  if (isError || !data) return <ErrorMessage message="Фильм не найден" />

  return (
    <div className="space-y-4">
      <Helmet>
        <title>{data.title} · IPTV Movies</title>
        <meta name="description" content={data.overview?.slice(0, 150)} />
      </Helmet>
      <MovieDetail movie={data} />
    </div>
  )
}
