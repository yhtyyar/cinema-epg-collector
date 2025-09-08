import { useState, useCallback, useRef, useEffect } from 'react'
import { LazyLoadImage } from 'react-lazy-load-image-component'
import 'react-lazy-load-image-component/src/effects/blur.css'

interface PosterImageProps {
  src?: string
  alt: string
  className?: string
  priority?: 'high' | 'normal' | 'low'
  showShimmer?: boolean
  onLoad?: () => void
  onError?: () => void
}

export default function PosterImage({ 
  src, 
  alt, 
  className = '', 
  priority = 'normal',
  showShimmer = true,
  onLoad,
  onError
}: PosterImageProps) {
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null)
  const [error, setError] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [aspectRatio, setAspectRatio] = useState('2/3') // default movie poster ratio
  const imgRef = useRef<HTMLImageElement>(null)

  const handleLoad = useCallback((e: any) => {
    try {
      const img: HTMLImageElement = e?.currentTarget || imgRef.current
      if (img && img.naturalWidth && img.naturalHeight) {
        const width = img.naturalWidth
        const height = img.naturalHeight
        const ratio = width / height
        
        setDimensions({ width, height })
        
        // Определяем оптимальное соотношение сторон
        if (ratio >= 1.7) {
          setAspectRatio('16/9')   // широкий формат
        } else if (ratio >= 1.4) {
          setAspectRatio('3/2')    // фото формат
        } else if (ratio >= 1.2) {
          setAspectRatio('4/3')    // стандартный
        } else if (ratio >= 0.8) {
          setAspectRatio('3/4')    // портретный
        } else {
          setAspectRatio('2/3')    // классический постер
        }
      }
      setIsLoading(false)
      onLoad?.()
    } catch {
      setIsLoading(false)
      onLoad?.()
    }
  }, [onLoad])

  const handleError = useCallback(() => {
    setError(true)
    setIsLoading(false)
    onError?.()
  }, [onError])

  // Предзагрузка изображения для высокоприоритетных постеров
  useEffect(() => {
    if (priority === 'high' && src && !error) {
      const img = new Image()
      img.onload = handleLoad
      img.onerror = handleError
      img.src = src
    }
  }, [src, priority, error, handleLoad, handleError])

  if (!src || error) {
    return (
      <div 
        className={`w-full bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg flex flex-col items-center justify-center text-gray-400 ${className}`}
        style={{ aspectRatio }}
      >
        <svg className="w-12 h-12 mb-2 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span className="text-xs font-medium opacity-60">Нет постера</span>
      </div>
    )
  }

  return (
    <div className={`relative overflow-hidden rounded-lg ${className}`} style={{ aspectRatio }}>
      {/* Shimmer loading effect */}
      {isLoading && showShimmer && (
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
      )}
      
      <LazyLoadImage
        ref={imgRef}
        src={src}
        alt={alt}
        effect="blur"
        className={`w-full h-full object-cover transition-all duration-500 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        onLoad={handleLoad}
        onError={handleError}
        loading={priority === 'high' ? 'eager' : 'lazy'}
      />
    </div>
  )
}
