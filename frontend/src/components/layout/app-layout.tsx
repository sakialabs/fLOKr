'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LeftSidebar } from './left-sidebar'
import { RightSidebar } from './right-sidebar'

interface AppLayoutProps {
  children: React.ReactNode
}

// Responsive breakpoint for collapsing sidebars (1280px = xl breakpoint)
const COLLAPSE_BREAKPOINT = 1280

export function AppLayout({ children }: AppLayoutProps) {
  // Initialize collapsed state based on screen size
  const [leftCollapsed, setLeftCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < COLLAPSE_BREAKPOINT
    }
    return false
  })
  const [rightCollapsed, setRightCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < COLLAPSE_BREAKPOINT
    }
    return false
  })
  const [shouldOpenOriChat, setShouldOpenOriChat] = useState(false)

  // Handle screen resize to auto-collapse/expand sidebars
  useEffect(() => {
    const handleResize = () => {
      const isSmallScreen = window.innerWidth < COLLAPSE_BREAKPOINT
      setLeftCollapsed(isSmallScreen)
      setRightCollapsed(isSmallScreen)
    }

    // Add debounce to avoid too many updates
    let timeoutId: NodeJS.Timeout
    const debouncedResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(handleResize, 150)
    }

    window.addEventListener('resize', debouncedResize)
    return () => {
      window.removeEventListener('resize', debouncedResize)
      clearTimeout(timeoutId)
    }
  }, [])

  useEffect(() => {
    const handleOpenOriChat = () => {
      setShouldOpenOriChat(true)
      setTimeout(() => setShouldOpenOriChat(false), 100)
    }
    window.addEventListener('openOriChat', handleOpenOriChat)
    return () => window.removeEventListener('openOriChat', handleOpenOriChat)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Left Sidebar - Navigation */}
      <LeftSidebar collapsed={leftCollapsed} onToggle={() => setLeftCollapsed(!leftCollapsed)} />

      {/* Main Content - Feed */}
      <motion.main
        layout
        className="flex-1 overflow-y-auto min-w-0"
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="max-w-6xl mx-auto p-4 md:p-6">
          {children}
        </div>
      </motion.main>

      {/* Right Sidebar - Friends & Chat */}
      <RightSidebar 
        collapsed={rightCollapsed} 
        onToggle={() => setRightCollapsed(!rightCollapsed)}
        shouldOpenOriChat={shouldOpenOriChat}
      />
    </div>
  )
}
