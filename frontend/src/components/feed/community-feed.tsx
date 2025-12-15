'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Package,
  Users,
  Calendar,
  MapPin,
  Heart,
  MessageCircle,
  Share2,
} from 'lucide-react'

type FeedItemType = 'item' | 'welcome' | 'event' | 'announcement' | 'updates'

interface FeedItem {
  id: number
  type: FeedItemType
  title: string
  content: string
  timestamp: string
  hub?: string
  author?: string
}

const mockFeedData: FeedItem[] = [
  {
    id: 1,
    type: 'welcome',
    title: 'Welcome to the community!',
    content: 'Maria Garcia just joined Hub #3. Let\'s make her feel welcome!',
    timestamp: '2 hours ago',
    hub: 'Hub #3',
  },
  {
    id: 2,
    type: 'item',
    title: 'New items available',
    content: '5 winter coats and 3 pairs of boots added to the inventory at Hub #2',
    timestamp: '4 hours ago',
    hub: 'Hub #2',
  },
  {
    id: 3,
    type: 'event',
    title: 'Community Dinner',
    content: 'Join us this Friday at 6 PM for a community dinner. All are welcome!',
    timestamp: '1 day ago',
    hub: 'Hub #1',
  },
  {
    id: 4,
    type: 'announcement',
    title: 'Hub #3 Update',
    content: 'Extended hours this week: Monday-Friday 9 AM - 8 PM',
    timestamp: '2 days ago',
    hub: 'Hub #3',
  },
]

const feedTypeConfig: Record<FeedItemType, { icon: any; color: string; bg: string }> = {
  item: { icon: Package, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  welcome: { icon: Users, color: 'text-green-500', bg: 'bg-green-500/10' },
  event: { icon: Calendar, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  announcement: { icon: MapPin, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  updates: { icon: MessageCircle, color: 'text-primary', bg: 'bg-primary/10' },
}

export function CommunityFeed() {
  const [filter, setFilter] = useState<'all' | FeedItemType>('all')
  const [hasUnreadUpdates, setHasUnreadUpdates] = useState(true)

  const filteredFeed = filter === 'all'
    ? mockFeedData
    : mockFeedData.filter(item => item.type === filter)

  const handleUpdatesClick = () => {
    setFilter('updates')
    setHasUnreadUpdates(false) // Mark updates as read
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.4 }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Community Feed</h1>
          <p className="text-muted-foreground">
            Stay updated with your hub and community
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto overflow-y-visible pb-2 pt-1">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All Updates
        </Button>
        <Button
          variant={filter === 'item' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('item')}
        >
          <Package className="h-4 w-4 mr-2" />
          Items
        </Button>
        <Button
          variant={filter === 'welcome' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('welcome')}
        >
          <Users className="h-4 w-4 mr-2" />
          Welcomes
        </Button>
        <Button
          variant={filter === 'event' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('event')}
        >
          <Calendar className="h-4 w-4 mr-2" />
          Events
        </Button>
        <Button
          variant={filter === 'announcement' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('announcement')}
        >
          <MapPin className="h-4 w-4 mr-2" />
          Announcements
        </Button>
        <div className="relative">
          <Button
            variant={filter === 'updates' ? 'default' : 'outline'}
            size="sm"
            onClick={handleUpdatesClick}
          >
            My Updates
          </Button>
          {/* Notification dot - positioned outside button like online status */}
          {hasUnreadUpdates && (
            <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 bg-primary rounded-full ring-2 ring-background" />
          )}
        </div>
      </div>

      {/* Feed */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="space-y-4"
      >
        {filteredFeed.map((item) => {
          const config = feedTypeConfig[item.type]
          const Icon = config.icon

          return (
            <motion.div
              key={item.id}
              variants={itemVariants}
              whileHover={{ scale: 1.01 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${config.bg}`}>
                      <Icon className={`h-5 w-5 ${config.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-base mb-1">{item.title}</h3>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{item.timestamp}</span>
                        {item.hub && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {item.hub}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-muted-foreground mb-4">
                    {item.content}
                  </p>
                  
                  {/* Actions (read-only for now) */}
                  <div className="flex items-center gap-4 text-muted-foreground">
                    <button className="flex items-center gap-1.5 text-xs hover:text-foreground transition-colors">
                      <Heart className="h-4 w-4" />
                      <span>Helpful</span>
                    </button>
                    <button className="flex items-center gap-1.5 text-xs hover:text-foreground transition-colors">
                      <MessageCircle className="h-4 w-4" />
                      <span>Comment</span>
                    </button>
                    <button className="flex items-center gap-1.5 text-xs hover:text-foreground transition-colors">
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
            <Users className="h-12 w-12 mx-auto text-muted-foreground/50 mb-3" />
            <p className="text-muted-foreground">No updates to show</p>
          </div>
        </Card>
      )}
    </div>
  )
}
