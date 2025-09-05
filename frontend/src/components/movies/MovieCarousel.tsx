import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import type { Movie } from '../../types/movie'
import ResponsivePoster from './ResponsivePoster'

// Пропсы компонента карусели
type Props = {
  movies: Movie[]
  title: string
  className?: string
}

/**
 * Компонент горизонтальной карусели фильмов с прокруткой
 * Используется для отображения рекомендаций и групп фильмов
 */
export default function MovieCarousel({ movies, title, className = '' }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)

  // Проверяем возможность прокрутки
  const checkScrollability = () => {
    if (!scrollRef.current) return
    
    const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
    setCanScrollLeft(scrollLeft > 0)
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
  }

  // Прокрутка влево
  const scrollLeft = () => {
    if (!scrollRef.current) return
    scrollRef.current.scrollBy({ left: -300, behavior: 'smooth' })
    setTimeout(checkScrollability, 300)
  }

  // Прокрутка вправо
  const scrollRight = () => {
    if (!scrollRef.current) return
    scrollRef.current.scrollBy({ left: 300, behavior: 'smooth' })
    setTimeout(checkScrollability, 300)
  }

  // Получение возрастного рейтинга
  const getAgeRating = (movie: Movie): string => {
    if (movie.age_rating) return movie.age_rating
    // Определяем возрастной рейтинг по рейтингу фильма
    if (movie.rating && movie.rating >= 8) return '12+'
    if (movie.rating && movie.rating >= 6) return '16+'
    return '18+'
  }

  if (!movies.length) return null

  return (
    <div className={`${className}`}>
      {/* Заголовок секции */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold gradient-text">{title}</h2>
        
        {/* Кнопки навигации */}
        <div className="flex items-center space-x-2">
          <button
            onClick={scrollLeft}
            disabled={!canScrollLeft}
            className={`p-2 rounded-lg transition-all duration-200 focus-ring ${
              canScrollLeft ? 'hover:scale-110' : 'opacity-50 cursor-not-allowed'
            }`}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)'
            }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <button
            onClick={scrollRight}
            disabled={!canScrollRight}
            className={`p-2 rounded-lg transition-all duration-200 focus-ring ${
              canScrollRight ? 'hover:scale-110' : 'opacity-50 cursor-not-allowed'
            }`}
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)'
            }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Карусель фильмов */}
      <div className="relative">
        <div
          ref={scrollRef}
          className="flex space-x-4 overflow-x-auto scrollbar-hide pb-4"
          onScroll={checkScrollability}
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {movies.map((movie) => (
            <Link
              key={movie.id}
              to={`/movie/${movie.id}`}
              className="flex-shrink-0 w-56 group"
            >
              <div className="card-hover rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)' }}>
                {/* Постер фильма */}
                <div className="relative">
                  <div className="relative">
                    <ResponsivePoster
                      src={movie.poster_url}
                      alt={movie.title}
                      className="w-full"
                      priority="normal"
                    >
                      {/* Элегантное позиционирование бейджей */}
                      <div className="flex justify-between items-start">
                        {/* Левый верхний угол - Возрастной рейтинг */}
                        <div 
                          className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg border border-white/20"
                          style={{
                            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.95), rgba(124, 58, 237, 0.95))',
                            color: 'white',
                            backdropFilter: 'blur(12px)'
                          }}
                        >
                          {getAgeRating(movie)}
                        </div>

                        {/* Правый верхний угол - Рейтинг TMDB */}
                        {typeof movie.rating === 'number' && (
                          <div 
                            className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-bold shadow-lg flex items-center gap-1.5 border border-white/20"
                            style={{
                              background: movie.rating >= 7 
                                ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.95), rgba(22, 163, 74, 0.95))' 
                                : movie.rating >= 5 
                                ? 'linear-gradient(135deg, rgba(251, 191, 36, 0.95), rgba(245, 158, 11, 0.95))' 
                                : 'linear-gradient(135deg, rgba(239, 68, 68, 0.95), rgba(220, 38, 38, 0.95))',
                              color: 'white',
                              backdropFilter: 'blur(12px)'
                            }}
                          >
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                            </svg>
                            {movie.rating.toFixed(1)}
                          </div>
                        )}
                      </div>

                      {/* Левый нижний угол - Время показа */}
                      {movie.broadcast_time && (
                        <div className="absolute bottom-3 left-3">
                          <div 
                            className="backdrop-blur px-3 py-1.5 rounded-lg text-xs font-semibold shadow-lg"
                            style={{
                              background: 'rgba(0, 0, 0, 0.9)',
                              color: 'white',
                              backdropFilter: 'blur(8px)'
                            }}
                          >
                            {new Date(movie.broadcast_time).toLocaleTimeString('ru-RU', { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </div>
                        </div>
                      )}
                    </ResponsivePoster>
                  </div>
                </div>

                {/* Информация о фильме */}
                <div className="p-4 space-y-3">
                  <h3 
                    className="font-bold text-base leading-tight line-clamp-2 group-hover:gradient-text transition-all duration-200"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {movie.title}
                  </h3>
                  
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span style={{ color: 'var(--text-secondary)' }}>
                        {movie.year || '—'}
                      </span>
                      {movie.duration && (
                        <>
                          <span style={{ color: 'var(--text-muted)' }}>•</span>
                          <span style={{ color: 'var(--text-secondary)' }}>
                            {movie.duration} мин
                          </span>
                        </>
                      )}
                    </div>
                    
                    {movie.genres && movie.genres.length > 0 && (
                      <span 
                        className="px-2.5 py-1 rounded-full text-xs font-medium"
                        style={{
                          background: 'linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary))',
                          color: 'var(--accent-primary)',
                          border: '1px solid var(--border-color)'
                        }}
                      >
                        {movie.genres[0].name}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Градиенты для плавного перехода */}
        <div 
          className="absolute left-0 top-0 bottom-0 w-8 pointer-events-none"
          style={{
            background: `linear-gradient(to right, var(--bg-primary), transparent)`
          }}
        />
        <div 
          className="absolute right-0 top-0 bottom-0 w-8 pointer-events-none"
          style={{
            background: `linear-gradient(to left, var(--bg-primary), transparent)`
          }}
        />
      </div>
    </div>
  )
}
