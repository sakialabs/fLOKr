'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronRight, 
  ChevronLeft, 
  Search, 
  MessageCircle, 
  Circle,
  MapPin,
  Clock,
  Users,
  Package,
  Calendar,
  Heart,
  HelpCircle,
  Gift
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface RightSidebarProps {
  collapsed: boolean
  onToggle: () => void
}

// Mock friends data
const mockFriends = [
  { id: 1, name: 'Sarah Chen', status: 'online', unread: 2 },
  { id: 2, name: 'Ahmed Hassan', status: 'online', unread: 0 },
  { id: 3, name: 'Maria Garcia', status: 'offline', unread: 0 },
  { id: 4, name: 'John Smith', status: 'online', unread: 1 },
  { id: 5, name: 'Priya Patel', status: 'offline', unread: 0 },
]

export function RightSidebar({ collapsed, onToggle }: RightSidebarProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFriend, setSelectedFriend] = useState<number | null>(null)

  const filteredFriends = mockFriends.filter(friend =>
    friend.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (collapsed) {
    return (
      <motion.aside
        initial={false}
        animate={{ width: 60 }}
        className="border-l border-border bg-card flex flex-col items-center py-4 gap-4"
      >
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="hover:bg-muted"
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        
        {/* Section Icons - in order of appearance */}
        <div className="flex flex-col items-center gap-4 pt-2">
          <div className="flex flex-col items-center gap-1">
            <MapPin className="h-5 w-5 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">Hub</span>
          </div>
          
          <div className="flex flex-col items-center gap-1">
            <Users className="h-5 w-5 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">Pulse</span>
          </div>
          
          <div className="flex flex-col items-center gap-1">
            <Gift className="h-5 w-5 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">Actions</span>
          </div>
          
          <div className="flex flex-col items-center gap-1">
            <MessageCircle className="h-5 w-5 text-muted-foreground" />
            <span className="text-[10px] text-muted-foreground">Friends</span>
          </div>
        </div>
      </motion.aside>
    )
  }

  return (
    <motion.aside
      initial={false}
      animate={{ width: 340 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="border-l border-border bg-card flex flex-col overflow-y-auto"
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border flex-shrink-0">
        <h2 className="text-lg font-semibold">Community</h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="hover:bg-muted"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Hub Snapshot */}
        <div className="p-4 border-b border-border">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Your Hub</h3>
          <Card className="bg-muted/30">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin className="h-4 w-4 text-primary" />
                    <p className="font-semibold">Hub #3 - Eastside</p>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <div className="h-2 w-2 rounded-full bg-green-500" />
                    <span className="text-muted-foreground">Open now</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>Today: 9 AM - 6 PM</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Community Pulse */}
        <div className="p-4 border-b border-border">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Community Pulse</h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3 text-sm">
              <Users className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <p className="text-muted-foreground">3 newcomers joined this week</p>
            </div>
            <div className="flex items-start gap-3 text-sm">
              <Package className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <p className="text-muted-foreground">12 items shared today</p>
            </div>
            <div className="flex items-start gap-3 text-sm">
              <Calendar className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <p className="text-muted-foreground">Next event: Friday at 6 PM</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="p-4 border-b border-border">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Quick Actions</h3>
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Gift className="h-4 w-4 mr-2" />
              Offer an item
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <HelpCircle className="h-4 w-4 mr-2" />
              Ask for help
            </Button>
            <Button variant="outline" size="sm" className="w-full justify-start">
              <Heart className="h-4 w-4 mr-2" />
              Welcome someone
            </Button>
          </div>
        </div>

        {/* Friends Section */}
        <div className="p-4">
          <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Friends</h3>
          
          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search friends..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Friends List */}
          <div className="space-y-1">
            {filteredFriends.map((friend) => (
              <motion.button
                key={friend.id}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedFriend(friend.id)}
                className={`w-full flex items-center gap-3 p-2.5 rounded-lg transition-colors ${
                  selectedFriend === friend.id
                    ? 'bg-primary/10 border border-primary/20'
                    : 'hover:bg-muted'
                }`}
              >
                {/* Avatar */}
                <div className="relative">
                  <div className="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
                    {friend.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  {/* Online Status */}
                  <Circle
                    className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 ${
                      friend.status === 'online'
                        ? 'fill-green-500 text-green-500'
                        : 'fill-gray-400 text-gray-400'
                    }`}
                  />
                </div>

                {/* Name & Status */}
                <div className="flex-1 text-left min-w-0">
                  <p className="text-sm font-medium truncate">{friend.name}</p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {friend.status}
                  </p>
                </div>

                {/* Unread Badge */}
                {friend.unread > 0 && (
                  <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-xs font-semibold text-primary-foreground">
                      {friend.unread}
                    </span>
                  </div>
                )}
              </motion.button>
            ))}

            {filteredFriends.length === 0 && (
              <div className="py-8 text-center">
                <MessageCircle className="h-10 w-10 mx-auto text-muted-foreground/50 mb-2" />
                <p className="text-sm text-muted-foreground">No friends found</p>
              </div>
            )}
          </div>
        </div>

        {/* Chat Preview (when friend selected) */}
        <AnimatePresence>
          {selectedFriend && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 180, opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="border-t border-border bg-muted/30 overflow-hidden"
            >
              <div className="p-4 h-full flex flex-col">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-semibold">
                    {mockFriends.find(f => f.id === selectedFriend)?.name}
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedFriend(null)}
                  >
                    Close
                  </Button>
                </div>
                <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
                  Chat coming soon...
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.aside>
  )
}
