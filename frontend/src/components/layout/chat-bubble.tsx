'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Loader2, Sparkles, Minimize2, Maximize2, Package, MapPin, Users, HelpCircle, Circle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { oriAIService, QuestionResponse } from '@/lib/ori-ai'

const quickActions = [
  { icon: Package, label: 'Find items', query: 'How do I find items to borrow?' },
  { icon: MapPin, label: 'Locate hubs', query: 'Where is my nearest hub?' },
  { icon: Users, label: 'Find mentors', query: 'How do I find a mentor?' },
  { icon: HelpCircle, label: 'Get help', query: 'How does fLOKr work?' },
]

interface Message {
  id: string
  type: 'user' | 'other'
  content: string
  timestamp: Date
  confidence?: number
}

interface ChatBubbleProps {
  isOpen: boolean
  onClose: () => void
  chatWith: {
    id: number
    name: string
    isOri?: boolean
  }
  sidebarCollapsed?: boolean
}

export function ChatBubble({ isOpen, onClose, chatWith, sidebarCollapsed = false }: ChatBubbleProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [hasUserTyped, setHasUserTyped] = useState(false)
  const [isClosing, setIsClosing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const handleClose = () => {
    setIsClosing(true)
    setTimeout(() => {
      setIsClosing(false)
      onClose()
    }, 400) // Match animation duration
  }

  // Initialize with welcome message for Ori
  useEffect(() => {
    if (isOpen && chatWith.isOri && messages.length === 0) {
      setMessages([
        {
          id: '1',
          type: 'other',
          content: "Hi! I'm Ori 🐦 your AI assistant. I'm here to help you navigate fLOKr, find items, connect with mentors, and answer any questions you have. How can I help you today?",
          timestamp: new Date(),
        }
      ])
    }
  }, [isOpen, chatWith.isOri, messages.length])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (question?: string) => {
    const messageText = question || input.trim()
    if (!messageText || isLoading) return

    // Mark that user has typed if they manually entered text
    if (!question) {
      setHasUserTyped(true)
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')

    if (chatWith.isOri) {
      setIsLoading(true)
      try {
        const response: QuestionResponse = await oriAIService.askQuestion(messageText)
        
        const oriMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'other',
          content: response.answer,
          timestamp: new Date(),
          confidence: response.confidence,
        }
        setMessages(prev => [...prev, oriMessage])
      } catch (error) {
        console.error('Error asking Ori:', error)
        
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'other',
          content: "I'm having trouble connecting right now. Please try again in a moment.",
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        setIsLoading(false)
      }
    } else {
      // For regular friends - simulate message sent (would connect to real chat API)
      setTimeout(() => {
        const replyMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'other',
          content: "Thanks for your message! Chat functionality coming soon.",
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, replyMessage])
      }, 1000)
    }
  }

  // Calculate right position based on sidebar state
  const rightPosition = sidebarCollapsed ? 80 : 360 // 60px sidebar + 20px gap or 340px sidebar + 20px gap

  return (
    <AnimatePresence>
      {(isOpen || isClosing) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ 
            opacity: 1, 
            scale: 1, 
            y: 0,
            height: isMinimized ? 'auto' : 500,
            right: rightPosition
          }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
          style={{ right: `${rightPosition}px` }}
          className="fixed bottom-6 w-96 bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50"
        >
        {/* Header */}
        <div 
          className={`flex items-center justify-between p-3 ${!isMinimized ? 'border-b border-border' : ''} ${
            chatWith.isOri ? 'bg-gradient-to-r from-[#D97A5B]/5 to-[#C26A52]/5' : 'bg-muted/30'
          } ${isMinimized ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
          onClick={isMinimized ? () => setIsMinimized(false) : undefined}
        >
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            {chatWith.isOri ? (
              <div className="relative flex-shrink-0">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#D97A5B] to-[#C26A52] flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <Circle className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 fill-green-500 text-green-500" />
              </div>
            ) : (
              <div className="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-sm flex-shrink-0">
                {chatWith.name.split(' ').map(n => n[0]).join('')}
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-sm truncate">
                {chatWith.name}
              </p>
              {!isMinimized && (
                <p className="text-xs text-muted-foreground truncate">
                  {chatWith.isOri ? 'AI Assistant' : 'Online'}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-0.5 flex-shrink-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-8 w-8"
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        {!isMinimized && (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-muted/20">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-2 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  {/* Message Content */}
                  <div className={`flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
                    <div
                      className={`inline-block max-w-[85%] rounded-2xl px-3 py-2 ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : chatWith.isOri
                          ? 'bg-card border border-border'
                          : 'bg-card'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      
                      {/* Confidence Badge for Ori */}
                      {chatWith.isOri && message.type === 'other' && message.confidence !== undefined && message.confidence > 0.7 && (
                        <div className="mt-1.5 flex items-center gap-1 text-xs text-muted-foreground">
                          <Sparkles className="h-3 w-3" />
                          <span>High confidence</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Timestamp */}
                    <p className="text-xs text-muted-foreground mt-1 px-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </motion.div>
              ))}

              {/* Typing Indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-2"
                >
                  <div className="bg-card border border-border rounded-2xl px-3 py-2">
                    <div className="flex gap-1">
                      <motion.div
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                        className="h-2 w-2 rounded-full bg-muted-foreground/50"
                      />
                      <motion.div
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                        className="h-2 w-2 rounded-full bg-muted-foreground/50"
                      />
                      <motion.div
                        animate={{ y: [0, -3, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                        className="h-2 w-2 rounded-full bg-muted-foreground/50"
                      />
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions - Show only for Ori until user types their own message */}
            {chatWith.isOri && !hasUserTyped && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="px-4 py-3 border-t border-border bg-card"
              >
                <p className="text-xs text-muted-foreground mb-2.5 font-medium">Quick actions:</p>
                <div className="grid grid-cols-2 gap-2">
                  {quickActions.map((action) => {
                    const Icon = action.icon
                    return (
                      <Button
                        key={action.label}
                        variant="outline"
                        size="sm"
                        onClick={() => handleSend(action.query)}
                        className="justify-start h-auto py-2 text-xs"
                        disabled={isLoading}
                      >
                        <Icon className="h-3.5 w-3.5 mr-1.5 flex-shrink-0" />
                        <span className="truncate">{action.label}</span>
                      </Button>
                    )
                  })}
                </div>
              </motion.div>
            )}

            {/* Input Area */}
            <div className="border-t border-border p-3 bg-card">
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSend()
                }}
                className="flex gap-2"
              >
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`Message ${chatWith.name}...`}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  size="icon"
                  disabled={!input.trim() || isLoading}
                  className="flex-shrink-0"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
            </div>
          </>
        )}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
