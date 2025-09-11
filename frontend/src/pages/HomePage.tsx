import { useSearchParams } from 'react-router-dom';
import { useState, useMemo, useEffect, memo } from 'react';
import MovieGrid from '../components/movies/MovieGrid';
import MovieDaySection from '../components/movies/MovieDaySection';
import DaySelector, { type DayOption } from '../components/ui/DaySelector';
import Pagination from '../components/ui/Pagination';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { useMovies } from '../hooks/useMovies';
import { groupMoviesByDay, getDayLabel } from '../utils/date';
import { DEFAULTS } from '../lib/constants';

interface HomePageProps { }

function HomePageComponent({ }: HomePageProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedDayKey, setSelectedDayKey] = useState<string>('');

  const page = parseInt(searchParams.get('page') || '1');
  const genre = searchParams.get('genre') || '';
  const year = searchParams.get('year') || '';
  const rating = searchParams.get('rating') || '';
  const source = searchParams.get('source') || '';
  const q = searchParams.get('q') || '';

  const { data, isLoading, error } = useMovies({
    page,
    size: DEFAULTS.MOVIE_PAGE_SIZE, // Увеличиваем размер для группировки по дням
    genre: genre || undefined,
    year: year ? parseInt(year) : undefined,
    rating: rating ? parseFloat(rating) : undefined,
    q: q || undefined
  });

  // Группируем фильмы по дням
  const daysSections = useMemo(() => {
    if (!data?.items) return [];
    return groupMoviesByDay(data.items);
  }, [data?.items]);

  // Создаем опции для селектора дня
  const dayOptions: DayOption[] = useMemo(() => {
    return daysSections.map(section => ({
      key: section.key,
      label: section.label,
      date: section.date,
      count: section.items.length
    }));
  }, [daysSections]);

  // Находим выбранную секцию
  const selectedSection = useMemo(() => {
    const key = selectedDayKey || daysSections[0]?.key;
    return daysSections.find(section => section.key === key) || daysSections[0];
  }, [daysSections, selectedDayKey]);

  // Устанавливаем сегодняшний день по умолчанию
  useEffect(() => {
    if (daysSections.length > 0 && !selectedDayKey) {
      const todaySection = daysSections.find(s => s.label === 'Сегодня');
      setSelectedDayKey(todaySection?.key || daysSections[0].key);
    }
  }, [daysSections, selectedDayKey]);

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  if (error) {
    return (
      <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
        <main className="py-8">
          <div className="container-responsive">
            <ErrorMessage message={error.message} />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      <main className="py-8">
        <div className="container-responsive">
          {/* Hero Section */}
          <div className="mb-12">
            <div className="text-center mb-8">
              <h1 className="text-4xl md:text-5xl font-bold mb-4 gradient-text">
                Кино программа
              </h1>
              <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
                Откройте для себя лучшие фильмы с подробной информацией и рейтингами
              </p>
            </div>
          </div>

          {/* Content */}
          {isLoading ? (
            <div className="flex justify-center py-20">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <>
              {data?.items && data.items.length > 0 ? (
                <>
                  {/* Группировка по дням и селектор */}
                  {!q && !genre && !year && !rating ? (
                    <>
                      {/* Селектор дня */}
                      <div className="mb-8">
                        <DaySelector
                          options={dayOptions}
                          selectedKey={selectedDayKey || dayOptions[0]?.key || ''}
                          onSelect={setSelectedDayKey}
                          className="max-w-md"
                        />
                      </div>

                      {/* Отображение выбранного дня */}
                      {selectedSection && (
                        <MovieDaySection section={selectedSection} />
                      )}
                    </>
                  ) : (
                    <>
                      {/* Обычный режим с фильтрами */}
                      <div className="mb-6">
                        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          Найдено {data.total || data.items.length} фильмов
                        </p>
                      </div>

                      <MovieGrid movies={data.items} />

                      {data.total > data.size && (
                        <div className="mt-16 flex justify-center">
                          <Pagination
                            currentPage={data.page}
                            totalPages={Math.ceil(data.total / data.size)}
                            onPageChange={handlePageChange}
                          />
                        </div>
                      )}
                    </>
                  )}
                </>
              ) : (
                <div className="text-center py-20">
                  <div className="mb-6">
                    <svg className="w-24 h-24 mx-auto mb-4 opacity-40" style={{ color: 'var(--text-muted)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 4v16l13-8L7 4z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                    Фильмы не найдены
                  </h3>
                  <p style={{ color: 'var(--text-secondary)' }}>
                    Попробуйте изменить параметры поиска или фильтры
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default memo(HomePageComponent);