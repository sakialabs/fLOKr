'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MapPin, Users, Package, Clock, Navigation, Search, Star, Phone, Mail } from 'lucide-react'
import { hubService, Hub } from '@/lib/api-services'

export default function HubsPage() {
  const router = useRouter()
  const { isAuthenticated, loading, user } = useSelector((state: RootState) => state.auth)
  const [hubs, setHubs] = useState<Hub[]>([])
  const [isLoadingHubs, setIsLoadingHubs] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedTab, setSelectedTab] = useState<string>('my-hub')

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  useEffect(() => {
    const fetchHubs = async () => {
      try {
        setIsLoadingHubs(true)
        const data = await hubService.getAll()
        // Ensure data is always an array
        setHubs(Array.isArray(data) ? data : [])
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

  // Find user's assigned hub
  const myHub = Array.isArray(hubs) ? hubs.find(hub => hub.id === user?.assigned_hub) : undefined
  
  // Filter hubs based on search
  const filteredHubs = Array.isArray(hubs) ? hubs.filter(hub =>
    hub.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    hub.address?.toLowerCase().includes(searchQuery.toLowerCase())
  ) : []

  const otherHubs = filteredHubs.filter(hub => hub.id !== myHub?.id)

  const HubCard = ({ hub, isFeatured = false }: { hub: Hub; isFeatured?: boolean }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="h-full"
    >
      <Card className={`h-full hover:shadow-lg transition-all ${isFeatured ? 'border-2 border-primary' : ''}`}>
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <MapPin className={`h-5 w-5 flex-shrink-0 ${isFeatured ? 'text-primary' : 'text-muted-foreground'}`} />
              <div className="min-w-0 flex-1">
                <CardTitle className="text-lg truncate flex items-center gap-2">
                  {hub.name}
                  {isFeatured && (
                    <Badge variant="default" className="shrink-0">
                      <Star className="h-3 w-3 mr-1" />
                      Your Hub
                    </Badge>
                  )}
                </CardTitle>
                {hub.distance && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {hub.distance.toFixed(1)} km away
                  </p>
                )}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-start gap-2 text-sm">
              <Navigation className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
              <p className="text-muted-foreground">{hub.address}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {hub.current_inventory_count !== undefined && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-muted">
                <Package className="h-4 w-4 text-primary" />
                <div className="min-w-0">
                  <p className="text-xs text-muted-foreground">Items</p>
                  <p className="font-semibold text-sm truncate">{hub.current_inventory_count}</p>
                </div>
              </div>
            )}
            
            {hub.capacity !== undefined && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-muted">
                <Users className="h-4 w-4 text-primary" />
                <div className="min-w-0">
                  <p className="text-xs text-muted-foreground">Capacity</p>
                  <p className="font-semibold text-sm truncate">{hub.capacity}</p>
                </div>
              </div>
            )}
          </div>

          {hub.operating_hours && (
            <div className="flex items-start gap-2 text-sm p-3 rounded-lg bg-muted/50">
              <Clock className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-muted-foreground mb-1">Hours</p>
                <p className="text-xs">
                  {typeof hub.operating_hours === 'object' ? 
                    Object.entries(hub.operating_hours).slice(0, 2).map(([day, hours]) => 
                      `${day}: ${hours}`
                    ).join(' • ') 
                    : 'Check with hub'}
                </p>
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            <Button 
              variant="default" 
              className="flex-1"
              onClick={() => router.push(`/hubs/${hub.id}`)}
            >
              View Details
            </Button>
            <Button 
              variant="outline" 
              size="icon"
              onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(hub.address)}`, '_blank')}
            >
              <Navigation className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold tracking-tight">Community Hubs</h1>
          <p className="text-muted-foreground">
            Connect with your local resource center and discover nearby hubs
          </p>
        </motion.div>

        {/* Search Bar - Centered */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex justify-center"
        >
          <div className="relative w-full max-w-2xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search hubs by name or location (e.g., 'Westdale', 'Downtown')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-full"
            />
          </div>
        </motion.div>

        {isLoadingHubs ? (
          <div className="text-center py-12">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading hubs...</p>
          </div>
        ) : (
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
            <div className="mb-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="my-hub">
                  <Star className="h-4 w-4 mr-2" />
                  My Hub
                </TabsTrigger>
                <TabsTrigger value="all-hubs">
                  <MapPin className="h-4 w-4 mr-2" />
                  All Hubs ({otherHubs.length})
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="my-hub" className="space-y-6 mt-6">
              {myHub ? (
                <div className="max-w-2xl">
                  <HubCard hub={myHub} isFeatured={true} />
                </div>
              ) : (
                <Card>
                  <CardContent className="py-12 text-center">
                    <MapPin className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                    <h3 className="font-semibold mb-2">No Hub Assigned</h3>
                    <p className="text-muted-foreground mb-4">
                      You haven't been assigned to a hub yet. Browse available hubs and contact an administrator.
                    </p>
                    <Button onClick={() => setSelectedTab('all-hubs')}>
                      Browse All Hubs
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Quick Actions for My Hub */}
              {myHub && (
                <div className="grid gap-4 md:grid-cols-2 max-w-2xl">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Browse Items</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Button 
                        className="w-full"
                        onClick={() => router.push(`/items?hub=${myHub.id}`)}
                      >
                        <Package className="h-4 w-4 mr-2" />
                        View Available Items
                      </Button>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Connect</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Button 
                        className="w-full"
                        variant="outline"
                        onClick={() => router.push('/community/mentorship')}
                      >
                        <Users className="h-4 w-4 mr-2" />
                        Find Mentors
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

            <TabsContent value="all-hubs" className="space-y-6 mt-6">
              {filteredHubs.length === 0 ? (
                <Card>
                  <CardContent className="py-12 text-center">
                    <Search className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                    <p className="text-muted-foreground">
                      {searchQuery ? `No hubs found matching "${searchQuery}"` : 'No hubs available'}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {filteredHubs.map((hub) => (
                    <HubCard key={hub.id} hub={hub} isFeatured={hub.id === myHub?.id} />
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}
      </div>
    </AppLayout>
  )
}
