'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Briefcase,
  Calendar,
  Package,
  Users,
} from 'lucide-react'
import { NaviChatInterface } from '@/components/ori/ori-chat-interface'
import { OriAvatar } from '@/components/ui/ori-avatar'
import { Logo } from '@/components/ui/logo'
import { Button } from '@/components/ui/button'

const guideStrengths = [
  {
    icon: Package,
    title: 'Resources',
    body: 'Find items, hubs, and practical support nearby.',
  },
  {
    icon: Users,
    title: 'Circles',
    body: 'Meet people gathering around shared needs.',
  },
  {
    icon: Calendar,
    title: 'Moves',
    body: 'Turn questions into workshops, drives, and meetups.',
  },
  {
    icon: Briefcase,
    title: 'Shifts',
    body: 'Get pointed toward work support and Lexi when rights questions come up.',
  },
]

export default function NaviPage() {
  return (
    <div className="flex h-dvh min-h-0 flex-col overflow-hidden bg-background">
      <header className="shrink-0 border-b border-border/80 bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
          <Link href="/" className="flex min-w-0 items-center gap-3">
            <Logo size={38} />
            <span className="text-lg font-bold text-primary">fLOKr</span>
          </Link>
          <div className="flex shrink-0 items-center gap-2">
            <Button asChild variant="ghost" size="sm" className="hidden sm:inline-flex">
              <Link href="/loop">Open Loop</Link>
            </Button>
            <Button asChild variant="outline" size="sm">
              <Link href="/">
                <ArrowLeft className="h-4 w-4" />
                Home
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="min-h-0 flex-1 px-4 py-4 sm:px-6 sm:py-5">
        <div className="mx-auto grid h-full min-h-0 w-full min-w-0 max-w-7xl gap-4 lg:grid-cols-[300px_minmax(0,1fr)]">
          <motion.aside
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="hidden min-h-0 min-w-0 flex-col overflow-hidden rounded-lg border border-border/80 bg-muted/25 p-5 shadow-sm lg:flex"
          >
            <div className="flex items-start gap-4">
              <OriAvatar size="lg" animated />
              <div className="min-w-0">
                <h1 className="text-3xl font-bold leading-tight">Chat with Navi</h1>
              </div>
            </div>

            <p className="mt-5 break-words text-sm leading-7 text-muted-foreground">
              Navi helps you find your way through fLOKr with resource guidance, Signal clarity, Circle matching, and
              practical next steps.
            </p>

            <div className="mt-5 grid gap-2">
              {guideStrengths.map((item) => {
                const Icon = item.icon

                return (
                  <div key={item.title} className="flex min-w-0 gap-3 rounded-lg border border-border/70 bg-background p-3">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-secondary/10 text-secondary">
                      <Icon className="h-4 w-4" />
                    </span>
                    <div className="min-w-0">
                      <h2 className="text-sm font-semibold">{item.title}</h2>
                      <p className="mt-1 break-words text-xs leading-5 text-muted-foreground">{item.body}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.aside>

          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.35 }}
            className="min-h-0 min-w-0"
          >
            <NaviChatInterface />
          </motion.section>
        </div>
      </main>
    </div>
  )
}
