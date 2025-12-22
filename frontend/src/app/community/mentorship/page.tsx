'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { DismissibleCard } from '@/components/ui/dismissible-card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { communityService, UserProfile, MentorshipConnection } from '@/lib/api-services'
import { Users, Send, Check, X, MessageCircle, Heart, Globe } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import Link from 'next/link'

export default function MentorshipPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { isAuthenticated, loading: authLoading, user } = useSelector((state: RootState) => state.auth)
  const [mentors, setMentors] = useState<UserProfile[]>([])
  const [myConnections, setMyConnections] = useState<MentorshipConnection[]>([])
  const [loading, setLoading] = useState(true)
  const [requesting, setRequesting] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])
  const fetchData = async () => {
    try {
      setLoading(true)
      const [mentorsData, connectionsData] = await Promise.all([
        communityService.findMentors(),
        communityService.getMentorships()
      ])
      // Ensure arrays are valid before setting state
      setMentors(Array.isArray(mentorsData) ? mentorsData : [])
      setMyConnections(Array.isArray(connectionsData) ? connectionsData : [])
    } catch (error) {
      console.error('Error fetching mentorship data:', error)
      // Set empty arrays on error
      setMentors([])
      setMyConnections([])
      toast({
        title: 'Error',
        description: 'Failed to load mentorship data',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRequestMentorship = async (mentorId: string) => {
    setRequesting(mentorId)
    try {
      await communityService.requestMentorship(mentorId)
      toast({
        title: '🤝 Request Sent!',
        description: 'The mentor will review your request soon'
      })
      fetchData()
    } catch (error) {
      console.error('Error requesting mentorship:', error)
      toast({
        title: 'Error',
        description: 'Failed to send mentorship request',
        variant: 'destructive'
      })
    } finally {
      setRequesting(null)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchData()
    }
  }, [isAuthenticated])

  const handleAccept = async (connectionId: string) => {
    try {
      await communityService.acceptMentorship(connectionId)
      toast({
        title: '✅ Mentorship Accepted!',
        description: 'Your mentorship journey begins'
      })
      fetchData()
    } catch (error) {
      console.error('Error accepting mentorship:', error)
      toast({
        title: 'Error',
        description: 'Failed to accept mentorship',
        variant: 'destructive'
      })
    }
  }

  const handleDecline = async (connectionId: string) => {
    try {
      await communityService.declineMentorship(connectionId)
      toast({
        title: 'Request Declined',
        description: 'The request has been declined'
      })
      fetchData()
    } catch (error) {
      console.error('Error declining mentorship:', error)
      toast({
        title: 'Error',
        description: 'Failed to decline mentorship',
        variant: 'destructive'
      })
    }
  }

  if (authLoading || !isAuthenticated || loading) {
    return (
      <AppLayout>
        <div className="space-y-6">
          <Skeleton className="h-10 w-64" />
          <div className="grid gap-4 md:grid-cols-2">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-48" />
            ))}
          </div>
        </div>
      </AppLayout>
    )
  }

  // Ensure myConnections is an array before filtering
  const safeConnections = Array.isArray(myConnections) ? myConnections : []
  const pendingRequests = safeConnections.filter(c => c.status === 'requested')
  const activeConnections = safeConnections.filter(c => c.status === 'active')

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-8 w-8" />
            Mentorship
          </h1>
          <p className="text-muted-foreground mt-2">
            Connect with experienced community members who can guide your journey
          </p>
        </div>

        {/* Info Card */}
        <DismissibleCard 
          id="mentorship-info-notice"
          className="border-teal-200 bg-teal-50/50 dark:bg-teal-950/20"
        >
          <div className="flex gap-3">
            <Heart className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-teal-900 dark:text-teal-100 mb-1">
                Support & Guidance
              </p>
              <p className="text-teal-700 dark:text-teal-300">
                Mentors are experienced community members who volunteer their time to help newcomers 
                settle in, navigate resources, and build confidence.
              </p>
            </div>
          </div>
        </DismissibleCard>

        <Tabs defaultValue="find">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="find">Find Mentors</TabsTrigger>
            <TabsTrigger value="active">
              Active ({activeConnections.length})
            </TabsTrigger>
            <TabsTrigger value="requests">
              Requests ({pendingRequests.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="find" className="space-y-4 mt-4">
            {mentors.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {mentors.map((mentor, index) => {
                  const initials = mentor.full_name
                    .split(' ')
                    .map(n => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2)

                  const alreadyConnected = myConnections.some(
                    c => c.mentor.id === mentor.id && ['requested', 'active'].includes(c.status)
                  )

                  return (
                    <motion.div
                      key={mentor.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Card className="hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-start gap-4">
                            {/* Clickable Avatar */}
                            <Link href={`/profile/${mentor.id}`}>
                              <Avatar className="h-14 w-14 cursor-pointer hover:ring-2 hover:ring-primary transition-all">
                                <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                                  {initials}
                                </AvatarFallback>
                              </Avatar>
                            </Link>
                            
                            <div className="flex-1 min-w-0">
                              {/* Name and Achievement Badge */}
                              <div className="flex items-center justify-between gap-3 mb-2">
                                <Link 
                                  href={`/profile/${mentor.id}`}
                                  className="font-semibold text-lg hover:text-primary transition-colors"
                                >
                                  {mentor.full_name}
                                </Link>
                                {/* Achievement Badge - Informative */}
                                {mentor.badges_earned && mentor.badges_earned.length > 0 && (
                                  <Badge variant="secondary" className="text-sm font-medium shrink-0 flex items-center gap-1.5">
                                    <span>{mentor.badges_earned[0].badge.icon}</span>
                                    <span>{mentor.badges_earned[0].badge.name}</span>
                                    {mentor.badges_earned.length > 1 && (
                                      <span className="text-xs opacity-75">+{mentor.badges_earned.length - 1}</span>
                                    )}
                                  </Badge>
                                )}
                              </div>
                              
                              {/* Languages - Full names with proper spacing */}
                              {mentor.languages_spoken && (
                                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
                                  <Globe className="h-3.5 w-3.5 flex-shrink-0" />
                                  <span>
                                    {(() => {
                                      // Map common language codes to full names
                                      const languageMap: Record<string, string> = {
                                        'en': 'English',
                                        'fr': 'French',
                                        'es': 'Spanish',
                                        'ar': 'Arabic',
                                        'zh': 'Mandarin',
                                        'ur': 'Urdu',
                                        'tl': 'Tagalog',
                                        'pt': 'Portuguese',
                                        'hi': 'Hindi',
                                        'bn': 'Bengali',
                                        'pa': 'Punjabi'
                                      };
                                      
                                      const spokenLangs = mentor.languages_spoken
                                      let languages: string[] = []
                                      
                                      // Handle array format
                                      if (Array.isArray(spokenLangs)) {
                                        languages = spokenLangs
                                      } 
                                      // Handle comma-separated string (e.g., "en,es" or "English, Arabic")
                                      else if (typeof spokenLangs === 'string') {
                                        languages = spokenLangs.split(',').map((l: string) => l.trim())
                                      }
                                      
                                      // Map codes to full names, keeping already full names as-is
                                      return languages
                                        .map((lang: string) => languageMap[lang.toLowerCase()] || lang)
                                        .join(', ');
                                    })()}
                                  </span>
                                </div>
                              )}
                              
                              {/* Request Button - Medium size, full width on mobile */}
                              <Button
                                onClick={() => handleRequestMentorship(mentor.id)}
                                disabled={alreadyConnected || requesting === mentor.id}
                                className="w-full sm:w-auto"
                              >
                                {alreadyConnected ? (
                                  <>
                                    <Check className="h-4 w-4 mr-2" />
                                    Connected
                                  </>
                                ) : (
                                  <>
                                    <Send className="h-4 w-4 mr-2" />
                                    {requesting === mentor.id ? 'Sending...' : 'Request Mentorship'}
                                  </>
                                )}
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="text-4xl mb-2">🌱</div>
                  <p className="text-muted-foreground">
                    No mentors available at the moment. Check back soon!
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="active" className="space-y-4 mt-4">
            {activeConnections.length > 0 ? (
              <div className="space-y-3">
                {activeConnections.map((connection) => {
                  const isMentor = connection.mentor.id === user?.id
                  const otherPerson = isMentor ? connection.mentee : connection.mentor
                  
                  return (
                    <Card key={connection.id}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Link href={`/profile/${otherPerson.id}`}>
                              <Avatar className="cursor-pointer hover:ring-2 hover:ring-primary transition-all">
                                <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                                  {otherPerson.full_name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                                </AvatarFallback>
                              </Avatar>
                            </Link>
                            <div>
                              <Link 
                                href={`/profile/${otherPerson.id}`}
                                className="font-semibold hover:text-primary hover:underline transition-colors"
                              >
                                {otherPerson.full_name}
                              </Link>
                              <p className="text-sm text-muted-foreground">
                                {isMentor ? 'You are mentoring' : 'Your mentor'}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Since {new Date(connection.start_date || connection.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <Button variant="outline" size="sm" asChild>
                            <Link href={`/messages/${connection.id}`}>
                              <MessageCircle className="h-4 w-4 mr-2" />
                              Message
                            </Link>
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="text-4xl mb-2">🤝</div>
                  <p className="text-muted-foreground">
                    No active mentorship connections yet
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="requests" className="space-y-4 mt-4">
            {pendingRequests.length > 0 ? (
              <div className="space-y-3">
                {pendingRequests.map((connection) => {
                  const isMentor = connection.mentor.id === user?.id
                  const otherPerson = isMentor ? connection.mentee : connection.mentor
                  
                  return (
                    <Card key={connection.id}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Link href={`/profile/${otherPerson.id}`}>
                              <Avatar className="cursor-pointer hover:ring-2 hover:ring-primary transition-all">
                                <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                                  {otherPerson.full_name?.split(' ').map((n: string) => n[0]).join('').slice(0, 2)}
                                </AvatarFallback>
                              </Avatar>
                            </Link>
                            <div>
                              <Link 
                                href={`/profile/${otherPerson.id}`}
                                className="font-semibold hover:text-primary hover:underline transition-colors"
                              >
                                {otherPerson.full_name}
                              </Link>
                              <p className="text-sm text-muted-foreground">
                                {isMentor ? 'Wants you as a mentor' : 'Request sent'}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(connection.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          {isMentor ? (
                            <div className="flex gap-2">
                              <Button 
                                size="sm" 
                                onClick={() => handleAccept(connection.id)}
                              >
                                <Check className="h-4 w-4 mr-2" />
                                Accept
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleDecline(connection.id)}
                              >
                                <X className="h-4 w-4 mr-2" />
                                Decline
                              </Button>
                            </div>
                          ) : (
                            <Badge>Pending</Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="text-4xl mb-2">📬</div>
                  <p className="text-muted-foreground">
                    No pending requests
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </motion.div>
    </AppLayout>
  )
}
