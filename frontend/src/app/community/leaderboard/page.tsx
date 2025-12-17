'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { DismissibleCard } from '@/components/ui/dismissible-card'
import { communityService } from '@/lib/api-services'
import { api } from '@/lib/api'
import { Sparkles, Heart, HandHeart, Users, Info } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import Link from 'next/link'

export default function LeaderboardPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  const [highlights, setHighlights] = useState<any[]>([])
  const [recentAwards, setRecentAwards] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchLeaderboard()
    }
  }, [isAuthenticated])

  const fetchLeaderboard = async () => {
    try {
      setLoading(true)
      const data = await communityService.getLeaderboard()
      // Backend returns { highlights: [...], note: '...' }
      const highlightsData = (data as any)?.highlights || data || []
      setHighlights(Array.isArray(highlightsData) ? highlightsData : [])
      
      // Fetch recent badge awards
      try {
        const badgesResponse = await api.get('/community/data/recent_badges/')
        const badgeAwards = Array.isArray(badgesResponse.data) ? badgesResponse.data : badgesResponse.data.results || []
        setRecentAwards(badgeAwards.slice(0, 4))
      } catch (badgeError) {
        console.error('Failed to fetch badges:', badgeError)
        setRecentAwards([])
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      setHighlights([]) // Set empty array on error
      toast({
        title: 'Error',
        description: 'Failed to load community highlights',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || !isAuthenticated || loading) {
    return (
      <AppLayout>
        <div className="space-y-6">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-64 w-full" />
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-yellow-500" />
            Community Highlights
          </h1>
          <p className="text-muted-foreground mt-2">
            Celebrating our community's kindness, generosity, and mutual support
          </p>
        </div>

        {/* Dignity-First Notice */}
        <DismissibleCard 
          id="leaderboard-dignity-notice"
          className="border-teal-200 bg-teal-50/50 dark:bg-teal-950/20"
        >
          <div className="flex gap-3">
            <Info className="h-5 w-5 text-teal-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-teal-900 dark:text-teal-100 mb-1">
                We celebrate without ranking
              </p>
              <p className="text-teal-700 dark:text-teal-300">
                No leaderboards, no competition. Instead, we shine a light on recent acts of kindness, 
                contributions, and community spirit. Everyone here matters equally.
              </p>
            </div>
          </div>
        </DismissibleCard>

        {/* Recent Contributors */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-red-500" />
              Recent Acts of Kindness
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {highlights.slice(0, 10).map((highlight, index) => {
                const initials = highlight.name
                  ?.split(' ')
                  .map((n: string) => n[0])
                  .join('')
                  .toUpperCase()
                  .slice(0, 2) || '🌟'
                
                return (
                  <motion.div
                    key={highlight.id || index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Link 
                      href={`/profile/${highlight.id}`}
                      className="flex items-start gap-4 p-4 rounded-lg border hover:bg-accent/50 hover:shadow-md transition-all cursor-pointer group"
                    >
                      <Avatar className="h-12 w-12 group-hover:scale-110 transition-transform">
                        <AvatarFallback className="bg-primary/10 text-primary">
                          {initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold group-hover:text-primary transition-colors">
                            {highlight.name}
                          </span>
                          <Sparkles className="w-4 h-4 text-yellow-500" />
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {highlight.gentle_note || 'Contributing to the community'}
                        </p>
                      </div>
                    </Link>
                  </motion.div>
                )
              })}
              
              {highlights.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🌱</div>
                  <p className="text-muted-foreground">
                    Be the first to make a positive impact!
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* This Month's Impact */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Items Shared</CardTitle>
              <HandHeart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,247</div>
              <p className="text-xs text-muted-foreground">
                This month across all hubs
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">New Connections</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">84</div>
              <p className="text-xs text-muted-foreground">
                Mentorship relationships formed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Community Growth</CardTitle>
              <Sparkles className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">+32%</div>
              <p className="text-xs text-muted-foreground">
                New members welcomed
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Badge Awards */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-yellow-500" />
              Recent Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {recentAwards.length === 0 ? (
                <p className="col-span-2 text-center text-muted-foreground py-4">No recent achievements yet</p>
              ) : (
                recentAwards.map((award, index) => (
                  <motion.div
                    key={award.id || index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="flex items-center gap-3 p-3 rounded-lg border"
                  >
                    <div className="text-3xl">{award.badge?.icon || '🏆'}</div>
                    <div className="flex-1">
                      <Link 
                        href={`/profile/${award.user_id}`}
                        className="font-medium text-sm hover:underline hover:text-primary"
                      >
                        {award.user_name}
                      </Link>
                      <p className="text-xs text-muted-foreground">
                        {award.badge?.name || 'Achievement'}
                      </p>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {new Date(award.awarded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </p>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </AppLayout>
  )
}
