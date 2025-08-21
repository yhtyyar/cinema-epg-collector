export default function LoadingSpinner({ label = 'Загрузка...' }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-gray-500">
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-r-transparent" />
      {label}
    </div>
  )
}
