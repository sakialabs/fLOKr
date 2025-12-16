'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
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
  Gift,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { ChatBubble } from './chat-bubble'
import { WelcomeModal } from './welcome-modal'
import { OfferItemModal } from './offer-item-modal'
import { toast } from 'sonner'
import { api } from '@/lib/api'

interface RightSidebarProps {
  collapsed: boolean
  onToggle: () => void
  shouldOpenOriChat?: boolean
}

interface Friend {
  id: string
  first_name: string
  last_name: string
  email: string
  status?: 'online' | 'offline'
  unread?: number
  connection_status?: 'none' | 'requested' | 'active' | 'declined'
  connection_id?: number
}

export function RightSidebar({ collapsed, onToggle, shouldOpenOriChat }: RightSidebarProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [activeChatId, setActiveChatId] = useState<number | null>(null)
  const [activeChatName, setActiveChatName] = useState<string>('')
  const [isOriChat, setIsOriChat] = useState(false)
  const [friends, setFriends] = useState<Friend[]>([])
  const [isLoadingFriends, setIsLoadingFriends] = useState(true)

  // Fetch real users from API
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setIsLoadingFriends(true)
        const response = await api.get('/community/data/newcomers/')
        const users = Array.isArray(response.data) ? response.data : response.data.results || []
        // Map users to friends format with random online status
        const mappedFriends = users.slice(0, 5).map((user: any) => ({
          id: user.id,
          first_name: user.name?.split(' ')[0] || 'User',
          last_name: user.name?.split(' ').slice(1).join(' ') || '',
          email: user.email || '',
          status: Math.random() > 0.5 ? 'online' : 'offline',
          unread: 0
        }))
        setFriends(mappedFriends)
      } catch (error) {
        console.error('Failed to fetch users:', error)
        // Fallback to empty array on error
        setFriends([])
      } finally {
        setIsLoadingFriends(false)
      }
    }
    fetchUsers()
  }, [])

  const filteredFriends = friends.filter(friend =>
    `${friend.first_name} ${friend.last_name}`.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const openChat = (id: number, name: string, isOri: boolean = false) => {
    setActiveChatId(id)
    setActiveChatName(name)
    setIsOriChat(isOri)
  }

  const closeChat = () => {
    setActiveChatId(null)
    setActiveChatName('')
    setIsOriChat(false)
  }

  const sendConnectionRequest = async (userId: string) => {
    try {
      await api.post('/community/mentorships/', {
        mentee: userId
      })
      toast.success('Connection request sent!')
      // Update the friend's connection status locally
      setFriends(prev => prev.map(f => 
        f.id === userId ? { ...f, connection_status: 'requested' } : f
      ))
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to send connection request')
    }
  }

  const [showOfferModal, setShowOfferModal] = useState(false)
  const [showWelcomeModal, setShowWelcomeModal] = useState(false)

  const handleOfferItem = () => {
    setShowOfferModal(true)
  }

  const handleWelcomeSomeone = () => {
    setShowWelcomeModal(true)
  }

  // Handle opening Ori chat from external trigger
  useEffect(() => {
    if (shouldOpenOriChat) {
      openChat(999, 'Ori', true)
    }
  }, [shouldOpenOriChat])

  if (collapsed) {
    return (
      <motion.aside
        initial={false}
        animate={{ width: 60 }}
        className="border-l border-border bg-card flex flex-col py-4"
      >
        <div className="flex justify-center">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="hover:bg-muted"
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>
        </div>
        
        {/* Section Icons - in order of appearance */}
        <div className="flex flex-col items-center gap-4 pt-6">
          <button 
            onClick={onToggle}
            className="flex flex-col items-center gap-1.5 hover:opacity-70 transition-opacity"
          >
            <div className="flex items-center justify-center w-10 h-10">
              <MapPin className="h-5 w-5 text-muted-foreground" />
            </div>
            <span className="text-[10px] text-muted-foreground text-center">Hub</span>
          </button>
          
          <button 
            onClick={onToggle}
            className="flex flex-col items-center gap-1.5 hover:opacity-70 transition-opacity"
          >
            <div className="flex items-center justify-center w-10 h-10">
              <Users className="h-5 w-5 text-muted-foreground" />
            </div>
            <span className="text-[10px] text-muted-foreground text-center">Pulse</span>
          </button>
          
          <button 
            onClick={handleOfferItem}
            className="flex flex-col items-center gap-1.5 hover:opacity-70 transition-opacity"
          >
            <div className="flex items-center justify-center w-10 h-10">
              <Gift className="h-5 w-5 text-muted-foreground" />
            </div>
            <span className="text-[10px] text-muted-foreground text-center">Actions</span>
          </button>
          
          <button 
            onClick={onToggle}
            className="flex flex-col items-center gap-1.5 hover:opacity-70 transition-opacity"
          >
            <div className="flex items-center justify-center w-10 h-10">
              <MessageCircle className="h-5 w-5 text-muted-foreground" />
            </div>
            <span className="text-[10px] text-muted-foreground text-center">Messages</span>
          </button>
        </div>
      </motion.aside>
    )
  }

  return (
    <motion.aside
      initial={false}
      animate={{ width: 320 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="border-l border-border bg-card flex flex-col overflow-hidden flex-shrink-0"
    >
      {/* Header */}
      <div className="h-14 flex items-center justify-between px-3 border-b border-border flex-shrink-0">
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
        <div className="p-3 border-b border-border">
          <h3 className="text-xs font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Your Hub</h3>
          <Card className="bg-muted/30">
            <CardContent className="p-3 space-y-2">
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
        <div className="p-3 border-b border-border">
          <h3 className="text-xs font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Community Pulse</h3>
          <div className="space-y-2">
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
        <div className="p-3 border-b border-border">
          <h3 className="text-xs font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Quick Actions</h3>
          <div className="space-y-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full justify-start"
              onClick={handleOfferItem}
            >
              <Gift className="h-4 w-4 mr-2" />
              Offer an item
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full justify-start"
              onClick={handleWelcomeSomeone}
            >
              <Heart className="h-4 w-4 mr-2" />
              Welcome someone
            </Button>
          </div>
        </div>

        {/* Messages Section */}
        <div className="p-3">
          <h3 className="text-xs font-semibold mb-2 text-muted-foreground uppercase tracking-wide">Messages</h3>
          
          {/* Search */}
          <div className="relative mb-2">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Contacts List */}
          <div className="space-y-1">
            {/* Ori AI - Styled like other friends */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => openChat(-1, 'Ori', true)}
              className="w-full flex items-center gap-3 p-2.5 rounded-lg transition-colors hover:bg-muted"
            >
              {/* Ori Avatar - Simple, no stripes */}
              <div className="relative">
                <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#D97A5B] to-[#C26A52] flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                {/* Always Online Badge */}
                <Circle className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 fill-green-500 text-green-500" />
              </div>

              {/* Name & Status */}
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-medium truncate">Ori</p>
                <p className="text-xs text-muted-foreground">
                  AI Assistant
                </p>
              </div>
            </motion.button>
            {isLoadingFriends ? (
              <div className="py-4 text-center">
                <p className="text-sm text-muted-foreground">Loading...</p>
              </div>
            ) : filteredFriends.length === 0 ? (
              <div className="py-8 text-center">
                <MessageCircle className="h-10 w-10 mx-auto text-muted-foreground/50 mb-2" />
                <p className="text-sm text-muted-foreground">No friends found</p>
              </div>
            ) : (
              filteredFriends.map((friend) => (
              <motion.div
                key={friend.id}
                whileHover={{ scale: 1.01 }}
                className="w-full flex items-center gap-3 p-2.5 rounded-lg transition-colors hover:bg-muted"
              >
                {/* Avatar */}
                <div className="relative flex-shrink-0">
                  <div className="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold text-sm">
                    {friend.first_name[0]}{friend.last_name[0]}
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
                  <p className="text-sm font-medium truncate">{friend.first_name} {friend.last_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {friend.connection_status === 'active' ? 'Connected' : friend.status}
                  </p>
                </div>

                {/* Action Button */}
                {friend.connection_status === 'active' ? (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openChat(Number(friend.id), `${friend.first_name} ${friend.last_name}`, false)}
                    className="h-7 px-2"
                  >
                    <MessageCircle className="h-3.5 w-3.5" />
                  </Button>
                ) : friend.connection_status === 'requested' ? (
                  <span className="text-xs text-muted-foreground px-2">Pending</span>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => sendConnectionRequest(friend.id)}
                    className="h-7 px-3 text-xs"
                  >
                    Connect
                  </Button>
                )}
              </motion.div>
            ))
            )}
          </div>
        </div>

      </div>

      {/* Chat Bubble */}
      {activeChatId !== null && (
        <ChatBubble
          isOpen={activeChatId !== null}
          onClose={closeChat}
          chatWith={{
            id: activeChatId,
            name: activeChatName,
            isOri: isOriChat
          }}
          sidebarCollapsed={collapsed}
        />
      )}

      {/* Offer Item Modal */}
      <OfferItemModal
        isOpen={showOfferModal}
        onClose={() => setShowOfferModal(false)}
      />

      {/* Welcome Modal */}
      <WelcomeModal
        isOpen={showWelcomeModal}
        onClose={() => setShowWelcomeModal(false)}
      />
    </motion.aside>
  )
}
