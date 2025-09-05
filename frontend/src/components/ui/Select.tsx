import { SelectHTMLAttributes } from 'react'
import cn from 'classnames'

type Props = SelectHTMLAttributes<HTMLSelectElement>

export default function Select({ className, children, ...props }: Props) {
  return (
    <select
      className={cn(
        'w-full rounded-md border border-gray-300 dark:border-white/10 bg-white dark:bg-white/5 px-3 py-2 text-sm outline-none focus:ring-2 ring-accent/50 transition',
        className
      )}
      {...props}
    >
      {children}
    </select>
  )
}
