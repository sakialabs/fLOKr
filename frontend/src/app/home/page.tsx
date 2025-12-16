'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar, Package, Sparkles, AlertCircle, CheckCircle, Clock } from 'lucide-react'
import { api } from '@/lib/api'

interface DashboardData {
  summary: {
    upcoming_returns_count: number
    overdue_count: number
    ready_for_pickup_count: number
    active_reservations_count: number
    total_borrowed: number
    on_time_returns: number
  }
  active_reservations: any[]
  upcoming_returns: any[]
  pending_reservations: any[]
  overdue_items: any[]
}

interface OriSuggestion {
  item: {
    id: string
    name: string
    category: string
    hub: string
  }
  score: number
  reasons: string[]
}

export default function HomePage() {
  const router = useRouter()
  const { isAuthenticated, loading, user } = useSelector((state: RootState) => state.auth)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [oriSuggestions, setOriSuggestions] = useState<OriSuggestion[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData()
      fetchOriSuggestions()
    }
  }, [isAuthenticated])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/auth/dashboard/')
      setDashboardData(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchOriSuggestions = async () => {
    try {
      const response = await api.get('/ori/recommendations/?limit=3')
      setOriSuggestions(response.data)
    } catch (error) {
      console.error('Failed to fetch Ori suggestions:', error)
    }
  }

  if (loading || !isAuthenticated || isLoading) {
    return null
  }

  const { summary } = dashboardData || { summary: {} }

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
    <AppLayout>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="space-y-6"
      >
        {/* Personal Header */}
        <motion.div variants={itemVariants}>
          <h1 className="text-2xl font-bold mb-1">My Home</h1>
          <p className="text-sm text-muted-foreground">Your personal dashboard for tasks and updates</p>
        </motion.div>

        {/* At a Glance - Real Data */}
        <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-4">At a Glance</h2>
            <div className="grid gap-4 md:grid-cols-3">
              {/* Upcoming Returns */}
              <div className="flex items-start gap-3 min-w-0">
                <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                  <Calendar className="h-5 w-5 text-amber-500" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">Upcoming Returns</p>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                    {summary.upcoming_returns_count || 0} items due this week
                  </p>
                </div>
              </div>

              {/* Active Reservations */}
              <div className="flex items-start gap-3 min-w-0">
                <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                  <Package className="h-5 w-5 text-blue-500" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">Active Reservations</p>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                    {summary.ready_for_pickup_count || 0} ready for pickup
                  </p>
                </div>
              </div>

              {/* Ori Suggestions */}
              <div className="flex items-start gap-3 min-w-0">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[#D97A5B] to-[#C26A52] flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-5 w-5 text-white" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">Ori Suggests</p>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                    {oriSuggestions.length} personalized recommendations
                  </p>
                </div>
              </div>
            </div>

            {/* Overdue Alert */}
            {summary.overdue_count > 0 && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <p className="text-sm text-red-700 dark:text-red-400">
                  You have {summary.overdue_count} overdue {summary.overdue_count === 1 ? 'item' : 'items'}. Please return them soon.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
        </motion.div>

        {/* My Active Reservations */}
        {dashboardData?.active_reservations && dashboardData.active_reservations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Items I'm Borrowing</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {dashboardData.active_reservations.map((reservation: any) => (
                <div key={reservation.id} className="flex items-center justify-between gap-3 p-3 bg-muted/50 rounded-lg min-w-0">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <Package className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium truncate">{reservation.item.name}</p>
                      <p className="text-xs text-muted-foreground truncate">Due: {new Date(reservation.expected_return_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <Button size="sm" variant="outline" className="flex-shrink-0">View</Button>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Ori Personal Suggestions */}
        {oriSuggestions.length > 0 && (
          <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2 min-w-0">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#D97A5B] to-[#C26A52] flex items-center justify-center flex-shrink-0">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <CardTitle className="text-lg truncate">Ori's Suggestions for You</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {oriSuggestions.map((suggestion: OriSuggestion, index: number) => (
                <div key={index} className="p-3 bg-muted/30 rounded-lg min-w-0">
                  <div className="flex items-start justify-between gap-3 min-w-0">
                    <div className="min-w-0 flex-1">
                      <p className="font-medium truncate">{suggestion.item.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 truncate">{suggestion.item.category}</p>
                      {suggestion.reasons && suggestion.reasons[0] && (
                        <p className="text-xs text-muted-foreground mt-1 italic line-clamp-2">"{suggestion.reasons[0]}"</p>
                      )}
                    </div>
                    <Button size="sm" className="flex-shrink-0">Reserve</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          </motion.div>
        )}

        {/* Quick Actions */}
        <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 sm:gap-3">
              <Button variant="outline" className="justify-start min-w-0" onClick={() => router.push('/items')}>
                <Package className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">Browse Items</span>
              </Button>
              <Button variant="outline" className="justify-start min-w-0" onClick={() => router.push('/reservations')}>
                <Calendar className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">My Reservations</span>
              </Button>
              <Button variant="outline" className="justify-start min-w-0" onClick={() => router.push('/hubs')}>
                <Clock className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">Find Nearby Hub</span>
              </Button>
              <Button variant="outline" className="justify-start min-w-0" onClick={() => {
                const event = new CustomEvent('openOriChat')
                window.dispatchEvent(event)
              }}>
                <Sparkles className="h-4 w-4 mr-2 flex-shrink-0" />
                <span className="truncate">Ask Ori</span>
              </Button>
            </div>
          </CardContent>
        </Card>
        </motion.div>
      </motion.div>
    </AppLayout>
  )
}
