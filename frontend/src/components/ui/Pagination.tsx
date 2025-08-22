type Props = {
  page: number
  pages: number
  onChange: (page: number) => void
}

export default function Pagination({ page, pages, onChange }: Props) {
  if (pages <= 1) return null
  const pg = (p: number) => (
    <button
      key={p}
      onClick={() => onChange(p)}
      className={`px-3 py-1 rounded-md border text-sm ${p === page ? 'bg-accent text-white' : 'hover:bg-gray-100 dark:hover:bg-white/10 border-gray-300 dark:border-white/10'}`}
    >
      {p}
    </button>
  )
  const items = [] as JSX.Element[]
  for (let i = 1; i <= pages; i++) items.push(pg(i))
  return <div className="flex gap-2 flex-wrap items-center">{items}</div>
}
