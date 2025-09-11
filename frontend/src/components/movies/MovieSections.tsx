import type { Movie } from '../../types/movie'
import { groupMoviesByDay } from '../../utils/date'
import { MovieCard } from './MovieCard'

import { useEffect, useMemo, useRef, useState } from 'react'

export default function MovieSections({ movies }: { movies: Movie[] }) {
  const sections = groupMoviesByDay(movies)
  const fmt = new Intl.DateTimeFormat('ru-RU', { weekday: 'short', day: '2-digit', month: 'long' })
  const sectionKeys = useMemo(() => sections.map(s => s.key).join(','), [sections])

  // Определяем ключ "Сегодня", если есть, и вычисляем ближайший будущий раздел,
  // если на сегодня показы уже прошли
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const todayKey = useMemo(() => {
    for (const s of sections) {
      if (s.date && s.date.getTime() === startOfToday) return s.key
    }
    return null
  }, [sectionKeys])

  const defaultKey = useMemo(() => {
    const idxByKey: Record<string, number> = {}
    sections.forEach((s, i) => { idxByKey[s.key] = i })
    const hasFutureIn = (s: typeof sections[number]) => s.items.some(m => {
      if (!m.broadcast_time) return false
      const t = new Date(m.broadcast_time).getTime()
      return t >= now.getTime()
    })
    if (todayKey) {
      const todayIdx = idxByKey[todayKey]
      const todaySection = sections[todayIdx]
      if (todaySection && hasFutureIn(todaySection)) return todayKey
      // Ищем ближайшую следующую секцию после сегодня, где есть будущие показы
      for (let i = todayIdx + 1; i < sections.length; i++) {
        const s = sections[i]
        if (!s) continue
        if (s.date && s.date.getTime() >= startOfToday && s.items.length > 0) return s.key
      }
    }
    return todayKey ?? sections[0]?.key ?? null
  }, [sectionKeys])

  const [activeKey, setActiveKey] = useState<string | null>(defaultKey)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>(() => {
    const now = new Date()
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
    const init: Record<string, boolean> = {}
    for (const s of sections) {
      const t = s.date ? new Date(s.date).getTime() : Number.POSITIVE_INFINITY
      init[s.key] = t < startOfToday // прошлые дни сворачиваем
    }
    return init
  })

  // Навигация: проскроллить чип активной секции (сегодня или ближайшая будущая) при первом рендере
  const navRef = useRef<HTMLDivElement | null>(null)
  const firstRender = useRef(true)
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      const targetKey = defaultKey
      if (targetKey && navRef.current) {
        const el = navRef.current.querySelector<HTMLAnchorElement>(`a[href="#section-${targetKey}"]`)
        el?.scrollIntoView({ behavior: 'auto', inline: 'center', block: 'nearest' })
        setActiveKey(targetKey)
        const sec = document.getElementById(`section-${targetKey}`)
        sec?.scrollIntoView({ behavior: 'auto', block: 'start', inline: 'nearest' })
      }
    }
  }, [defaultKey])

  // Обновлять список ключей в collapsed при изменении секций
  useEffect(() => {
    setCollapsed(prev => {
      const now = new Date()
      const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
      const next: Record<string, boolean> = { ...prev }
      for (const s of sections) {
        if (!(s.key in next)) {
          const t = s.date ? new Date(s.date).getTime() : Number.POSITIVE_INFINITY
          next[s.key] = t < startOfToday
        }
      }
      return next
    })
  }, [sectionKeys])

  // Scroll spy: подсвечиваем активную дату в навигации
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const id = (entry.target as HTMLElement).id
        if (entry.isIntersecting && id?.startsWith('section-')) {
          const key = id.replace('section-', '')
          setActiveKey(key)
        }
      })
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 })

    const els = Array.from(document.querySelectorAll('section[id^="section-"]'))
    els.forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [sectionKeys])

  return (
    <div className="space-y-6">
      {/* Навигация по датам */}
      {sections.length > 1 && (
        <nav aria-label="Навигация по датам" className="-mt-1">
          <div ref={navRef} className="flex gap-2 overflow-x-auto pb-1">
            {sections.map((s) => (
              <a
                key={s.key}
                href={`#section-${s.key}`}
                className={
                  'shrink-0 inline-flex items-center gap-2 rounded-md border border-gray-200 dark:border-white/10 px-3 py-1.5 text-xs hover:bg-gray-50 dark:hover:bg-white/10 ' +
                  (activeKey === s.key ? 'bg-gray-900 text-white dark:bg-white/20' : '')
                }
                title={s.date ? fmt.format(s.date) : s.label}
                aria-current={activeKey === s.key ? 'page' : undefined}
              >
                <span className="font-medium">{s.label}</span>
                <span className="text-[10px] text-gray-500 dark:text-gray-400">{s.items.length}</span>
              </a>
            ))}
          </div>
        </nav>
      )}

      {sections.map((s) => {
        const itemsSorted = [...s.items].sort((a, b) => {
          const ta = a.broadcast_time ? new Date(a.broadcast_time).getTime() : Number.POSITIVE_INFINITY
          const tb = b.broadcast_time ? new Date(b.broadcast_time).getTime() : Number.POSITIVE_INFINITY
          return ta - tb
        })
        return (
          <section id={`section-${s.key}`} key={s.key} aria-label={s.label} className="space-y-3 scroll-mt-20">
            <div className="sticky top-16 z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur supports-[backdrop-filter]:bg-white/40 dark:supports-[backdrop-filter]:bg-gray-900/40 rounded-md px-2 py-2">
              <h2 className="flex items-baseline gap-2 text-base font-semibold text-gray-800 dark:text-gray-100">
                <span>{s.label}</span>
                {s.date && (
                  <span className="text-xs font-normal text-gray-500 dark:text-gray-400">{fmt.format(s.date)}</span>
                )}
                <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">{itemsSorted.length} фильмов</span>
                <button
                  className="ml-2 text-xs rounded-md border border-gray-200 dark:border-white/10 px-2 py-0.5 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10"
                  onClick={(e) => { e.preventDefault(); setCollapsed(c => ({ ...c, [s.key]: !c[s.key] })) }}
                  aria-expanded={!collapsed[s.key]}
                  aria-controls={`grid-${s.key}`}
                >
                  {collapsed[s.key] ? 'Развернуть' : 'Свернуть'}
                </button>
              </h2>
            </div>
            {!collapsed[s.key] && (
              <div id={`grid-${s.key}`} className="grid gap-4 sm:gap-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                {itemsSorted.map((m) => (
                  <MovieCard key={m.id} movie={m} />
                ))}
              </div>
            )}
          </section>
        )
      })}
    </div>
  )
}
