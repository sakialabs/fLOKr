'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MapPin, Users, Package, Calendar } from 'lucide-react'
import { api } from '@/lib/api'

interface Hub {
  id: string
  name: string
  address: string
  city: string
  province: string
  capacity?: number
}

export default function HubsPage() {
  const router = useRouter()
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth)
  const [hubs, setHubs] = useState<Hub[]>([])
  const [isLoadingHubs, setIsLoadingHubs] = useState(true)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    const fetchHubs = async () => {
      try {
        setIsLoadingHubs(true)
        const response = await api.get('/hubs/hubs/')
        const hubsData = Array.isArray(response.data) ? response.data : response.data.results || []
        setHubs(hubsData)
      } catch (error) {
        console.error('Failed to fetch hubs:', error)
        setHubs([])
      } finally {
        setIsLoadingHubs(false)
      }
    }
    
    if (isAuthenticated) {
      fetchHubs()
    }
  }, [isAuthenticated])

  if (loading || !isAuthenticated) {
    return null
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Community Hubs</h1>
          <p className="text-muted-foreground">
            Connect with local resource centers
          </p>
        </div>

        {isLoadingHubs ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading hubs...</p>
          </div>
        ) : hubs.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <MapPin className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground">No hubs found</p>
            </CardContent>
          </Card>
        ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {hubs.map((hub, index) => (
            <motion.div
              key={hub.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <Card className="h-full hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2 min-w-0">
                    <MapPin className="h-5 w-5 text-primary flex-shrink-0" />
                    <CardTitle className="text-lg truncate">{hub.name}</CardTitle>
                  </div>
                  {[hub.city, hub.province].filter(Boolean).length > 0 && (
                    <CardDescription className="truncate">
                      {[hub.city, hub.province].filter(Boolean).join(', ')}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="text-muted-foreground line-clamp-2">{hub.address}</p>
                  </div>
                  {hub.capacity && (
                    <div className="flex items-center gap-2 text-sm">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span>Capacity: {hub.capacity}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
        )}
      </div>
    </AppLayout>
  )
}
