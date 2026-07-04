'use client'

import { useState } from 'react'
import type { ComponentType } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Briefcase,
  Calendar,
  HelpCircle,
  Heart,
  MapPin,
  Megaphone,
  MessageCircle,
  Package,
  Send,
  Share2,
  Sparkles,
  Users,
} from 'lucide-react'

type SignalType = 'update' | 'ask' | 'offer' | 'welcome' | 'move' | 'hub_update' | 'shift'
type FeedFilter = 'all' | 'my' | SignalType
type ReactionAction = 'boost' | 'helpful' | 'solidarity' | 'can_help'

interface FeedItem {
  id: number
  signalType: SignalType
  title: string
  content: string
  timestamp: string
  hub?: string
  author?: string
  circle?: string
  crew?: string
  isMine?: boolean
  reactions: Record<ReactionAction, number>
}

interface Config {
  label: string
  icon: ComponentType<{ className?: string }>
  color: string
  bg: string
}

const emptyReactions = (): Record<ReactionAction, number> => ({
  boost: 0,
  helpful: 0,
  solidarity: 0,
  can_help: 0,
})

const mockFeedData: FeedItem[] = [
  {
    id: 1,
    signalType: 'welcome',
    title: 'Welcome Amina to the Newcomer Circle',
    content: 'Amina just joined Eastside Hub and is looking for winter gear, ESL practice, and a few friendly faces this week.',
    timestamp: '2 hours ago',
    hub: 'Eastside Hub',
    circle: 'Newcomer Circle',
    reactions: { boost: 4, helpful: 9, solidarity: 7, can_help: 3 },
  },
  {
    id: 2,
    signalType: 'offer',
    title: 'Phone chargers and transit cards available',
    content: 'The front desk has extra USB-C chargers and five transit cards for anyone settling in or heading to appointments.',
    timestamp: '4 hours ago',
    hub: 'Hub #2',
    author: 'Maya',
    reactions: { boost: 2, helpful: 12, solidarity: 4, can_help: 1 },
  },
  {
    id: 3,
    signalType: 'move',
    title: 'Friday dinner and supply table',
    content: 'Join the Food Pickup Crew at 6 PM. Bring a container if you have one, or show up early to help set tables.',
    timestamp: '1 day ago',
    hub: 'Hub #1',
    crew: 'Food Pickup Crew',
    reactions: { boost: 8, helpful: 10, solidarity: 11, can_help: 6 },
  },
  {
    id: 4,
    signalType: 'hub_update',
    title: 'Extended pickup window this week',
    content: 'Eastside Hub is open until 8 PM on Thursday and Friday for item pickups, returns, and quick support.',
    timestamp: '2 days ago',
    hub: 'Eastside Hub',
    reactions: { boost: 1, helpful: 6, solidarity: 2, can_help: 0 },
  },
  {
    id: 5,
    signalType: 'shift',
    title: 'Wage note: kitchen prep shifts',
    content: 'A local cafe posted transparent pay at $19/hour plus pooled tips. Share red flags or better leads with the Shift Circle.',
    timestamp: '3 days ago',
    hub: 'Downtown Circle',
    circle: 'Worker Support Circle',
    reactions: { boost: 5, helpful: 8, solidarity: 9, can_help: 2 },
  },
  {
    id: 6,
    signalType: 'ask',
    title: 'Need a stroller by Saturday',
    content: 'A family near Westside Hub needs a foldable stroller for a medical appointment. Pickup today or tomorrow would help.',
    timestamp: '3 days ago',
    hub: 'Westside Hub',
    author: 'Priya',
    reactions: { boost: 6, helpful: 5, solidarity: 6, can_help: 4 },
  },
]

