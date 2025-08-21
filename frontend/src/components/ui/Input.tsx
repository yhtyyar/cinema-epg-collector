import { forwardRef, InputHTMLAttributes } from 'react'
import cn from 'classnames'

type Props = InputHTMLAttributes<HTMLInputElement>

const Input = forwardRef<HTMLInputElement, Props>(function Input({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        'w-full rounded-md border border-gray-300/60 dark:border-white/10 bg-white dark:bg-white/5 px-3 py-2 text-sm outline-none focus:ring-2 ring-accent/50 transition',
        className
      )}
      {...props}
    />
  )
})

export default Input
