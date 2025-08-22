import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import Input from '../ui/Input'

export default function Header() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const defaultQ = params.get('q') ?? ''

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    const q = String(form.get('q') || '')
    navigate(q ? `/search?q=${encodeURIComponent(q)}` : '/')
  }

  return (
    <header className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-black/30 bg-white/80 dark:bg-black/40 border-b border-gray-200 dark:border-white/10">
      <div className="container-responsive flex items-center gap-4 py-3">
        <Link to="/" className="font-semibold tracking-tight text-xl">
          IPTV<span className="text-accent">Movies</span>
        </Link>
        <form className="flex-1 hidden sm:flex" onSubmit={onSubmit}>
          <Input name="q" defaultValue={defaultQ} placeholder="Поиск фильмов..." aria-label="Поиск" />
        </form>
        <ThemeToggle />
      </div>
    </header>
  )
}
