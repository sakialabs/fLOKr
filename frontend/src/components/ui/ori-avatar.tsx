import Image from 'next/image'
import { cn } from '@/lib/utils'

interface OriAvatarProps {
  size?: 'sm' | 'md' | 'lg'
  showBadge?: boolean
  isTyping?: boolean
  animated?: boolean
  className?: string
}

const sizeMap = {
  sm: { container: 32, image: 26, status: 9, statusOffset: 0 },
  md: { container: 44, image: 36, status: 11, statusOffset: 1 },
  lg: { container: 68, image: 58, status: 14, statusOffset: 2 },
}

export function OriAvatar({
  size = 'md',
  showBadge = false,
  isTyping = false,
  animated = false,
  className = '',
}: OriAvatarProps) {
  const dimensions = sizeMap[size]
  const src = animated || isTyping ? '/compass-animated.png' : '/compass.png'

  return (
    <div
      className={cn('relative shrink-0', className)}
      style={{
        width: dimensions.container,
        height: dimensions.container,
      }}
    >
      <div
        className="relative flex h-full w-full items-center justify-center overflow-hidden rounded-full border border-secondary/20 bg-card shadow-sm"
        role="img"
        aria-label="Navi"
      >
        <Image
          src={src}
          alt=""
          width={dimensions.image}
          height={dimensions.image}
          unoptimized
          priority={size === 'lg'}
          className="h-[82%] w-[82%] select-none object-contain"
          draggable={false}
        />
      </div>

      {isTyping && (
        <div
          className="absolute inset-0 rounded-full border-2 border-secondary/45"
          aria-hidden="true"
        />
      )}

      {showBadge && (
        <span
          className="absolute -bottom-1 -right-1 rounded-full border-2 border-background bg-secondary px-1.5 py-0.5 text-[9px] font-bold leading-none text-secondary-foreground shadow-sm"
          aria-hidden="true"
        >
          Navi
        </span>
      )}

      <span
        className="absolute rounded-full border-2 border-background bg-success shadow-sm"
        style={{
          width: dimensions.status,
          height: dimensions.status,
          right: dimensions.statusOffset,
          bottom: dimensions.statusOffset,
        }}
        aria-hidden="true"
      />
    </div>
  )
}
