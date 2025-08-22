import { useState, useCallback } from 'react'
import { LazyLoadImage } from 'react-lazy-load-image-component'
import 'react-lazy-load-image-component/src/effects/blur.css'

type Props = {
  src?: string
  alt: string
  className?: string
  children?: React.ReactNode // overlay content (e.g. badges)
}

export default function ResponsivePoster({ src, alt, className = '', children }: Props) {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape' | undefined>(undefined)
  const [error, setError] = useState(false)

  const handleLoad = useCallback((e: any) => {
    try {
      const img: HTMLImageElement | undefined = e?.currentTarget
      if (img && img.naturalWidth && img.naturalHeight) {
        setOrientation(img.naturalWidth >= img.naturalHeight ? 'landscape' : 'portrait')
      }
    } catch {}
  }, [])

  const aspectClass = orientation === 'landscape' ? 'aspect-[16/9]' : 'aspect-[2/3]'

  return (
    <div className={`relative ${className}`}>
      <div className={`${aspectClass} w-full bg-gray-100 dark:bg-white/5 rounded-md overflow-hidden`}>
        {src && !error ? (
          <LazyLoadImage
            src={src}
            alt={alt}
            effect="blur"
            className="h-full w-full object-contain"
            onLoad={handleLoad}
            onError={() => setError(true)}
          />
        ) : (
          <div className="h-full w-full flex items-center justify-center text-gray-400 text-sm">Нет постера</div>
        )}
      </div>
      {children && (
        <div className="pointer-events-none absolute inset-0 flex p-2">
          {children}
        </div>
      )}
    </div>
  )
}
