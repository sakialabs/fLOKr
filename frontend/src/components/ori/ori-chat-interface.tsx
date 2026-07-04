'use client'

import { useState, useRef, useEffect } from 'react'
import type { KeyboardEvent } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, HelpCircle, Package, MapPin, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { OriAvatar } from '@/components/ui/ori-avatar'
import { naviAIService, QuestionResponse } from '@/lib/ori-ai'

interface Message {
  id: string
  type: 'user' | 'navi'
  content: string
  timestamp: Date
  confidence?: number
  relatedFAQs?: Array<{ question: string; answer: string }>
}

const quickActions = [
  { icon: Package, label: 'Find items', query: 'Help me find a winter coat or household items nearby.' },
  { icon: MapPin, label: 'Locate hubs', query: 'Where should I go if I need support from a local hub?' },
  { icon: Users, label: 'Find Leads', query: 'Can you help me find a Lead who understands translation or housing questions?' },
  { icon: HelpCircle, label: 'Post a Signal', query: 'Help me write a Signal asking my community for support.' },
]

export function NaviChatInterface() {
  const composerRef = useRef<HTMLTextAreaElement>(null)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'navi',
      content: "Hi, I'm Navi. I can help you find resources, understand Signals, join Circles, plan Moves, connect with Crews, and get support through Shifts.",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    const container = messagesContainerRef.current

    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const initialPrompt = new URLSearchParams(window.location.search).get('prompt')?.trim()

    if (!initialPrompt) {
      return
    }

    setInput(initialPrompt)
    composerRef.current?.focus()
  }, [])

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
      const response: QuestionResponse = await naviAIService.askQuestion(messageText)
      
      const naviMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'navi',
        content: response.answer,
        timestamp: new Date(),
        confidence: response.confidence,
        relatedFAQs: response.related_faqs.slice(0, 2), // Show top 2 related FAQs
      }
      setMessages(prev => [...prev, naviMessage])
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      console.warn(`Navi request failed: ${message}`)
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'navi',
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

  const handleComposerKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full min-h-0 max-w-full flex-col overflow-hidden rounded-lg border border-border/80 bg-card/90 shadow-xl shadow-primary/5">
      <div className="flex items-center justify-between border-b border-border/80 px-4 py-3 sm:px-5">
        <div className="flex min-w-0 items-center gap-3">
          <OriAvatar size="md" />
          <div className="min-w-0">
            <h2 className="truncate text-base font-semibold">Navi</h2>
            <p className="truncate text-xs text-muted-foreground">Community guide for fLOKr</p>
          </div>
        </div>
      </div>

      <div ref={messagesContainerRef} className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-5">
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
                {message.type === 'navi' && <OriAvatar size="sm" />}

                {message.type === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                    U
                  </div>
                )}

                <div className={`min-w-0 flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
                  <div
                    className={`max-w-[min(40rem,85%)] rounded-2xl px-4 py-3 text-sm leading-6 sm:text-base sm:leading-7 ${
                      message.type === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'border border-border/70 bg-background'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>

                    {message.type === 'navi' && message.relatedFAQs && message.relatedFAQs.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs font-semibold text-muted-foreground">Related questions</p>
                        {message.relatedFAQs.map((faq, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSend(faq.question)}
                            className="block w-full rounded-lg border border-border/70 bg-card/80 p-2 text-left text-xs transition-colors hover:border-primary/35 hover:bg-primary/10"
                          >
                            {faq.question}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  <p className={`mt-1 px-1 text-xs text-muted-foreground ${message.type === 'user' ? 'text-right' : ''}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <OriAvatar size="sm" isTyping />
              <div className="rounded-2xl border border-border/70 bg-background px-4 py-3">
                <div className="flex gap-1.5">
                  <motion.div
                    animate={{ y: [0, -4, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    className="h-2 w-2 rounded-full bg-muted-foreground/60"
                  />
                  <motion.div
                    animate={{ y: [0, -4, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    className="h-2 w-2 rounded-full bg-muted-foreground/60"
                  />
                  <motion.div
                    animate={{ y: [0, -4, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    className="h-2 w-2 rounded-full bg-muted-foreground/60"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {messages.length === 1 && (
            <div className="ml-0 grid gap-2 sm:ml-11 sm:grid-cols-2">
              {quickActions.map((action) => {
                const Icon = action.icon
                return (
                  <button
                    key={action.label}
                    onClick={() => handleQuickAction(action.query)}
                    className="group flex min-h-16 items-start gap-3 rounded-lg border border-border/80 bg-background p-3 text-left transition-colors hover:border-primary/35 hover:bg-primary/10 disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={isLoading}
                  >
                    <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary/10 text-secondary">
                      <Icon className="h-4 w-4" />
                    </span>
                    <span className="min-w-0">
                      <span className="block text-sm font-semibold">{action.label}</span>
                      <span className="mt-1 block break-words text-xs leading-5 text-muted-foreground">
                        {action.query}
                      </span>
                    </span>
                  </button>
                )
              })}
            </div>
          )}

        </div>
      </div>

      <div className="border-t border-border/80 bg-background/65 p-3 sm:p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="mx-auto flex max-w-3xl items-end gap-2 rounded-lg border border-border bg-card p-2 shadow-sm focus-within:border-primary/45"
        >
          <Textarea
            ref={composerRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleComposerKeyDown}
            placeholder="Ask Navi anything..."
            disabled={isLoading}
            rows={1}
            className="max-h-32 min-h-11 flex-1 resize-none border-0 bg-transparent px-2 py-2.5 text-sm leading-6 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 sm:text-base"
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
            className="h-11 w-11 shrink-0"
            aria-label="Send message"
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
