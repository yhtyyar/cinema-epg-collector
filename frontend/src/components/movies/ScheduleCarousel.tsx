import { useMemo, useRef } from 'react'
import { formatTimeMSK } from '../../utils/format'

export type ScheduleItem = {
  start?: string // ISO datetime string (optional for suggestion cards)
  label?: string // Custom label override
}

function startOfDay(d: Date) {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  return x
}

function isToday(date: Date) {
  const t = startOfDay(date).getTime()
  const n = startOfDay(new Date()).getTime()
  return t === n
}

function isTomorrow(date: Date) {
  const n = new Date()
  const tomorrow = new Date(n)
  tomorrow.setDate(n.getDate() + 1)
  return startOfDay(date).getTime() === startOfDay(tomorrow).getTime()
}

export default function ScheduleCarousel({ items }: { items: ScheduleItem[] }) {
  const list = useMemo(() => items.slice(), [items])
  const longFmt = useMemo(() => new Intl.DateTimeFormat('ru-RU', { weekday: 'long', day: '2-digit', month: 'long' }), [])
  const scrollerRef = useRef<HTMLDivElement | null>(null)

  const scrollBy = (dx: number) => scrollerRef.current?.scrollBy({ left: dx, behavior: 'smooth' })

  if (list.length === 0) {
    return (
      <div className="mt-4">
        <div className="rounded-md border border-gray-200 dark:border-white/10 p-3 text-sm text-gray-600 dark:text-gray-300">
          Расписание показа неизвестно
        </div>
      </div>
    )
  }

  // Derived logic: if today's items exist but all already passed, append a suggestion for tomorrow
  const now = new Date()
  const sod = (d: Date) => { const x = new Date(d); x.setHours(0,0,0,0); return x }
  const isSameDay = (a: Date, b: Date) => sod(a).getTime() === sod(b).getTime()
  const entries = list.map((it) => {
    const d = it.start ? new Date(it.start) : null
    const today = d ? isSameDay(d, now) : false
    const future = d ? d.getTime() >= now.getTime() : false
    return { it, d, today, future }
  })
  const hasToday = entries.some(e => e.today)
  const hasFutureToday = entries.some(e => e.today && e.future)
  const renderItems: ScheduleItem[] = hasToday && !hasFutureToday
    ? [...list, { label: 'Завтра — можете посмотреть' }]
    : list

  return (
    <section aria-label="Показы" className="mt-4">
      <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-100 mb-2">Показы</h3>
      <div className="relative">
        <div
          ref={scrollerRef}
          className="flex gap-3 overflow-x-auto snap-x snap-mandatory pb-2"
          role="list"
          aria-label="Список ближайших показов"
        >
          {renderItems.map((it, idx) => {
            const d = it.start ? new Date(it.start) : null
            const today = d ? isToday(d) : false
            const tomorrow = d ? isTomorrow(d) : false
            const label = it.label
              ?? (d
                    ? (today
                        ? 'Сегодня ещё можете посмотреть'
                        : tomorrow
                          ? 'Завтра — можете посмотреть'
                          : `${longFmt.format(d)} — можете посмотреть`)
                    : 'Скоро — можете посмотреть')
            const timeStr = it.start ? formatTimeMSK(it.start, true) : undefined
            return (
              <div
                key={idx}
                role="listitem"
                className="shrink-0 snap-start w-[260px] rounded-md border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 p-3"
              >
                <div className="text-xs font-medium text-gray-800 dark:text-gray-100">{label}</div>
                {timeStr && (
                  <div className="mt-1 text-xs text-gray-600 dark:text-gray-300">{timeStr}</div>
                )}
              </div>
            )
          })}
        </div>
        <div className="pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-white dark:from-gray-900 to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-white dark:from-gray-900 to-transparent" />
        <div className="absolute inset-y-0 left-0 flex items-center">
          <button
            type="button"
            aria-label="Прокрутить влево"
            onClick={() => scrollBy(-300)}
            className="pointer-events-auto ml-1 rounded-md border border-gray-200 dark:border-white/10 bg-white/80 dark:bg-gray-800/60 backdrop-blur hover:bg-white dark:hover:bg-gray-800 px-2 py-1 text-xs"
          >
            ←
          </button>
        </div>
        <div className="absolute inset-y-0 right-0 flex items-center">
          <button
            type="button"
            aria-label="Прокрутить вправо"
            onClick={() => scrollBy(300)}
            className="pointer-events-auto mr-1 rounded-md border border-gray-200 dark:border-white/10 bg-white/80 dark:bg-gray-800/60 backdrop-blur hover:bg-white dark:hover:bg-gray-800 px-2 py-1 text-xs"
          >
            →
          </button>
        </div>
      </div>
    </section>
  )
}
