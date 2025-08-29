import { ButtonHTMLAttributes } from 'react'
import cn from 'classnames'

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'ghost' }

export default function Button({ className, variant = 'primary', ...props }: Props) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition disabled:opacity-60 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-accent text-white hover:opacity-90 shadow-soft',
    secondary: 'bg-gray-200 dark:bg-white/10 text-gray-900 dark:text-gray-100 hover:bg-gray-300/70 dark:hover:bg-white/15',
    ghost: 'hover:bg-gray-100 dark:hover:bg-white/10'
  }
  return <button className={cn(base, variants[variant], className)} {...props} />
}
