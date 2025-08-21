import { useEffect, useMemo, useState } from 'react'
import Select from '../ui/Select'
import Button from '../ui/Button'
import { useGenres } from '../../hooks/useMovies'

export type Filters = { genre?: string; year?: string; rating?: string }

type Props = {
  initial: Filters
  onApply: (f: Filters) => void
  onReset: () => void
}

export default function MovieFilters({ initial, onApply, onReset }: Props) {
  const { data: genres } = useGenres()
  const [state, setState] = useState<Filters>(initial)

  useEffect(() => setState(initial), [initial])

  const years = useMemo(() => {
    const cur = new Date().getFullYear()
    return Array.from({ length: 60 }, (_, i) => String(cur - i))
  }, [])

  const ratings = ['9', '8', '7', '6', '5']

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-xs mb-1 text-gray-500">Жанр</label>
        <Select value={state.genre ?? ''} onChange={e => setState(s => ({ ...s, genre: e.target.value || undefined }))}>
          <option value="">Любой</option>
          {genres?.map(g => (
            <option key={g.id} value={g.name}>{g.name}</option>
          ))}
        </Select>
      </div>
      <div>
        <label className="block text-xs mb-1 text-gray-500">Год</label>
        <Select value={state.year ?? ''} onChange={e => setState(s => ({ ...s, year: e.target.value || undefined }))}>
          <option value="">Любой</option>
          {years.map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </Select>
      </div>
      <div>
        <label className="block text-xs mb-1 text-gray-500">Рейтинг от</label>
        <Select value={state.rating ?? ''} onChange={e => setState(s => ({ ...s, rating: e.target.value || undefined }))}>
          <option value="">Любой</option>
          {ratings.map(r => (
            <option key={r} value={r}>{r}+</option>
          ))}
        </Select>
      </div>
      <div className="flex gap-2 pt-1">
        <Button onClick={() => onApply(state)} className="flex-1">Применить</Button>
        <Button variant="secondary" onClick={onReset}>Сброс</Button>
      </div>
    </div>
  )
}
