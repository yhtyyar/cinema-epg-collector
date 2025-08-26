import { useState, useEffect, useCallback, useRef } from 'react'
import type { ApiError } from '../services/api'

/**
 * Состояние для асинхронных операций
 */
export interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

/**
 * Хук для работы с асинхронными API вызовами
 */
export function useAsync<T>(
  asyncFunction: (signal: AbortSignal) => Promise<T>,
  dependencies: any[] = []
): AsyncState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const execute = useCallback(async () => {
    // Отменяем предыдущий запрос
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Создаем новый контроллер отмены
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal

    setLoading(true)
    setError(null)

    try {
      const result = await asyncFunction(signal)
      
      // Проверяем, не был ли запрос отменен
      if (!signal.aborted) {
        setData(result)
      }
    } catch (err) {
      if (!signal.aborted) {
        const apiError = err as ApiError
        setError(apiError.message || 'Произошла ошибка')
        console.error('API Error:', apiError)
      }
    } finally {
      if (!signal.aborted) {
        setLoading(false)
      }
    }
  }, dependencies)

  useEffect(() => {
    execute()

    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [execute])

  const refetch = useCallback(async () => {
    await execute()
  }, [execute])

  return { data, loading, error, refetch }
}

/**
 * Хук для ленивых API вызовов (вызываются вручную)
 */
export function useLazyAsync<T, Args extends any[]>(
  asyncFunction: (signal: AbortSignal, ...args: Args) => Promise<T>
): [
  (...args: Args) => Promise<T | null>,
  AsyncState<T>
] {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const execute = useCallback(async (...args: Args): Promise<T | null> => {
    // Отменяем предыдущий запрос
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Создаем новый контроллер отмены
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal

    setLoading(true)
    setError(null)

    try {
      const result = await asyncFunction(signal, ...args)
      
      if (!signal.aborted) {
        setData(result)
        return result
      }
      return null
    } catch (err) {
      if (!signal.aborted) {
        const apiError = err as ApiError
        setError(apiError.message || 'Произошла ошибка')
        console.error('API Error:', apiError)
      }
      return null
    } finally {
      if (!signal.aborted) {
        setLoading(false)
      }
    }
  }, [asyncFunction])

  const refetch = useCallback(async (): Promise<void> => {
    // Для ленивых хуков refetch не имеет смысла без аргументов
    return
  }, [])

  return [execute, { data, loading, error, refetch }]
}

/**
 * Хук для работы с пагинированными данными
 */
export interface PaginatedState<T> extends AsyncState<T[]> {
  page: number
  totalPages: number
  total: number
  hasNextPage: boolean
  hasPrevPage: boolean
  nextPage: () => void
  prevPage: () => void
  goToPage: (page: number) => void
}

export function usePaginated<T>(
  asyncFunction: (page: number, signal: AbortSignal) => Promise<{
    items: T[]
    total: number
    page: number
    size: number
  }>,
  initialPage = 1
): PaginatedState<T> {
  const [page, setPage] = useState(initialPage)
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)

  const { data, loading, error, refetch } = useAsync(
    async (signal) => {
      const result = await asyncFunction(page, signal)
      setTotal(result.total)
      setTotalPages(Math.ceil(result.total / result.size))
      return result.items
    },
    [page]
  )

  const nextPage = useCallback(() => {
    if (page < totalPages) {
      setPage(prev => prev + 1)
    }
  }, [page, totalPages])

  const prevPage = useCallback(() => {
    if (page > 1) {
      setPage(prev => prev - 1)
    }
  }, [page])

  const goToPage = useCallback((newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage)
    }
  }, [totalPages])

  return {
    data: data || [],
    loading,
    error,
    refetch,
    page,
    totalPages,
    total,
    hasNextPage: page < totalPages,
    hasPrevPage: page > 1,
    nextPage,
    prevPage,
    goToPage
  }
}

/**
 * Хук для debounced поиска
 */
export function useDebounced<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
