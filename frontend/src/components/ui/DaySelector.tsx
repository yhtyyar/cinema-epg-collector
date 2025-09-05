import { useState, useRef, useEffect, useMemo } from 'react'
import { getDayLabel } from '../../utils/date'

// Тип для элемента выбора дня
export type DayOption = {
  key: string
  label: string
  date: Date | null
  count?: number  // Количество фильмов в этот день
}

// Пропсы компонента селектора дня
type Props = {
  options: DayOption[]
  selectedKey: string
  onSelect: (key: string) => void
  className?: string
}

/**
 * Компонент выпадающего меню для выбора дня просмотра фильмов
 * Сегодня по центру, прошлые даты сверху, будущие снизу
 */
export default function DaySelector({ options, selectedKey, onSelect, className = '' }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  // Сортируем опции: прошлые -> сегодня -> будущие
  const sortedOptions = useMemo(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    return [...options].sort((a, b) => {
      if (!a.date || !b.date) return 0
      
      const aDate = new Date(a.date)
      const bDate = new Date(b.date)
      aDate.setHours(0, 0, 0, 0)
      bDate.setHours(0, 0, 0, 0)
      
      const aDiff = aDate.getTime() - today.getTime()
      const bDiff = bDate.getTime() - today.getTime()
      
      // Сегодня всегда в центре
      if (Math.abs(aDiff) < 86400000 && Math.abs(bDiff) >= 86400000) return -1
      if (Math.abs(bDiff) < 86400000 && Math.abs(aDiff) >= 86400000) return 1
      
      return aDiff - bDiff
    })
  }, [options])

  // Находим выбранный элемент
  const selectedOption = sortedOptions.find(opt => opt.key === selectedKey) || sortedOptions[0]

  // Закрываем меню при клике вне его
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Обработчик выбора дня
  const handleSelect = (key: string) => {
    onSelect(key)
    setIsOpen(false)
  }

  // Центрируем список на сегодняшней дате при открытии
  useEffect(() => {
    if (isOpen && listRef.current) {
      const todayIndex = sortedOptions.findIndex(option => option.label === 'Сегодня')
      if (todayIndex !== -1) {
        const itemHeight = 60 // Примерная высота элемента
        const containerHeight = listRef.current.clientHeight
        const scrollTop = (todayIndex * itemHeight) - (containerHeight / 2) + (itemHeight / 2)
        listRef.current.scrollTop = Math.max(0, scrollTop)
      }
    }
  }, [isOpen, sortedOptions])

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Кнопка открытия меню */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full px-4 py-3 rounded-lg text-left focus-ring transition-all duration-200 hover:scale-[1.02]"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          color: 'var(--text-primary)'
        }}
      >
        <div className="flex items-center space-x-3">
          {/* Иконка календаря */}
          <svg className="w-5 h-5" style={{ color: 'var(--accent-primary)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          
          <div>
            <div className="font-medium">{selectedOption?.label || 'Выберите день'}</div>
            {selectedOption?.count !== undefined && (
              <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {selectedOption.count} фильмов
              </div>
            )}
          </div>
        </div>

        {/* Стрелка */}
        <svg 
          className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          style={{ color: 'var(--text-muted)' }}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Выпадающее меню */}
      {isOpen && (
        <div 
          className="absolute top-full left-0 right-0 mt-2 rounded-lg shadow-xl z-50 backdrop-blur overflow-hidden"
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
          }}
        >
          <div ref={listRef} className="max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent">
            {sortedOptions.map((option, index) => {
              const isToday = option.label === 'Сегодня'
              const isSelected = option.key === selectedKey
              
              return (
                <button
                  key={option.key}
                  onClick={() => handleSelect(option.key)}
                  className={`w-full px-4 py-4 text-left transition-all duration-200 flex items-center justify-between hover:scale-[1.01] relative ${
                    isSelected ? 'font-medium' : ''
                  } ${isToday ? 'border-l-4' : ''}`}
                  style={{
                    background: isSelected 
                      ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))' 
                      : isToday
                      ? 'var(--bg-tertiary)'
                      : 'transparent',
                    color: isSelected 
                      ? 'white' 
                      : 'var(--text-primary)',
                    borderLeftColor: isToday ? 'var(--accent-primary)' : 'transparent'
                  }}
                >
                  <div className="flex items-center space-x-3">
                    {/* Индикатор и иконка */}
                    <div className="flex items-center justify-center w-8 h-8 rounded-full" 
                         style={{ 
                           background: isToday 
                             ? 'var(--accent-primary)' 
                             : isSelected
                             ? 'rgba(255, 255, 255, 0.2)'
                             : 'var(--bg-secondary)'
                         }}>
                      {isToday ? (
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                      ) : (
                        <div className="w-2 h-2 rounded-full" 
                             style={{ background: isSelected ? 'white' : 'var(--text-muted)' }} />
                      )}
                    </div>
                    
                    <div>
                      <div className="font-medium">{option.label}</div>
                      {option.date && (
                        <div className="text-xs opacity-70">
                          {option.date.toLocaleDateString('ru-RU', { 
                            weekday: 'long',
                            day: 'numeric',
                            month: 'long'
                          })}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Количество фильмов */}
                  {option.count !== undefined && (
                    <div 
                      className="text-xs px-3 py-1.5 rounded-full font-medium"
                      style={{
                        background: isSelected 
                          ? 'rgba(255, 255, 255, 0.25)' 
                          : isToday
                          ? 'var(--accent-primary)'
                          : 'var(--bg-tertiary)',
                        color: isSelected || isToday
                          ? 'white' 
                          : 'var(--text-secondary)'
                      }}
                    >
                      {option.count}
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
