'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, Award, Heart, Calendar, Megaphone, MessageCircle } from 'lucide-react'
import { api } from '@/lib/api'
import { toast } from 'sonner'

interface Newcomer {
  id: string
  name: string
  joined_days_ago: number
  hub: string
  language: string
}

interface BadgeAward {
  id: string
  user_id: string
  user_name: string
  badge: {
    name: string
    description: string
    category: string
  }
  awarded_at: string
}

interface Event {
  id: string
  title: string
  description: string
  event_type: string
  event_date: string
  hub_name: string
  organizer_name: string
}

interface Announcement {
  id: string
  title: string
  content: string
  priority: string
  hub_name: string
  active_until: string
}

interface Feedback {
  id: string
  user_id: string
  user_name: string
  item_name: string
  comment: string
  rating: number
  created_at: string
}

export default function CommunityPage() {
  const router = useRouter()
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth)
  const [newcomers, setNewcomers] = useState<Newcomer[]>([])
  const [recentBadges, setRecentBadges] = useState<BadgeAward[]>([])
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([])
  const [announcements, setAnnouncements] = useState<Announcement[]>([])
  const [successStories, setSuccessStories] = useState<Feedback[]>([])
  const [mentorshipCount, setMentorshipCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [connectingUsers, setConnectingUsers] = useState<Set<string>>(new Set())

  const sendConnectionRequest = async (userId: string) => {
    if (connectingUsers.has(userId)) return
    
    setConnectingUsers(prev => new Set(prev).add(userId))
    try {
      await api.post('/community/mentorships/', {
        mentee: userId
      })
      toast.success('Connection request sent!')
    } catch (error) {
      const err = error as { response?: { data?: { error?: string } } }
      toast.error(err.response?.data?.error || 'Failed to send connection request')
      setConnectingUsers(prev => {
        const newSet = new Set(prev)
        newSet.delete(userId)
        return newSet
      })
    }
  }

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchCommunityData()
    }
  }, [isAuthenticated])

  const fetchCommunityData = async () => {
    try {
      // Fetch all community data in parallel
      const [newcomersRes, badgesRes, eventsRes, announcementsRes, feedbackRes, mentorshipRes] = await Promise.all([
        api.get('/community/data/newcomers/'),
        api.get('/community/user-badges/?recent=true'),
        api.get('/hubs/events/?upcoming=true'),
        api.get('/hubs/announcements/?active_only=true'),
        api.get('/community/feedback/?positive_only=true'),
        api.get('/community/data/mentorship_opportunities/'),
      ])

      // Handle both paginated (ViewSet) and non-paginated responses
      const newcomersData = Array.isArray(newcomersRes.data) ? newcomersRes.data : newcomersRes.data.results || []
      const badgesData = Array.isArray(badgesRes.data) ? badgesRes.data : badgesRes.data.results || []
      const eventsData = Array.isArray(eventsRes.data) ? eventsRes.data : eventsRes.data.results || []
      const announcementsData = Array.isArray(announcementsRes.data) ? announcementsRes.data : announcementsRes.data.results || []
      const feedbackData = Array.isArray(feedbackRes.data) ? feedbackRes.data : feedbackRes.data.results || []
      const mentorshipData = Array.isArray(mentorshipRes.data) ? mentorshipRes.data : mentorshipRes.data.results || []

      setNewcomers(newcomersData.slice(0, 5))
      setRecentBadges(badgesData.slice(0, 5))
      setUpcomingEvents(eventsData.slice(0, 5))
      setAnnouncements(announcementsData.slice(0, 5))
      setSuccessStories(feedbackData.slice(0, 5))
      setMentorshipCount(mentorshipData.length || 0)
    } catch (error) {
      console.error('Failed to fetch community data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (loading || !isAuthenticated || isLoading) {
    return null
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
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
    <AppLayout>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="space-y-6"
      >
        {/* Community Header */}
        <motion.div variants={itemVariants}>
          <h1 className="text-3xl font-bold tracking-tight">Community Space</h1>
          <p className="text-muted-foreground">
            What&apos;s happening across our community
          </p>
        </motion.div>

        {/* All Cards in Responsive Grid */}
        <div className="grid gap-6 lg:grid-cols-2">
        {/* Welcome New Members */}
        {newcomers.length > 0 && (
          <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-green-500" />
                <CardTitle>Welcome New Members</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {newcomers.map((newcomer) => (
                <div key={newcomer.id} className="flex items-center justify-between gap-3 p-3 bg-green-500/5 rounded-lg border border-green-500/10 min-w-0">
                  <div className="min-w-0 flex-1">
                    <Link href={`/profile/${newcomer.id}`} className="font-medium truncate hover:text-primary hover:underline transition-colors">
                      {newcomer.name}
                    </Link>
                    <p className="text-xs text-muted-foreground truncate">
                      Joined {newcomer.joined_days_ago} {newcomer.joined_days_ago === 1 ? 'day' : 'days'} ago · {newcomer.hub}
                    </p>
                  </div>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => sendConnectionRequest(newcomer.id)}
                    disabled={connectingUsers.has(newcomer.id)}
                    className="flex-shrink-0"
                  >
                    {connectingUsers.has(newcomer.id) ? 'Pending' : 'Connect'}
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Community Achievements */}
        {recentBadges.length > 0 && (
          <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-amber-500" />
                <CardTitle>Community Achievements</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              {recentBadges.map((award) => (
                <div key={award.id} className="flex items-center gap-3 p-3 bg-amber-500/5 rounded-lg border border-amber-500/10 min-w-0">
                  <Award className="h-5 w-5 text-amber-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      <Link href={`/profile/${award.user_id || award.id}`} className="hover:text-primary hover:underline transition-colors">
                        {award.user_name}
                      </Link> earned &quot;{award.badge.name}&quot;
                    </p>
                    <p className="text-xs text-muted-foreground line-clamp-2">{award.badge.description}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Upcoming Events */}
        {upcomingEvents.length > 0 && (
          <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-500" />
                <CardTitle>Upcoming Events</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {upcomingEvents.map((event) => (
                <div key={event.id} className="p-3 bg-blue-500/5 rounded-lg border border-blue-500/10 min-w-0">
                  <div className="flex items-start justify-between gap-3 min-w-0">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{event.title}</p>
                      <p className="text-xs text-muted-foreground mt-1 truncate">
                        {new Date(event.event_date).toLocaleDateString()} · {event.hub_name}
                      </p>
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{event.description}</p>
                    </div>
                    <Button size="sm" variant="outline" className="flex-shrink-0">Details</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Hub Announcements */}
        {announcements.length > 0 && (
          <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Megaphone className="h-5 w-5 text-orange-500" />
                <CardTitle>Hub Announcements</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {announcements.map((announcement) => (
                <div key={announcement.id} className="p-3 bg-orange-500/5 rounded-lg border border-orange-500/10 min-w-0">
                  <div className="flex items-start gap-3 min-w-0">
                    <Megaphone className="h-5 w-5 text-orange-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-medium truncate flex-1 min-w-0">{announcement.title}</p>
                        {announcement.priority === 'high' && (
                          <span className="px-2 py-0.5 bg-orange-500 text-white text-xs rounded-full whitespace-nowrap flex-shrink-0">High Priority</span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 truncate">{announcement.hub_name}</p>
                      <p className="text-sm mt-2 line-clamp-3">{announcement.content}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Active Mentorships */}
        {mentorshipCount > 0 && (
          <motion.div variants={itemVariants}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5 text-purple-500" />
                <CardTitle>Active Mentorships</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between gap-3 p-4 bg-purple-500/5 rounded-lg border border-purple-500/10 min-w-0">
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate">{mentorshipCount} active mentorship connections</p>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                    Community members helping newcomers settle in
                  </p>
                </div>
                <Button size="sm" className="flex-shrink-0">Learn More</Button>
              </div>
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Success Stories */}
        {successStories.length > 0 && (
          <motion.div variants={itemVariants} className={successStories.length === 1 && (newcomers.length + recentBadges.length + upcomingEvents.length + announcements.length + (mentorshipCount > 0 ? 1 : 0)) % 2 === 0 ? 'lg:col-span-2' : ''}>
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-pink-500" />
                <CardTitle>Community Stories</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {successStories.map((story) => (
                <div key={story.id} className="p-4 bg-pink-500/5 rounded-lg border border-pink-500/10 min-w-0">
                  <div className="flex items-start gap-3 min-w-0">
                    <Heart className="h-5 w-5 text-pink-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm italic line-clamp-3">&quot;{story.comment}&quot;</p>
                      <p className="text-xs text-muted-foreground mt-2 truncate">
                        — <Link href={`/profile/${story.user_id}`} className="hover:text-primary hover:underline transition-colors">
                          {story.user_name}
                        </Link> · {story.item_name}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}
        </div>
      </motion.div>
    </AppLayout>
  )
}

