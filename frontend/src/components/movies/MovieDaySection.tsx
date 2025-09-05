import type { MovieDaySection as MovieDaySectionType } from '../../utils/date'
import MovieGrid from './MovieGrid'

// Пропсы компонента секции дня
type Props = {
  section: MovieDaySectionType
  className?: string
}

/**
 * Компонент для отображения фильмов одного дня
 * Показывает заголовок дня и сетку фильмов
 */
export default function MovieDaySection({ section, className = '' }: Props) {
  if (!section.items.length) return null

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Заголовок дня */}
      <div className="flex items-center space-x-4">
        <h2 className="text-2xl font-bold gradient-text">
          {section.label}
        </h2>
        
        {/* Количество фильмов */}
        <div 
          className="px-3 py-1 rounded-full text-sm font-medium"
          style={{
            background: 'var(--bg-tertiary)',
            color: 'var(--accent-primary)',
            border: '1px solid var(--border-color)'
          }}
        >
          {section.items.length} фильмов
        </div>

        {/* Дата */}
        {section.date && (
          <div 
            className="text-sm"
            style={{ color: 'var(--text-secondary)' }}
          >
            {section.date.toLocaleDateString('ru-RU', { 
              weekday: 'long',
              day: 'numeric',
              month: 'long'
            })}
          </div>
        )}
      </div>

      {/* Сетка фильмов */}
      <MovieGrid movies={section.items} />
    </div>
  )
}
