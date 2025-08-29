export default function ErrorMessage({ message = 'Ошибка загрузки данных' }: { message?: string }) {
  return (
    <div role="alert" className="rounded-md border border-red-300/50 bg-red-50/50 dark:bg-red-900/10 px-3 py-2 text-red-700 dark:text-red-300">
      {message}
    </div>
  )
}
