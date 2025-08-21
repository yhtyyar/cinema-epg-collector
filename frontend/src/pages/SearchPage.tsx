import { useSearchParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useMovies } from '../hooks/useMovies'
import MovieGrid from '../components/movies/MovieGrid'
import ErrorMessage from '../components/common/ErrorMessage'
import { SkeletonGrid } from '../components/common/Skeletons'
import Pagination from '../components/ui/Pagination'
import { useMemo } from 'react'

export default function SearchPage() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') || ''
  const page = Number(params.get('page') || '1')
  const size = 20

  const { data, isLoading, isError, error } = useMovies({ page, size, q })

  const totalPages = useMemo(() => {
    if (!data) return 1
    return Math.max(1, Math.ceil(data.total / data.size))
  }, [data])

  function updatePage(p: number) {
    const next = new URLSearchParams(params)
    next.set('page', String(p))
    setParams(next)
  }

  return (
    <div className="space-y-4">
      <Helmet>
        <title>Поиск: {q} · IPTV Movies</title>
      </Helmet>
      {isLoading && <SkeletonGrid count={12} />}
      {isError && <ErrorMessage message={(error as Error)?.message} />}
      {data && (
        <>
          <MovieGrid movies={data.items} />
          <div className="flex items-center justify-center pt-4">
            <Pagination page={page} pages={totalPages} onChange={updatePage} />
          </div>
        </>
      )}
      {data && data.items.length === 0 && !isLoading && !isError && (
        <div className="text-center text-sm text-gray-500">Ничего не найдено по запросу “{q}”.</div>
      )}
    </div>
  )
}
