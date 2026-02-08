import React from 'react';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export function Skeleton({ className = '', ...props }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded-md bg-muted ${className}`}
      {...props}
    />
  );
}

export function SkeletonText({
  className = '',
  lines = 1,
  ...props
}: SkeletonProps & { lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={`h-4 w-full ${i === lines - 1 ? className : ''}`}
          {...(i === lines - 1 ? props : {})}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className = '', ...props }: SkeletonProps) {
  return (
    <div
      className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
      {...props}
    >
      <div className="p-6 space-y-4">
        <Skeleton className="h-6 w-3/4" />
        <SkeletonText lines={3} />
      </div>
    </div>
  );
}

export function SkeletonLine({ className = '', ...props }: SkeletonProps) {
  return <Skeleton className={`h-4 w-full ${className}`} {...props} />;
}

export function SkeletonAvatar({ className = '', ...props }: SkeletonProps) {
  return <Skeleton className={`h-10 w-10 rounded-full ${className}`} {...props} />;
}

export function SkeletonButton({ className = '', ...props }: SkeletonProps) {
  return <Skeleton className={`h-10 w-20 rounded-md ${className}`} {...props} />;
}
