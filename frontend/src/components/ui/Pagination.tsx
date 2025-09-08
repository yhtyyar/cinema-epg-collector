// Типы пропсов для компонента пагинации
type Props = {
  currentPage: number    // Текущая активная страница
  totalPages: number     // Общее количество страниц
  onPageChange: (page: number) => void  // Колбэк для смены страницы
}

/**
 * Компонент пагинации для навигации по страницам
 * Отображает кнопки для перехода между страницами с современным дизайном
 */
export default function Pagination({ currentPage, totalPages, onPageChange }: Props) {
  // Не показываем пагинацию если страница всего одна
  if (totalPages <= 1) return null
  
  // Функция для создания кнопки страницы
  const createPageButton = (pageNumber: number) => (
    <button
      key={pageNumber}
      onClick={() => onPageChange(pageNumber)}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring ${
        pageNumber === currentPage 
          ? 'text-white' 
          : 'hover:scale-105'
      }`}
      style={{
        background: pageNumber === currentPage 
          ? 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))'
          : 'var(--bg-tertiary)',
        color: pageNumber === currentPage 
          ? 'white'
          : 'var(--text-primary)',
        border: `1px solid ${pageNumber === currentPage ? 'transparent' : 'var(--border-color)'}`
      }}
    >
      {pageNumber}
    </button>
  )
  
  // Генерируем массив кнопок для всех страниц
  const pageButtons: JSX.Element[] = []
  for (let i = 1; i <= totalPages; i++) {
    pageButtons.push(createPageButton(i))
  }
  
  return (
    <div className="flex gap-2 flex-wrap items-center justify-center">
      {/* Кнопка "Предыдущая" */}
      {currentPage > 1 && (
        <button
          onClick={() => onPageChange(currentPage - 1)}
          className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring hover:scale-105"
          style={{
            background: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)'
          }}
        >
          ← Назад
        </button>
      )}
      
      {/* Кнопки страниц */}
      {pageButtons}
      
      {/* Кнопка "Следующая" */}
      {currentPage < totalPages && (
        <button
          onClick={() => onPageChange(currentPage + 1)}
          className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus-ring hover:scale-105"
          style={{
            background: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)'
          }}
        >
          Вперед →
        </button>
      )}
    </div>
  )
}
