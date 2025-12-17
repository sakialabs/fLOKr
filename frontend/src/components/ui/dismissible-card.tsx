'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface DismissibleCardProps {
  id: string
  children: React.ReactNode
  className?: string
  onDismiss?: () => void
}

export function DismissibleCard({ id, children, className, onDismiss }: DismissibleCardProps) {
  const [isDismissed, setIsDismissed] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(`dismissed-card-${id}`) === 'true'
    }
    return false
  })

  const handleDismiss = () => {
    setIsDismissed(true)
    if (typeof window !== 'undefined') {
      localStorage.setItem(`dismissed-card-${id}`, 'true')
    }
    onDismiss?.()
  }

  return (
    <AnimatePresence>
      {!isDismissed && (
        <motion.div
          initial={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0, marginBottom: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card className={cn('relative', className)}>
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 h-6 w-6 rounded-full opacity-50 hover:opacity-100 transition-opacity"
              onClick={handleDismiss}
            >
              <X className="h-4 w-4" />
            </Button>
            <CardContent className="p-4">
              {children}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
