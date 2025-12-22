import Image from 'next/image'
import { useState } from 'react'

interface LogoProps {
  className?: string
  size?: number
}

export function Logo({ className = '', size = 32 }: LogoProps) {
  const [imageError, setImageError] = useState(false)

  if (imageError) {
    return (
      <span 
        className={className}
        style={{ 
          fontSize: `${size}px`, 
          lineHeight: 1,
          display: 'inline-block',
          width: `${size}px`,
          height: `${size}px`,
        }}
        role="img"
        aria-label="fLOKr Logo"
      >
        🪿
      </span>
    )
  }

  return (
    <Image
      src="/logo.png"
      alt="fLOKr Logo"
      width={size}
      height={size}
      className={className}
      priority
      onError={() => setImageError(true)}
    />
  )
}