const signalTypeConfig: Record<SignalType, Config> = {
  update: { label: 'Update', icon: MessageCircle, color: 'text-primary', bg: 'bg-primary/10' },
  ask: { label: 'Ask', icon: HelpCircle, color: 'text-rose-500', bg: 'bg-rose-500/10' },
  offer: { label: 'Offer', icon: Package, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  welcome: { label: 'Welcome', icon: Users, color: 'text-green-500', bg: 'bg-green-500/10' },
  move: { label: 'Move', icon: Calendar, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  hub_update: { label: 'Hub Update', icon: Megaphone, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  shift: { label: 'Shift', icon: Briefcase, color: 'text-amber-600', bg: 'bg-amber-500/10' },
}

const filterConfig: Array<{ value: FeedFilter; label: string; icon: Config['icon'] }> = [
  { value: 'all', label: 'All Signals', icon: MessageCircle },
  { value: 'ask', label: 'Asks', icon: HelpCircle },
  { value: 'offer', label: 'Offers', icon: Package },
  { value: 'welcome', label: 'Welcomes', icon: Users },
  { value: 'move', label: 'Moves', icon: Calendar },
  { value: 'hub_update', label: 'Hub Updates', icon: Megaphone },
  { value: 'shift', label: 'Shifts', icon: Briefcase },
  { value: 'my', label: 'My Signals', icon: Sparkles },
]

const composerTypes: SignalType[] = ['update', 'ask', 'offer', 'move', 'shift']

const reactionConfig: Array<{ value: ReactionAction; label: string; icon: Config['icon'] }> = [
  { value: 'boost', label: 'Boost', icon: Sparkles },
  { value: 'helpful', label: 'Helpful', icon: Heart },
  { value: 'solidarity', label: 'Solidarity', icon: Users },
  { value: 'can_help', label: 'I can help', icon: HelpCircle },
]

interface CommunityFeedProps {
  showHeader?: boolean
  defaultFilter?: 'all' | 'updates' | 'my' | SignalType
  hideMyUpdates?: boolean
}

export function CommunityFeed({
  showHeader = true,
  defaultFilter = 'all',
  hideMyUpdates = false,
}: CommunityFeedProps) {
  const initialFilter = defaultFilter === 'updates' ? 'my' : defaultFilter
  const [filter, setFilter] = useState<FeedFilter>(initialFilter)
  const [signals, setSignals] = useState<FeedItem[]>(mockFeedData)
  const [activeReactions, setActiveReactions] = useState<Set<string>>(new Set())
  const [signalType, setSignalType] = useState<SignalType>('update')
  const [signalText, setSignalText] = useState('')
  const [signalError, setSignalError] = useState('')

  const maxChars = 360
  const remainingChars = maxChars - signalText.length

  const filteredFeed = signals.filter((item) => {
    if (filter === 'all') return true
    if (filter === 'my') return item.isMine
    return item.signalType === filter
  })

  const handlePostSignal = () => {
    const trimmed = signalText.trim()

    if (!trimmed) {
      setSignalError('Add a short Signal before posting.')
      return
    }

    if (trimmed.length > maxChars) {
      setSignalError(`Signals must be ${maxChars} characters or less.`)
      return
    }

    const config = signalTypeConfig[signalType]
    const newSignal: FeedItem = {
      id: Date.now(),
      signalType,
      title: `${config.label} from you`,
      content: trimmed,
      timestamp: 'Just now',
      hub: 'Your hub',
      author: 'You',
      isMine: true,
      reactions: emptyReactions(),
    }

    setSignals((current) => [newSignal, ...current])
    setSignalText('')
    setSignalError('')
    setFilter('all')
  }

  const handleReaction = (itemId: number, action: ReactionAction) => {
    const reactionKey = `${itemId}:${action}`
    const wasActive = activeReactions.has(reactionKey)

    setSignals((current) =>
      current.map((item) => {
        if (item.id !== itemId) return item

        return {
          ...item,
          reactions: {
            ...item.reactions,
            [action]: Math.max(0, item.reactions[action] + (wasActive ? -1 : 1)),
          },
        }
      })
    )

    setActiveReactions((current) => {
      const next = new Set(current)
      if (wasActive) {
        next.delete(reactionKey)
      } else {
        next.add(reactionKey)
      }
      return next
    })
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 },
    },
  }

  return (
    <div className="space-y-6">
      {showHeader && (
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Loop</h1>
            <p className="text-muted-foreground">
              Stay connected with your hub, circles, and local crews.
            </p>
          </div>
        </div>
      )}

      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Post a Signal</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {composerTypes.map((type) => {
                const config = signalTypeConfig[type]
                const Icon = config.icon

                return (
                  <Button
                    key={type}
                    type="button"
                    variant={signalType === type ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSignalType(type)}
                  >
                    <Icon className="h-4 w-4" />
                    {config.label}
                  </Button>
                )
              })}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {signalError && (
            <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {signalError}
            </p>
          )}
          <Textarea
            value={signalText}
            onChange={(event) => {
              setSignalText(event.target.value)
              if (signalError) setSignalError('')
            }}
            placeholder="Share an update, ask for help, offer support, or organize something nearby..."
            className="min-h-[112px] resize-none"
          />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <span
              className={`text-sm ${remainingChars < 0 ? 'text-destructive' : 'text-muted-foreground'}`}
            >
              {remainingChars}
            </span>
            <Button onClick={handlePostSignal} disabled={!signalText.trim() || remainingChars < 0}>
              <Send className="h-4 w-4" />
              Post Signal
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2 overflow-x-auto overflow-y-visible pb-2 pt-1">
        {filterConfig
          .filter((item) => !hideMyUpdates || item.value !== 'my')
          .map((item) => {
            const Icon = item.icon
            return (
              <Button
                key={item.value}
                variant={filter === item.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(item.value)}
                className="flex-shrink-0"
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Button>
            )
          })}
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {filteredFeed.map((item) => {
          const config = signalTypeConfig[item.signalType]
          const Icon = config.icon

          return (
            <motion.div
              key={item.id}
              variants={itemVariants}
              whileHover={{ scale: 1.005 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className={`p-2 rounded-lg ${config.bg} flex-shrink-0`}>
                      <Icon className={`h-5 w-5 ${config.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-base truncate">{item.title}</h3>
                        <Badge variant="secondary" className="flex-shrink-0">
                          {config.label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
                        <span className="whitespace-nowrap">{item.timestamp}</span>
                        {item.author && (
                          <>
                            <span aria-hidden="true">-</span>
                            <span className="truncate">{item.author}</span>
                          </>
                        )}
                        {item.hub && (
                          <>
                            <span aria-hidden="true">-</span>
                            <span className="flex items-center gap-1 truncate">
                              <MapPin className="h-3 w-3 flex-shrink-0" />
                              <span className="truncate">{item.hub}</span>
                            </span>
                          </>
                        )}
                        {item.circle && (
                          <>
                            <span aria-hidden="true">-</span>
                            <span className="truncate">{item.circle}</span>
                          </>
                        )}
                        {item.crew && (
                          <>
                            <span aria-hidden="true">-</span>
                            <span className="truncate">{item.crew}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
                    {item.content}
                  </p>

                  <div className="flex flex-wrap items-center gap-2 text-muted-foreground">
                    {reactionConfig.map((reaction) => {
                      const ReactionIcon = reaction.icon
                      const reactionKey = `${item.id}:${reaction.value}`
                      const isActive = activeReactions.has(reactionKey)

                      return (
                        <button
                          key={reaction.value}
                          type="button"
                          onClick={() => handleReaction(item.id, reaction.value)}
                          className={`flex h-8 items-center gap-1.5 rounded-full border px-3 text-xs transition-colors ${
                            isActive
                              ? 'border-primary bg-primary/10 text-primary'
                              : 'border-border hover:border-primary/40 hover:text-foreground'
                          }`}
                        >
                          <ReactionIcon className="h-4 w-4" />
                          <span>{reaction.label}</span>
                          {item.reactions[reaction.value] > 0 && (
                            <span className="font-semibold">{item.reactions[reaction.value]}</span>
                          )}
                        </button>
                      )
                    })}
                    <button className="flex h-8 items-center gap-1.5 rounded-full border border-border px-3 text-xs transition-colors hover:border-primary/40 hover:text-foreground">
                      <MessageCircle className="h-4 w-4" />
                      <span>Comment</span>
                    </button>
                    <button className="flex h-8 items-center gap-1.5 rounded-full border border-border px-3 text-xs transition-colors hover:border-primary/40 hover:text-foreground">
                      <Share2 className="h-4 w-4" />
                      <span>Share</span>
                    </button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {filteredFeed.length === 0 && (
        <Card className="p-12">
          <div className="text-center">
            <MessageCircle className="h-12 w-12 mx-auto text-muted-foreground/50 mb-3" />
            <p className="text-muted-foreground">No Signals to show</p>
          </div>
        </Card>
      )}
    </div>
  )
}
