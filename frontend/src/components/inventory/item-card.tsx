'use client'

import { Card, CardFooter, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { InventoryItem } from '@/lib/api-services'
import { Package, MapPin, CheckCircle, XCircle, Clock } from 'lucide-react'
import { motion } from 'framer-motion'
import Image from 'next/image'
import Link from 'next/link'

interface ItemCardProps {
  item: InventoryItem
  index?: number
}

export function ItemCard({ item, index = 0 }: ItemCardProps) {
  const isAvailable = item.quantity_available > 0 && item.status === 'available'
  
  const getConditionColor = (condition: string) => {
    switch (condition?.toLowerCase()) {
      case 'new':
        return 'bg-green-500/10 text-green-600 dark:text-green-400'
      case 'good':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400'
      case 'fair':
        return 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400'
      default:
        return 'bg-gray-500/10 text-gray-600 dark:text-gray-400'
    }
  }

  const getStatusIcon = () => {
    if (isAvailable) return <CheckCircle className="h-3 w-3" />
    if (item.status === 'reserved') return <Clock className="h-3 w-3" />
    return <XCircle className="h-3 w-3" />
  }

  const getStatusText = () => {
    if (isAvailable) return 'Available'
    if (item.status === 'reserved') return 'Reserved'
    return 'Unavailable'
  }

  const getStatusColor = () => {
    if (isAvailable) return 'bg-green-500/10 text-green-600 dark:text-green-400'
    if (item.status === 'reserved') return 'bg-orange-500/10 text-orange-600 dark:text-orange-400'
    return 'bg-red-500/10 text-red-600 dark:text-red-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      className="h-full"
    >
      <Link href={`/items/${item.id}`} className="block h-full">
        <Card className="h-full flex flex-col hover:shadow-lg transition-shadow">
          {/* Image */}
          <div className="relative aspect-video w-full overflow-hidden rounded-t-lg bg-muted">
            {item.images && item.images.length > 0 ? (
              <Image
                src={item.images[0]}
                alt={item.name}
                fill
                className="object-cover"
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <Package className="h-16 w-16 text-muted-foreground/30" />
              </div>
            )}
            
            {/* Status Badge */}
            <div className="absolute top-2 right-2 flex gap-1">
              <Badge className={getStatusColor()}>
                <div className="flex items-center gap-1">
                  {getStatusIcon()}
                  <span className="text-xs">{getStatusText()}</span>
                </div>
              </Badge>
            </div>
          </div>

          <CardHeader className="flex-1">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-lg line-clamp-2">{item.name}</h3>
              <Badge className={getConditionColor(item.condition)}>
                {item.condition || 'N/A'}
              </Badge>
            </div>
            
            <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
              {item.description || 'No description available'}
            </p>
          </CardHeader>

          <CardFooter className="flex flex-col gap-2 pt-0">
            <div className="flex items-center justify-between w-full text-sm">
              <div className="flex items-center gap-1 text-muted-foreground">
                <MapPin className="h-3 w-3" />
                <span className="truncate">{item.hub_name || 'Unknown Hub'}</span>
              </div>
              <div className="text-muted-foreground">
                <span className="font-medium">{item.quantity_available}</span> / {item.quantity_total} available
              </div>
            </div>
            
            <Button 
              className="w-full" 
              disabled={!isAvailable}
              onClick={(e) => {
                e.preventDefault()
                // Will be handled by Link navigation
              }}
            >
              {isAvailable ? 'View Details' : 'Not Available'}
            </Button>
          </CardFooter>
        </Card>
      </Link>
    </motion.div>
  )
}

export function ItemCardSkeleton() {
  return (
    <Card className="h-full flex flex-col">
      <div className="relative aspect-video w-full overflow-hidden rounded-t-lg bg-muted animate-pulse" />
      
      <CardHeader className="flex-1 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <div className="h-6 bg-muted rounded w-3/4 animate-pulse" />
          <div className="h-5 w-16 bg-muted rounded animate-pulse" />
        </div>
        <div className="space-y-1">
          <div className="h-4 bg-muted rounded w-full animate-pulse" />
          <div className="h-4 bg-muted rounded w-2/3 animate-pulse" />
        </div>
      </CardHeader>

      <CardFooter className="flex flex-col gap-2 pt-0">
        <div className="flex items-center justify-between w-full">
          <div className="h-4 bg-muted rounded w-1/3 animate-pulse" />
          <div className="h-4 bg-muted rounded w-1/4 animate-pulse" />
        </div>
        <div className="h-10 bg-muted rounded w-full animate-pulse" />
      </CardFooter>
    </Card>
  )
}
