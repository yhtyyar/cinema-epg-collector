import { useMemo } from 'react'
import { Helmet } from 'react-helmet-async'
import { useSearchParams } from 'react-router-dom'
import { useMovies } from '../hooks/useMovies'
import MovieSections from '../components/movies/MovieSections'
import MovieFilters, { Filters } from '../components/movies/MovieFilters'
import ErrorMessage from '../components/common/ErrorMessage'
import Pagination from '../components/ui/Pagination'
import { SkeletonGrid } from '../components/common/Skeletons'
import Modal from '../components/ui/Modal'
import { useState } from 'react'

export default function HomePage() {
  const [params, setParams] = useSearchParams()
  const page = Number(params.get('page') || '1')
  const size = Number(params.get('size') || '20')
  const genre = params.get('genre') || undefined
  const year = params.get('year') || undefined
  const rating = params.get('rating') || undefined

  const { data, isLoading, isError, error } = useMovies({ page, size, genre, year, rating })
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)

  const totalPages = useMemo(() => {
    if (!data) return 1
    return Math.max(1, Math.ceil(data.total / data.size))
  }, [data])

  function update(k: string, v?: string) {
    const next = new URLSearchParams(params)
    if (v == null || v === '') next.delete(k)
    else next.set(k, v)
    if (k !== 'page') next.set('page', '1')
    setParams(next)
  }

  function applyFilters(f: Filters) {
    update('genre', f.genre)
    update('year', f.year)
    update('rating', f.rating)
    setMobileFiltersOpen(false)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6">
      <Helmet>
        <title>Фильмы · IPTV Movies</title>
        <meta name="description" content="Каталог фильмов IPTV: жанры, рейтинг, год, поиск и пагинация" />
      </Helmet>

      <aside className="hidden lg:block">
        <div className="sticky top-[72px] rounded-lg border border-gray-200 p-4 bg-white dark:bg-white/5">
          <h2 className="font-semibold mb-3">Фильтры</h2>
          <MovieFilters
            initial={{ genre, year, rating }}
            onApply={applyFilters}
            onReset={() => { update('genre'); update('year'); update('rating') }}
          />
        </div>
      </aside>

      <section className="space-y-4">
        {/* Мобильные фильтры кнопка */}
        <div className="lg:hidden flex justify-end">
          <button
            className="rounded-md border border-gray-300 dark:border-white/10 px-3 py-2 text-sm hover:bg-gray-100 dark:hover:bg-white/10"
            onClick={() => setMobileFiltersOpen(true)}
            aria-label="Открыть фильтры"
          >
            Фильтры
          </button>
        </div>

        {isLoading && <SkeletonGrid count={12} />}
        {isError && <ErrorMessage message={(error as Error)?.message} />}
        {data && (
          <>
            <MovieSections movies={data.items} />
            <div className="flex items-center justify-center pt-4">
              <Pagination page={page} pages={totalPages} onChange={(p) => update('page', String(p))} />
            </div>
          </>
        )}
        {data && data.items.length === 0 && !isLoading && !isError && (
          <div className="text-center text-sm text-gray-500">Ничего не найдено. Попробуйте изменить фильтры.</div>
        )}
      </section>

      {/* Мобильное модальное окно фильтров */}
      <Modal open={mobileFiltersOpen} onClose={() => setMobileFiltersOpen(false)} title="Фильтры">
        <MovieFilters
          initial={{ genre, year, rating }}
          onApply={applyFilters}
          onReset={() => { update('genre'); update('year'); update('rating') }}
        />
      </Modal>
    </div>
  )
}
