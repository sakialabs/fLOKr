'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, X, Loader2, Sparkles, Tag as TagIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { oriAIService, TagSuggestion } from '@/lib/ori-ai'

interface ImageUploadWithTagsProps {
  onTagsSuggested?: (tags: string[], category: string) => void
  onImageSelected?: (file: File) => void
  maxSize?: number // in MB
}

export function ImageUploadWithTags({
  onTagsSuggested,
  onImageSelected,
  maxSize = 5
}: ImageUploadWithTagsProps) {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [suggestedTags, setSuggestedTags] = useState<string[]>([])
  const [suggestedCategory, setSuggestedCategory] = useState<string>('')
  const [detailedTags, setDetailedTags] = useState<TagSuggestion[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleImageSelect = useCallback(async (file: File) => {
    // Validate file size
    if (file.size > maxSize * 1024 * 1024) {
      setError(`Image size must be less than ${maxSize}MB`)
      return
    }

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file')
      return
    }

    setError(null)
    setSelectedImage(file)
    onImageSelected?.(file)

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Analyze image with AI
    setIsAnalyzing(true)
    try {
      const result = await oriAIService.suggestTagsFromFile(file)
      setSuggestedTags(result.tags)
      setSuggestedCategory(result.category)
      setDetailedTags(result.detailed_tags)
      onTagsSuggested?.(result.tags, result.category)
    } catch (err: any) {
      console.error('Failed to analyze image:', err)
      setError('Failed to analyze image. You can still add tags manually.')
    } finally {
      setIsAnalyzing(false)
    }
  }, [maxSize, onImageSelected, onTagsSuggested])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleImageSelect(file)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleImageSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const clearImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    setSuggestedTags([])
    setSuggestedCategory('')
    setDetailedTags([])
    setError(null)
  }

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      {!imagePreview ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleFileInput}
            className="hidden"
            id="image-upload"
          />
          <label htmlFor="image-upload" className="cursor-pointer">
            <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-sm font-medium mb-1">
              Click to upload or drag and drop
            </p>
            <p className="text-xs text-muted-foreground">
              PNG, JPG, GIF up to {maxSize}MB
            </p>
          </label>
        </div>
      ) : (
        <Card>
          <CardContent className="p-4">
            <div className="relative">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-64 object-cover rounded-lg"
              />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
                onClick={clearImage}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 bg-destructive/10 text-destructive rounded-lg text-sm"
        >
          {error}
        </motion.div>
      )}

      {/* AI Analysis Loading */}
      <AnimatePresence>
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                  <div>
                    <p className="text-sm font-medium flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-primary" />
                      AI is analyzing your image...
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Generating tags and category suggestions
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Suggested Tags */}
      <AnimatePresence>
        {suggestedTags.length > 0 && !isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-3"
          >
            <Card className="bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800">
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <p className="text-sm font-semibold text-green-900 dark:text-green-100">
                    AI Suggestions
                  </p>
                </div>

                {/* Category */}
                <div>
                  <p className="text-xs text-muted-foreground mb-1">
                    Suggested Category:
                  </p>
                  <div className="inline-flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
                    <TagIcon className="h-3 w-3" />
                    {suggestedCategory}
                  </div>
                </div>

                {/* Tags */}
                <div>
                  <p className="text-xs text-muted-foreground mb-2">
                    Suggested Tags:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detailedTags.map((tag, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1 }}
                        className="inline-flex items-center gap-2 px-3 py-1 bg-background border border-border rounded-full text-sm"
                      >
                        <span>{tag.tag}</span>
                        <span className="text-xs text-muted-foreground">
                          {Math.round(tag.confidence * 100)}%
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                <p className="text-xs text-muted-foreground italic">
                  You can edit these suggestions before creating the item
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
