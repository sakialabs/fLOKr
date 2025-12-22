'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { reservationService, Reservation } from '@/lib/api-services'
import { Calendar, Clock, Package, MapPin, AlertCircle, CheckCircle, XCircle, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { format } from 'date-fns'
import { toast } from 'sonner'

export default function ReservationsPage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchReservations()
    }
  }, [isAuthenticated])

  const fetchReservations = async () => {
    try {
      setLoading(true)
      const data = await reservationService.getAll()
      // Ensure data is always an array
      setReservations(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to fetch reservations:', error)
      toast.error('Failed to load reservations')
      setReservations([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id: string) => {
    try {
      await reservationService.cancel(id)
      toast.success('Reservation cancelled successfully')
      fetchReservations()
    } catch (error) {
      console.error('Failed to cancel reservation:', error)
      toast.error('Failed to cancel reservation')
    }
  }

  const handleExtend = async (id: string) => {
    try {
      await reservationService.requestExtension(id)
      toast.success('Extension request submitted')
      fetchReservations()
    } catch (error) {
      console.error('Failed to request extension:', error)
      toast.error('Failed to request extension')
    }
  }

  if (authLoading || !isAuthenticated) {
    return null
  }

  // Ensure reservations is always an array before filtering
  const safeReservations = Array.isArray(reservations) ? reservations : []
  const activeReservations = safeReservations.filter(r => r.status === 'active' || r.status === 'ready_for_pickup')
  const pendingReservations = safeReservations.filter(r => r.status === 'pending')
  const completedReservations = safeReservations.filter(r => r.status === 'completed' || r.status === 'cancelled')

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20'
      case 'pending':
        return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border-yellow-500/20'
      case 'ready_for_pickup':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20'
      case 'completed':
        return 'bg-gray-500/10 text-gray-600 dark:text-gray-400 border-gray-500/20'
      case 'cancelled':
        return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
      case 'overdue':
        return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
      default:
        return 'bg-muted'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'ready_for_pickup':
        return <CheckCircle className="h-3 w-3" />
      case 'pending':
        return <Clock className="h-3 w-3" />
      case 'overdue':
        return <AlertCircle className="h-3 w-3" />
      case 'cancelled':
        return <XCircle className="h-3 w-3" />
      default:
        return null
    }
  }

  const ReservationCard = ({ reservation }: { reservation: Reservation }) => {
    const isActive = reservation.status === 'active' || reservation.status === 'ready_for_pickup'
    const canCancel = reservation.status === 'pending' || reservation.status === 'active'
    const canExtend = reservation.status === 'active' && !reservation.extension_requested

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.01 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2">
                  <CardTitle className="text-lg">{reservation.item_name}</CardTitle>
                  <Badge variant="outline" className={getStatusColor(reservation.status)}>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(reservation.status)}
                      <span className="capitalize">{reservation.status.replace('_', ' ')}</span>
                    </div>
                  </Badge>
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <MapPin className="h-3 w-3" />
                  <span>{reservation.hub_name}</span>
                </div>
              </div>
              <div className="text-right text-sm">
                <p className="font-medium">Qty: {reservation.quantity}</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">Pickup Date</p>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <p className="font-medium">{format(new Date(reservation.pickup_date), 'MMM dd, yyyy')}</p>
                </div>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Return Date</p>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <p className="font-medium">{format(new Date(reservation.expected_return_date), 'MMM dd, yyyy')}</p>
                </div>
              </div>
            </div>

            {reservation.extension_requested && (
              <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400 bg-yellow-500/10 p-2 rounded-md">
                <Clock className="h-4 w-4" />
                <span>Extension {reservation.extension_approved ? 'approved' : 'requested'}</span>
              </div>
            )}

            <div className="flex gap-2">
              {canCancel && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCancel(reservation.id)}
                >
                  Cancel
                </Button>
              )}
              {canExtend && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExtend(reservation.id)}
                >
                  Request Extension
                </Button>
              )}
              {isActive && (
                <Button variant="default" size="sm" asChild className="ml-auto">
                  <Link href={`/items/${reservation.item_name}`}>
                    View Item
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    )
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold tracking-tight">My Reservations</h1>
          <p className="text-muted-foreground">
            Track your borrowed items and return dates
          </p>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid gap-4 md:grid-cols-3"
        >
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Active</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Package className="h-8 w-8 text-primary" />
                <p className="text-3xl font-bold">{loading ? '...' : activeReservations.length}</p>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Currently borrowed</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Clock className="h-8 w-8 text-yellow-500" />
                <p className="text-3xl font-bold">{loading ? '...' : pendingReservations.length}</p>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Awaiting approval</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Calendar className="h-8 w-8 text-muted-foreground" />
                <p className="text-3xl font-bold">{loading ? '...' : completedReservations.length}</p>
              </div>
              <p className="text-xs text-muted-foreground mt-1">Past reservations</p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Reservations List */}
        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-32" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-24 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : reservations.length > 0 ? (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="active">Active</TabsTrigger>
              <TabsTrigger value="pending">Pending</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              {reservations.map(reservation => (
                <ReservationCard key={reservation.id} reservation={reservation} />
              ))}
            </TabsContent>

            <TabsContent value="active" className="space-y-4">
              {activeReservations.length > 0 ? (
                activeReservations.map(reservation => (
                  <ReservationCard key={reservation.id} reservation={reservation} />
                ))
              ) : (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-muted-foreground">No active reservations</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="pending" className="space-y-4">
              {pendingReservations.length > 0 ? (
                pendingReservations.map(reservation => (
                  <ReservationCard key={reservation.id} reservation={reservation} />
                ))
              ) : (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-muted-foreground">No pending reservations</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              {completedReservations.length > 0 ? (
                completedReservations.map(reservation => (
                  <ReservationCard key={reservation.id} reservation={reservation} />
                ))
              ) : (
                <Card>
                  <CardContent className="py-8 text-center">
                    <p className="text-muted-foreground">No past reservations</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        ) : (
          <Card>
            <CardContent className="py-16 text-center">
              <Package className="h-16 w-16 text-muted-foreground/30 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No reservations yet</h3>
              <p className="text-muted-foreground mb-4">
                Browse available items to get started!
              </p>
              <Button asChild>
                <Link href="/items">Browse Items</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  )
}
