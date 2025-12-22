'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, Sparkles, HelpCircle, Package, MapPin, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { OriAvatar } from '@/components/ui/ori-avatar'
import { oriAIService, QuestionResponse } from '@/lib/ori-ai'

interface Message {
  id: string
  type: 'user' | 'ori'
  content: string
  timestamp: Date
  confidence?: number
  relatedFAQs?: Array<{ question: string; answer: string }>
}

const quickActions = [
  { icon: Package, label: 'Find items', query: 'How do I find items to borrow?' },
  { icon: MapPin, label: 'Locate hubs', query: 'Where is my nearest hub?' },
  { icon: Users, label: 'Find mentors', query: 'How do I find a mentor?' },
  { icon: HelpCircle, label: 'Get help', query: 'How does fLOKr work?' },
]

export function OriChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ori',
      content: "Hi! I'm Ori 🐦 your AI assistant. I'm here to help you navigate fLOKr, find items, connect with mentors, and answer any questions you have. How can I help you today?",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (question?: string) => {
    const messageText = question || input.trim()
    if (!messageText || isLoading) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Get response from Ori
      const response: QuestionResponse = await oriAIService.askQuestion(messageText)
      
      // Add Ori's response
      const oriMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ori',
        content: response.answer,
        timestamp: new Date(),
        confidence: response.confidence,
        relatedFAQs: response.related_faqs.slice(0, 2), // Show top 2 related FAQs
      }
      setMessages(prev => [...prev, oriMessage])
    } catch (error) {
      console.error('Error asking Ori:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ori',
        content: "I'm having trouble connecting right now. Please try again in a moment, or contact your hub steward for immediate assistance.",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = (query: string) => {
    handleSend(query)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* Avatar */}
              {message.type === 'ori' && (
                <div className="flex-shrink-0">
                  <OriAvatar size="sm" showBadge />
                </div>
              )}
              
              {message.type === 'user' && (
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-semibold">
                    U
                  </div>
                </div>
              )}

              {/* Message Content */}
              <div className={`flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
                <div
                  className={`inline-block max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    message.type === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  
                  {/* Confidence Badge */}
                  {message.type === 'ori' && message.confidence !== undefined && message.confidence > 0.7 && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
                      <Sparkles className="h-3 w-3" />
                      <span>High confidence answer</span>
                    </div>
                  )}
                  
                  {/* Related FAQs */}
                  {message.type === 'ori' && message.relatedFAQs && message.relatedFAQs.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-semibold text-muted-foreground">Related questions:</p>
                      {message.relatedFAQs.map((faq, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(faq.question)}
                          className="block w-full text-left text-xs p-2 rounded-lg bg-background/50 hover:bg-background transition-colors"
                        >
                          {faq.question}
                        </button>
                      ))}
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
        </AnimatePresence>

        {/* Typing Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3"
          >
            <div className="flex-shrink-0">
              <OriAvatar size="sm" isTyping />
            </div>
            <div className="bg-muted rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <motion.div
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  className="h-2 w-2 rounded-full bg-muted-foreground/50"
                />
                <motion.div
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  className="h-2 w-2 rounded-full bg-muted-foreground/50"
                />
                <motion.div
                  animate={{ y: [0, -5, 0] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  className="h-2 w-2 rounded-full bg-muted-foreground/50"
                />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      {messages.length === 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="px-4 pb-3"
        >
          <p className="text-xs text-muted-foreground mb-2 font-semibold">Quick actions:</p>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((action) => {
              const Icon = action.icon
              return (
                <Button
                  key={action.label}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickAction(action.query)}
                  className="justify-start h-auto py-2"
                  disabled={isLoading}
                >
                  <Icon className="h-4 w-4 mr-2 flex-shrink-0" />
                  <span className="text-xs">{action.label}</span>
                </Button>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* Input Area */}
      <div className="border-t border-border p-4">
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
            placeholder="Ask Ori anything..."
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
    </div>
  )
}
