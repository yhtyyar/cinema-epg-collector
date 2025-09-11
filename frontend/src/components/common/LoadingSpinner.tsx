import { memo } from 'react';
import { cn } from '../../lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

function LoadingSpinnerComponent({ size = 'md', className }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          sizeClasses[size],
          'animate-spin rounded-full border-2 border-solid border-t-transparent'
        )}
        style={{
          borderColor: 'var(--accent-primary)',
          borderTopColor: 'transparent'
        }}
      />
    </div>
  );
}

export const LoadingSpinner = memo(LoadingSpinnerComponent);