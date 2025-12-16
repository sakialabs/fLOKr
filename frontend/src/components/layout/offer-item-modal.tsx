'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Upload, Check, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

interface OfferItemModalProps {
  isOpen: boolean
  onClose: () => void
}

const itemCategories = [
  'Tools & Equipment',
  'Kitchen & Cooking',
  'Books & Media',
  'Sports & Recreation',
  'Electronics',
  'Furniture',
  'Other',
]

export function OfferItemModal({ isOpen, onClose }: OfferItemModalProps) {
  const [itemName, setItemName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [condition, setCondition] = useState<'excellent' | 'good' | 'fair' | ''>('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = () => {
    if (!itemName.trim() || !category || !condition) return

    // Here you would submit to API
    setSubmitted(true)
    
    setTimeout(() => {
      toast.success('Your item has been listed. Thank you for sharing!')
      onClose()
      // Reset state after animation
      setTimeout(() => {
        setItemName('')
        setCategory('')
        setDescription('')
        setCondition('')
        setSubmitted(false)
      }, 300)
    }, 1000)
  }

  const handleClose = () => {
    onClose()
    // Reset state after animation
    setTimeout(() => {
      setItemName('')
      setCategory('')
      setDescription('')
      setCondition('')
      setSubmitted(false)
    }, 300)
  }

  return (
    <AnimatePresence mode="wait">
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            onClick={handleClose}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 20 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="relative z-10 w-full max-w-md mx-4"
          >
            <Card className="bg-card border border-border shadow-2xl">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <Package className="h-5 w-5 text-primary" />
                  <h2 className="text-lg font-semibold">Offer an Item</h2>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleClose}
                  className="h-8 w-8"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Content */}
              <div className="p-4 space-y-4 max-h-[70vh] overflow-y-auto">
                {!submitted ? (
                  <>
                    {/* Item Name */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        What are you offering?
                      </label>
                      <Input
                        value={itemName}
                        onChange={(e) => setItemName(e.target.value)}
                        placeholder="e.g., Electric drill, Camping tent..."
                        className="w-full"
                      />
                    </div>

                    {/* Category */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Category
                      </label>
                      <div className="grid grid-cols-2 gap-2">
                        {itemCategories.map((cat) => (
                          <button
                            key={cat}
                            onClick={() => setCategory(cat)}
                            className={`p-2.5 rounded-lg border text-sm transition-colors ${
                              category === cat
                                ? 'border-primary bg-primary/5 text-foreground'
                                : 'border-border hover:border-primary/50 hover:bg-muted/50 text-muted-foreground'
                            }`}
                          >
                            {cat}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Condition */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Condition
                      </label>
                      <div className="grid grid-cols-3 gap-2">
                        {[
                          { value: 'excellent', label: 'Excellent' },
                          { value: 'good', label: 'Good' },
                          { value: 'fair', label: 'Fair' },
                        ].map((cond) => (
                          <button
                            key={cond.value}
                            onClick={() => setCondition(cond.value as any)}
                            className={`p-2.5 rounded-lg border text-sm transition-colors ${
                              condition === cond.value
                                ? 'border-primary bg-primary/5 text-foreground'
                                : 'border-border hover:border-primary/50 hover:bg-muted/50 text-muted-foreground'
                            }`}
                          >
                            {cond.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Description */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Description (optional)
                      </label>
                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Any details about the item, how to use it, etc."
                        className="w-full min-h-[80px] p-3 rounded-lg border border-border bg-background text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
                      />
                    </div>

                    {/* Photo Upload Placeholder */}
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Photo (optional)
                      </label>
                      <button className="w-full p-6 rounded-lg border-2 border-dashed border-border hover:border-primary/50 transition-colors flex flex-col items-center gap-2 text-muted-foreground hover:text-foreground">
                        <Upload className="h-6 w-6" />
                        <span className="text-sm">Click to upload photo</span>
                      </button>
                    </div>
                  </>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="py-8 text-center"
                  >
                    <div className="h-16 w-16 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-4">
                      <Check className="h-8 w-8 text-green-500" />
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Your item has been listed. Thank you for sharing!
                    </p>
                  </motion.div>
                )}
              </div>

              {/* Footer */}
              {!submitted && (
                <div className="flex items-center justify-end gap-2 p-4 border-t border-border">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClose}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSubmit}
                    disabled={!itemName.trim() || !category || !condition}
                  >
                    <Package className="h-4 w-4 mr-2" />
                    List Item
                  </Button>
                </div>
              )}
            </Card>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
