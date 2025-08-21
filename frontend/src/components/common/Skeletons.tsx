export function SkeletonCard() {
  return (
    <div className="rounded-lg overflow-hidden border border-gray-200/10 bg-white/50 dark:bg-white/5">
      <div className="aspect-[2/3] skeleton" />
      <div className="p-3 space-y-2">
        <div className="h-4 w-3/4 skeleton" />
        <div className="h-3 w-1/3 skeleton" />
      </div>
    </div>
  )
}

export function SkeletonGrid({ count = 12 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:gap-5 grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {Array.from({ length: count }, (_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  )
}

export function SkeletonDetail() {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-1">
        <div className="aspect-[2/3] skeleton rounded-lg" />
      </div>
      <div className="md:col-span-2 space-y-4">
        <div className="h-7 w-2/3 skeleton" />
        <div className="h-4 w-1/2 skeleton" />
        <div className="flex gap-3">
          <div className="h-4 w-24 skeleton" />
          <div className="h-4 w-28 skeleton" />
          <div className="h-4 w-32 skeleton" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-full skeleton" />
          <div className="h-4 w-11/12 skeleton" />
          <div className="h-4 w-10/12 skeleton" />
        </div>
      </div>
    </div>
  )
}
