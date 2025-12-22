'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Logo } from '@/components/ui/logo'
import { Button } from '@/components/ui/button'
import { useTheme } from 'next-themes'
import { Moon, Sun, Sparkles, Info, Mail, Menu, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AppHeaderProps {
  isAuthenticated?: boolean
}

export function AppHeader({ isAuthenticated = false }: AppHeaderProps) {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    setMounted(true)
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = isAuthenticated
    ? [
        { href: '/home', label: 'Dashboard', icon: null },
        { href: '/ori', label: 'Ori AI', icon: Sparkles },
        { href: '/about', label: 'About', icon: Info },
        { href: '/contact', label: 'Contact', icon: Mail },
      ]
    : [
        { href: '/about', label: 'About', icon: Info },
        { href: '/contact', label: 'Contact', icon: Mail },
        { href: '/login', label: 'Login', icon: null },
      ]

  const ctaLink = isAuthenticated ? null : { href: '/register', label: 'Get Involved' }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  if (!mounted) {
    return null
  }

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className={cn(
        'sticky top-0 z-50 w-full border-b transition-all duration-300',
        scrolled
          ? 'bg-background/80 backdrop-blur-lg shadow-sm'
          : 'bg-background/50 backdrop-blur-sm'
      )}
    >
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href={isAuthenticated ? '/home' : '/'} className="flex items-center gap-3">
            <motion.div whileHover={{ scale: 1.1 }} transition={{ duration: 0.2 }}>
              <Logo size={40} showBackground animate={false} />
            </motion.div>
            <span className="text-xl font-bold text-primary">
              fLOKr
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link, index) => {
              const Icon = link.icon
              const isActive = pathname === link.href || 
                (link.href === '/login' && pathname === '/register')
              
              return (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Link href={link.href}>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="relative gap-2 transition-all duration-200"
                    >
                      {Icon && <Icon className="h-4 w-4" />}
                      {link.label}
                      {isActive && (
                        <motion.div
                          layoutId="activeTab"
                          className="absolute bottom-0 left-0 right-0 h-0.5 bg-secondary"
                          transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                        />
                      )}
                    </Button>
                  </Link>
                </motion.div>
              )
            })}

            {/* Get Involved CTA */}
            {ctaLink && (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.05 }}
                transition={{ delay: 0.3, type: 'spring', stiffness: 400 }}
              >
                <Button asChild size="sm" className="ml-2">
                  <Link href={ctaLink.href}>{ctaLink.label}</Link>
                </Button>
              </motion.div>
            )}

            {/* Theme Toggle */}
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 }}
            >
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="gap-2 ml-2"
              >
                <AnimatePresence mode="wait">
                  <motion.div
                    key={theme}
                    initial={{ rotate: -180, opacity: 0 }}
                    animate={{ rotate: 0, opacity: 1 }}
                    exit={{ rotate: 180, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {theme === 'dark' ? (
                      <Sun className="h-4 w-4" />
                    ) : (
                      <Moon className="h-4 w-4" />
                    )}
                  </motion.div>
                </AnimatePresence>
              </Button>
            </motion.div>
          </nav>

          {/* Mobile Menu Toggle */}
          <div className="flex md:hidden items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.nav
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="md:hidden overflow-hidden border-t"
            >
              <div className="py-4 space-y-1">
                {navLinks.map((link, index) => {
                  const Icon = link.icon
                  const isActive = pathname === link.href
                  
                  return (
                    <motion.div
                      key={link.href}
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link href={link.href} onClick={() => setMobileMenuOpen(false)}>
                        <Button
                          variant={isActive ? 'secondary' : 'ghost'}
                          className="w-full justify-start gap-2"
                        >
                          {Icon && <Icon className="h-4 w-4" />}
                          {link.label}
                        </Button>
                      </Link>
                    </motion.div>
                  )
                })}
              </div>
            </motion.nav>
          )}
        </AnimatePresence>
      </div>
    </motion.header>
  )
}
