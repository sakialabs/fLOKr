'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { toast } from 'sonner'
import { api } from '@/lib/api'

interface Newcomer {
  id: string
  name: string
  joined_days_ago: number
  hub: string
  language: string
}

interface WelcomeModalProps {
  isOpen: boolean
  onClose: () => void
}

const welcomeTemplates = [
  "Welcome to the community 👋",
  "If you need help finding essentials, feel free to ask",
  "Glad you're here. Hope your first days go smoothly",
]

export function WelcomeModal({ isOpen, onClose }: WelcomeModalProps) {
  const [newcomers, setNewcomers] = useState<Newcomer[]>([])
  const [selectedNewcomer, setSelectedNewcomer] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [customMessage, setCustomMessage] = useState<string>('')
  const [sent, setSent] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (isOpen) {
      fetchNewcomers()
    }
  }, [isOpen])

  const fetchNewcomers = async () => {
    try {
      const response = await api.get('/community/data/newcomers/')
      setNewcomers(response.data)
    } catch (error) {
      console.error('Failed to fetch newcomers:', error)
      toast.error('Failed to load newcomers')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectTemplate = (template: string) => {
    setSelectedTemplate(template)
    setCustomMessage(template)
  }

  const handleSend = () => {
    if (!selectedNewcomer || !customMessage.trim()) return

    // Here you would send the welcome message via API
    setSent(true)
    
    setTimeout(() => {
      toast.success('Your welcome was sent. Thank you.')
      onClose()
      // Reset state
      setTimeout(() => {
        setSelectedNewcomer(null)
        setSelectedTemplate('')
        setCustomMessage('')
        setSent(false)
      }, 300)
    }, 1000)
  }

  const handleClose = () => {
    onClose()
    // Reset state after animation
    setTimeout(() => {
      setSelectedNewcomer(null)
      setSelectedTemplate('')
      setCustomMessage('')
      setSent(false)
    }, 300)
  }

  return (
    <AnimatePresence mode="wait">
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            onClick={handleClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 20 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="relative z-10 w-full max-w-md mx-4"
          >
            <Card className="bg-card border border-border shadow-2xl">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-border">
                <h2 className="text-lg font-semibold">Welcome Someone</h2>
                <button
                  onClick={handleClose}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                {/* Success State */}
                {sent && (
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="py-12 text-center"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: 'spring' }}
                      className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10 mx-auto mb-4"
                    >
                      <Check className="h-8 w-8 text-green-500" />
                    </motion.div>
                    <p className="text-lg font-medium">Message sent</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Thank you for welcoming a new member
                    </p>
                  </motion.div>
                )}

                {/* Form */}
                {!sent && (
                  <>
                    {/* Intro */}
                    <p className="text-sm text-muted-foreground">
                      {isLoading ? 'Loading newcomers...' : newcomers.length === 0 
                        ? 'No new members to welcome right now.'
                        : 'Send a warm welcome to help new members feel at home.'}
                    </p>

                    {!isLoading && newcomers.length > 0 && (
                      <>
                        {/* Select Newcomer */}
                        <div className="space-y-2">
                          <label className="text-sm font-medium">Select a newcomer</label>
                          <div className="space-y-2">
                            {newcomers.map((newcomer) => (
                              <button
                                key={newcomer.id}
                                onClick={() => setSelectedNewcomer(newcomer.id)}
                                className={`w-full p-3 text-left rounded-lg border transition-all ${
                                  selectedNewcomer === newcomer.id
                                    ? 'border-primary bg-primary/5'
                                    : 'border-border hover:border-primary/50 hover:bg-muted/50'
                                }`}
                              >
                                <div className="flex items-center justify-between">
                                  <div>
                                    <p className="font-medium">{newcomer.name}</p>
                                    <p className="text-xs text-muted-foreground mt-0.5">
                                      {newcomer.hub} · Joined {newcomer.joined_days_ago} {newcomer.joined_days_ago === 1 ? 'day' : 'days'} ago
                                    </p>
                                  </div>
                                  {newcomer.language && newcomer.language !== 'en' && (
                                    <span className="px-2 py-1 text-xs bg-muted rounded">
                                      {newcomer.language.toUpperCase()}
                                    </span>
                                  )}
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Message Templates */}
                        {selectedNewcomer && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-2"
                          >
                            <label className="text-sm font-medium">Choose a message</label>
                            <div className="space-y-2">
                              {welcomeTemplates.map((template, index) => (
                                <button
                                  key={index}
                                  onClick={() => handleSelectTemplate(template)}
                                  className={`w-full p-3 text-left text-sm rounded-lg border transition-all ${
                                    selectedTemplate === template
                                      ? 'border-primary bg-primary/5'
                                      : 'border-border hover:border-primary/50 hover:bg-muted/50'
                                  }`}
                                >
                                  {template}
                                </button>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* Custom Message */}
                        {selectedNewcomer && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="space-y-2"
                          >
                            <label className="text-sm font-medium">Or write your own</label>
                            <textarea
                              value={customMessage}
                              onChange={(e) => setCustomMessage(e.target.value)}
                              className="w-full min-h-[100px] p-3 rounded-lg border border-border bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
                              placeholder="Or write your own message..."
                            />
                          </motion.div>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>

              {/* Footer */}
              {!sent && !isLoading && newcomers.length > 0 && (
                <div className="p-6 border-t border-border">
                  <Button
                    onClick={handleSend}
                    disabled={!selectedNewcomer || !customMessage.trim()}
                    className="w-full"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send Welcome
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
