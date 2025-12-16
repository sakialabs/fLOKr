'use client'

import { motion } from 'framer-motion'
import { OriChatInterface } from '@/components/ori/ori-chat-interface'
import { OriAvatar } from '@/components/ui/ori-avatar'
import { Sparkles, MessageCircle, Zap, Heart } from 'lucide-react'

export default function OriPage() {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-border bg-card/50 backdrop-blur-sm"
      >
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4">
            <OriAvatar size="lg" showBadge />
            <div className="flex-1">
              <h1 className="text-2xl font-bold flex items-center gap-2">
                Chat with Ori
                <span className="text-lg bg-gradient-to-r from-[#D97A5B] to-[#C26A52] text-white px-2 py-1 rounded-lg text-sm">
                  AI Assistant
                </span>
              </h1>
              <p className="text-muted-foreground mt-1">
                Your friendly AI assistant for all things fLOKr 🐦
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6">
            <div className="flex items-center gap-2 text-sm">
              <div className="h-8 w-8 rounded-full bg-[#D97A5B]/10 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-[#D97A5B]" />
              </div>
              <span className="text-muted-foreground">Smart answers</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-8 w-8 rounded-full bg-[#D97A5B]/10 flex items-center justify-center">
                <Zap className="h-4 w-4 text-[#D97A5B]" />
              </div>
              <span className="text-muted-foreground">Instant help</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-8 w-8 rounded-full bg-[#D97A5B]/10 flex items-center justify-center">
                <MessageCircle className="h-4 w-4 text-[#D97A5B]" />
              </div>
              <span className="text-muted-foreground">24/7 available</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="h-8 w-8 rounded-full bg-[#D97A5B]/10 flex items-center justify-center">
                <Heart className="h-4 w-4 text-[#D97A5B]" />
              </div>
              <span className="text-muted-foreground">Always helpful</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Chat Interface */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex-1 overflow-hidden"
      >
        <div className="max-w-5xl mx-auto h-full">
          <div className="h-full bg-card border-x border-border">
            <OriChatInterface />
          </div>
        </div>
      </motion.div>
    </div>
  )
}
