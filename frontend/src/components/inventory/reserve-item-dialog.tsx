'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { InventoryItem, reservationService } from '@/lib/api-services'
import { Calendar as CalendarIcon, Loader2 } from 'lucide-react'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface ReserveItemDialogProps {
  item: InventoryItem
  open: boolean
  onOpenChange: (open: boolean) => void
  onReserve: () => void
}

export function ReserveItemDialog({ item, open, onOpenChange, onReserve }: ReserveItemDialogProps) {
  const [pickupDate, setPickupDate] = useState<Date>()
  const [returnDate, setReturnDate] = useState<Date>()
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!pickupDate || !returnDate) {
      toast.error('Please select both pickup and return dates')
      return
    }

    if (returnDate <= pickupDate) {
      toast.error('Return date must be after pickup date')
      return
    }

    if (quantity < 1 || quantity > item.quantity_available) {
      toast.error(`Quantity must be between 1 and ${item.quantity_available}`)
      return
    }

    try {
      setLoading(true)
      await reservationService.create({
        item: item.id,
        hub: item.hub_name || '', // You might need to get hub ID from a different field
        quantity,
        pickup_date: format(pickupDate, 'yyyy-MM-dd'),
        expected_return_date: format(returnDate, 'yyyy-MM-dd'),
      })
      
      toast.success('Reservation created successfully!')
      onReserve()
    } catch (error: any) {
      console.error('Failed to create reservation:', error)
      toast.error(error.response?.data?.message || 'Failed to create reservation')
    } finally {
      setLoading(false)
    }
  }

  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Reserve {item.name}</DialogTitle>
          <DialogDescription>
            Select your pickup and return dates. Maximum {item.quantity_available} available.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          {/* Quantity */}
          <div className="space-y-2">
            <Label htmlFor="quantity">Quantity</Label>
            <Input
              id="quantity"
              type="number"
              min={1}
              max={item.quantity_available}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              required
            />
            <p className="text-xs text-muted-foreground">
              {item.quantity_available} available
            </p>
          </div>

          {/* Pickup Date */}
          <div className="space-y-2">
            <Label>Pickup Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'w-full justify-start text-left font-normal',
                    !pickupDate && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {pickupDate ? format(pickupDate, 'PPP') : 'Pick a date'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={pickupDate}
                  onSelect={setPickupDate}
                  disabled={(date: Date) => date < tomorrow}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Return Date */}
          <div className="space-y-2">
            <Label>Expected Return Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    'w-full justify-start text-left font-normal',
                    !returnDate && 'text-muted-foreground'
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {returnDate ? format(returnDate, 'PPP') : 'Pick a date'}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={returnDate}
                  onSelect={setReturnDate}
                  disabled={(date: Date) => {
                    if (!pickupDate) return date < tomorrow
                    const minReturn = new Date(pickupDate)
                    minReturn.setDate(minReturn.getDate() + 1)
                    return date < minReturn
                  }}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Confirm Reservation
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
