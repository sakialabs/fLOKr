'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LeftSidebar } from './left-sidebar'
import { RightSidebar } from './right-sidebar'

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const [leftCollapsed, setLeftCollapsed] = useState(false)
  const [rightCollapsed, setRightCollapsed] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Left Sidebar - Navigation */}
      <LeftSidebar collapsed={leftCollapsed} onToggle={() => setLeftCollapsed(!leftCollapsed)} />

      {/* Main Content - Feed */}
      <motion.main
        layout
        className="flex-1 overflow-y-auto"
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="max-w-4xl mx-auto p-6">
          {children}
        </div>
      </motion.main>

      {/* Right Sidebar - Friends & Chat */}
      <RightSidebar collapsed={rightCollapsed} onToggle={() => setRightCollapsed(!rightCollapsed)} />
    </div>
  )
}
