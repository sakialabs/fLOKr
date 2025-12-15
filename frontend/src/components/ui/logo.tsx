import Image from 'next/image'

interface LogoProps {
  className?: string
  size?: number
}

export function Logo({ className = '', size = 32 }: LogoProps) {
  return (
    <Image
      src="/logo.png"
      alt="fLOKr Logo"
      width={size}
      height={size}
      className={className}
      priority
    />
  )
}
