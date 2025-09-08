import { useState, useCallback, useRef, useEffect } from 'react'
import { LazyLoadImage } from 'react-lazy-load-image-component'
import 'react-lazy-load-image-component/src/effects/blur.css'

type Props = {
  src?: string
  alt: string
  className?: string
  children?: React.ReactNode // overlay content (e.g. badges)
  priority?: 'high' | 'normal' | 'low'
  showShimmer?: boolean
  fixedAspectRatio?: boolean // принудительно использовать фиксированное соотношение
  aspectRatio?: string // кастомное соотношение сторон
}

export default function ResponsivePoster({ 
  src, 
  alt, 
  className = '', 
  children, 
  priority = 'normal',
  showShimmer = true,
  fixedAspectRatio = false,
  aspectRatio
}: Props) {
  const [naturalDimensions, setNaturalDimensions] = useState<{ width: number; height: number } | null>(null)
  const [error, setError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [imageLoaded, setImageLoaded] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)

  const handleLoad = useCallback((e: any) => {
    try {
      const img: HTMLImageElement | undefined = e?.currentTarget
      if (img && img.naturalWidth && img.naturalHeight) {
        setNaturalDimensions({
          width: img.naturalWidth,
          height: img.naturalHeight
        })
        setImageLoaded(true)
      }
      setIsLoading(false)
    } catch {
      setIsLoading(false)
    }
  }, [])

  const handleError = useCallback(() => {
    setError(true)
    setIsLoading(false)
  }, [])

  // Вычисляем динамическое соотношение сторон
  const getDynamicStyle = () => {
    // Если задано фиксированное соотношение или кастомное
    if (fixedAspectRatio || aspectRatio) {
      return {
        aspectRatio: aspectRatio || '2/3',
        width: '100%'
      }
    }

    // Если изображение загружено, используем его натуральные пропорции
    if (naturalDimensions && imageLoaded) {
      const ratio = naturalDimensions.width / naturalDimensions.height
      return {
        aspectRatio: `${naturalDimensions.width}/${naturalDimensions.height}`,
        width: '100%'
      }
    }

    // Дефолтное соотношение для постеров фильмов
    return {
      aspectRatio: '2/3',
      width: '100%'
    }
  }

  const dynamicStyle = getDynamicStyle()

  return (
    <div className={`relative group ${className}`} ref={containerRef}>
      <div 
        className="w-full rounded-xl overflow-hidden transition-all duration-300 shadow-lg hover:shadow-2xl"
        style={{
          ...dynamicStyle,
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-color)'
        }}
      >
        {src && !error ? (
          <>
            {/* Shimmer loading effect */}
            {isLoading && showShimmer && (
              <div className="absolute inset-0 animate-shimmer rounded-xl" />
            )}
            
            <LazyLoadImage
              src={src}
              alt={alt}
              effect="blur"
              className={`h-full w-full transition-all duration-500 group-hover:scale-[1.02] ${
                isLoading ? 'opacity-0' : 'opacity-100'
              }`}
              style={{
                objectFit: 'contain', // Сохраняем пропорции без обрезки
                background: 'var(--bg-secondary)'
              }}
              onLoad={handleLoad}
              onError={handleError}
              loading={priority === 'high' ? 'eager' : 'lazy'}
            />
          </>
        ) : (
          <div className="h-full w-full flex flex-col items-center justify-center"
               style={{ color: 'var(--text-muted)' }}>
            <div className="p-8 text-center">
              <svg className="w-16 h-16 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} 
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium opacity-50">Постер недоступен</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Overlay content with improved positioning */}
      {children && (
        <div className="pointer-events-none absolute inset-0 flex p-3">
          {children}
        </div>
      )}
      
      {/* Elegant hover effect */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/0 via-transparent to-black/0 group-hover:from-black/5 group-hover:to-black/5 transition-all duration-300 rounded-xl pointer-events-none" />
    </div>
  )
}
