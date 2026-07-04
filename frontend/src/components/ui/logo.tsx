'use client'

import { cn } from '@/lib/utils'
import Image from 'next/image'
import Link from 'next/link'

interface LogoProps {
  className?: string
  size?: number
  href?: string
  showBackground?: boolean
  animate?: boolean
  onClick?: () => void
}

export function Logo({ className = '', size = 32, href, showBackground = false, animate = false, onClick }: LogoProps) {
  const src = animate ? '/goose-animated.png' : '/goose.png'

  const logoContent = (
    <span
      onClick={onClick}
      className={cn(
        "inline-flex shrink-0 items-center justify-center overflow-hidden",
        showBackground && "rounded-full bg-muted p-1",
        className
      )}
      style={{
        width: `${size}px`,
        height: `${size}px`,
      }}
      role="img"
      aria-label="fLOKr Logo"
    >
      <Image
        src={src}
        alt=""
        width={size}
        height={size}
        unoptimized
        priority={size >= 72}
        className="h-full w-full select-none object-contain"
        draggable={false}
      />
    </span>
  )

  if (href) {
    return (
      <Link href={href} className="inline-flex">
        {logoContent}
      </Link>
    )
  }

  return logoContent
}
