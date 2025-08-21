import { useTheme } from '../../context/ThemeContext'

export default function ThemeToggle() {
  const { theme, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      className="inline-flex items-center gap-2 rounded-md border border-gray-200/10 px-3 py-2 text-sm hover:bg-gray-100/50 dark:hover:bg-white/5 transition"
      aria-label="Переключить тему"
      title="Переключить тему"
    >
      <span className="i">{theme === 'dark' ? '🌙' : '🌞'}</span>
      <span className="hidden sm:inline">{theme === 'dark' ? 'Тёмная' : 'Светлая'}</span>
    </button>
  )
}
