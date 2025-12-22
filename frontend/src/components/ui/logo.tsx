'use client'

import { cn } from '@/lib/utils'
import Link from 'next/link'
import { motion } from 'framer-motion'

interface LogoProps {
  className?: string
  size?: number
  href?: string
  showBackground?: boolean
  animate?: boolean
  onClick?: () => void
}

export function Logo({ className = '', size = 32, href, showBackground = false, animate = true, onClick }: LogoProps) {
  const logoContent = (
    <motion.span
      onClick={onClick} 
      className={cn(
        "inline-flex items-center justify-center",
        showBackground && "rounded-full bg-muted",
        className
      )}
      style={{ 
        fontSize: `${size * 0.6}px`, 
        lineHeight: 1,
        width: `${size}px`,
        height: `${size}px`,
      }}
      role="img"
      aria-label="fLOKr Logo"
      animate={animate ? { 
        rotate: [-4, 4],
        x: [-1, 1],
      } : { rotate: 0, x: 0 }}
      transition={{
        duration: 0.8,
        repeat: Infinity,
        ease: "easeInOut",
        repeatType: "reverse"
      }}
      whileHover={!animate ? {
        scale: 1.1,
        transition: { 
          duration: 0.3,
          ease: "easeOut"
        }
      } : {
        rotate: [-8, 8, -8, 0],
        x: [-2, 2, -2, 0],
        transition: { 
          duration: 0.8,
          repeat: Infinity,
          ease: "easeInOut",
          repeatType: "loop"
        }
      }}
    >
      🪿
    </motion.span>
  )

  if (href) {
    return (
      <Link href={href} className="inline-flex transition-opacity hover:opacity-80">
        {logoContent}
      </Link>
    )
  }

  return logoContent
}
