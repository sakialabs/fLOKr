'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { inventoryService, InventoryItem } from '@/lib/api-services'
import { ArrowLeft, MapPin, Package, CheckCircle, XCircle, Clock, Calendar } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { ReserveItemDialog } from '@/components/inventory/reserve-item-dialog'

export default function ItemDetailPage() {
  const params = useParams()
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  
  const [item, setItem] = useState<InventoryItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedImage, setSelectedImage] = useState(0)
  const [showReserveDialog, setShowReserveDialog] = useState(false)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated && params.id) {
      fetchItem()
    }
  }, [isAuthenticated, params.id])

  const fetchItem = async () => {
    try {
      setLoading(true)
      const data = await inventoryService.getById(params.id as string)
      setItem(data)
    } catch (error) {
      console.error('Failed to fetch item:', error)
    } finally {
      setLoading(false)
    }
  }

  if (authLoading || !isAuthenticated) {
    return null
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="space-y-6">
          <Skeleton className="h-10 w-32" />
          <div className="grid gap-6 md:grid-cols-2">
            <Skeleton className="aspect-square w-full rounded-lg" />
            <div className="space-y-4">
              <Skeleton className="h-10 w-3/4" />
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (!item) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Package className="h-16 w-16 text-muted-foreground/30 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Item not found</h3>
          <p className="text-muted-foreground mb-4">
            The item you're looking for doesn't exist or has been removed.
          </p>
          <Button asChild>
            <Link href="/items">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Items
            </Link>
          </Button>
        </div>
      </AppLayout>
    )
  }

  const isAvailable = item.quantity_available > 0 && item.status === 'available'
  const images = item.images && item.images.length > 0 ? item.images : []

  const getConditionColor = (condition: string) => {
    switch (condition?.toLowerCase()) {
      case 'new':
        return 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20'
      case 'good':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20'
      case 'fair':
        return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border-yellow-500/20'
      default:
        return 'bg-gray-500/10 text-gray-600 dark:text-gray-400 border-gray-500/20'
    }
  }

  const getStatusIcon = () => {
    if (isAvailable) return <CheckCircle className="h-4 w-4" />
    if (item.status === 'reserved') return <Clock className="h-4 w-4" />
    return <XCircle className="h-4 w-4" />
  }

  const getStatusText = () => {
    if (isAvailable) return 'Available'
    if (item.status === 'reserved') return 'Reserved'
    return 'Unavailable'
  }

  const getStatusColor = () => {
    if (isAvailable) return 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20'
    if (item.status === 'reserved') return 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20'
    return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
  }

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
        {/* Back Button */}
        <Button variant="ghost" asChild>
          <Link href="/items">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Items
          </Link>
        </Button>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Image Gallery */}
          <div className="space-y-4">
            {/* Main Image */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative aspect-square w-full overflow-hidden rounded-lg bg-muted border"
            >
              {images.length > 0 ? (
                <Image
                  src={images[selectedImage]}
                  alt={item.name}
                  fill
                  className="object-cover"
                  priority
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <Package className="h-24 w-24 text-muted-foreground/30" />
                </div>
              )}
            </motion.div>

            {/* Thumbnail Gallery */}
            {images.length > 1 && (
              <div className="grid grid-cols-4 gap-2">
                {images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImage(idx)}
                    className={`relative aspect-square overflow-hidden rounded-md border-2 transition-all ${
                      selectedImage === idx
                        ? 'border-primary'
                        : 'border-transparent hover:border-muted-foreground/30'
                    }`}
                  >
                    <Image
                      src={img}
                      alt={`${item.name} ${idx + 1}`}
                      fill
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Item Details */}
          <div className="space-y-6">
            {/* Title and Badges */}
            <div className="space-y-3">
              <div className="flex gap-2">
                <Badge variant="outline" className={getStatusColor()}>
                  <div className="flex items-center gap-1">
                    {getStatusIcon()}
                    {getStatusText()}
                  </div>
                </Badge>
                <Badge variant="outline" className={getConditionColor(item.condition)}>
                  {item.condition || 'N/A'}
                </Badge>
                <Badge variant="outline" className="border-muted-foreground/20">
                  {item.category || 'Uncategorized'}
                </Badge>
              </div>

              <h1 className="text-3xl font-bold tracking-tight">{item.name}</h1>
            </div>

            {/* Description */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground whitespace-pre-wrap">
                  {item.description || 'No description available.'}
                </p>
              </CardContent>
            </Card>

            {/* Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Availability</span>
                  <span className="font-medium">
                    {item.quantity_available} of {item.quantity_total} available
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Location</span>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{item.hub_name || 'Unknown Hub'}</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Listed</span>
                  <span className="font-medium">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Reserve Button */}
            <Button
              size="lg"
              className="w-full"
              disabled={!isAvailable}
              onClick={() => setShowReserveDialog(true)}
            >
              <Calendar className="h-4 w-4 mr-2" />
              {isAvailable ? 'Reserve This Item' : 'Not Available'}
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Reserve Dialog */}
      {item && (
        <ReserveItemDialog
          item={item}
          open={showReserveDialog}
          onOpenChange={setShowReserveDialog}
          onReserve={() => {
            setShowReserveDialog(false)
            router.push('/reservations')
          }}
        />
      )}
    </AppLayout>
  )
}
