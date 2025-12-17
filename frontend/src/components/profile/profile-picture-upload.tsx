'use client'

import { useState, useRef } from 'react'
import { useDispatch } from 'react-redux'
import { Camera, Trash2, Upload, Smile } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { communityService } from '@/lib/api-services'
import { toast } from 'sonner'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { AvatarSelector } from './avatar-selector'
import { setUser } from '@/store/slices/authSlice'

interface ProfilePictureUploadProps {
  currentPictureUrl?: string
  userName: string
  onUploadSuccess?: (url: string) => void
  avatarChoice?: string
}

export function ProfilePictureUpload({ currentPictureUrl, userName, onUploadSuccess, avatarChoice }: ProfilePictureUploadProps) {
  const dispatch = useDispatch()
  const [uploading, setUploading] = useState(false)
  
  // Determine initial picture URL: use avatar if set, otherwise use uploaded picture
  const getDisplayUrl = () => {
    if (avatarChoice) {
      return `/avatars/${avatarChoice}.png`
    }
    return currentPictureUrl || undefined
  }
  
  const [pictureUrl, setPictureUrl] = useState<string | undefined>(getDisplayUrl())
  const [selectedTab, setSelectedTab] = useState<string>('current')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB')
      return
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Only JPEG, PNG, and WebP images are allowed')
      return
    }

    setUploading(true)

    try {
      const result = await communityService.uploadProfilePicture(file)
      
      // Clear avatar_choice so uploaded photo takes precedence
      const token = localStorage.getItem('access_token')
      const clearAvatarResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ avatar_choice: null })
      })
      
      if (!clearAvatarResponse.ok) {
        console.warn('Failed to clear avatar choice, but upload succeeded')
      }
      
      // Fetch updated user data which includes the full profile_picture URL
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const userData = await response.json()
        dispatch(setUser(userData))
        setPictureUrl(userData.profile_picture)
        onUploadSuccess?.(userData.profile_picture)
      }
      
      toast.success('Profile picture uploaded successfully!')
      setSelectedTab('current')
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to upload profile picture')
    } finally {
      setUploading(false)
    }
  }

  const handleAvatarSelect = async (avatarUrl: string) => {
    setUploading(true)
    try {
      // Extract avatar number from URL (e.g., /avatars/avatar1.png -> avatar1)
      const avatarMatch = avatarUrl.match(/avatar(\d+)/)
      const avatarChoice = avatarMatch ? `avatar${avatarMatch[1]}` : avatarUrl
      
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ avatar_choice: avatarChoice })
      })
      
      if (!response.ok) throw new Error('Failed to save avatar')
      
      const userData = await response.json()
      setPictureUrl(avatarUrl)
      toast.success('Avatar updated successfully!')
      onUploadSuccess?.(avatarUrl)
      setSelectedTab('current')
      
      // Update Redux state
      dispatch(setUser(userData))
    } catch (error) {
      toast.error('Failed to save avatar')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async () => {
    if (!pictureUrl) return

    setUploading(true)
    try {
      const token = localStorage.getItem('access_token')
      
      // Check if it's an avatar or uploaded picture
      const isAvatar = pictureUrl.startsWith('/avatars/')
      
      if (isAvatar) {
        // Clear avatar_choice field
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ avatar_choice: null })
        })
        if (!response.ok) throw new Error('Failed to remove avatar')
        const userData = await response.json()
        dispatch(setUser(userData))
      } else {
        // Delete uploaded profile picture
        await communityService.deleteProfilePicture()
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (response.ok) {
          const userData = await response.json()
          dispatch(setUser(userData))
        }
      }
      
      setPictureUrl(undefined)
      toast.success('Profile picture removed')
      onUploadSuccess?.('')
    } catch (error) {
      toast.error('Failed to remove profile picture')
    } finally {
      setUploading(false)
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <Card className="p-6">
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">Current</TabsTrigger>
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="avatars">Avatars</TabsTrigger>
        </TabsList>

        <TabsContent value="current" className="space-y-4 pt-4">
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <Avatar className="h-32 w-32 border-4 border-background transition-all duration-300 bg-primary">
                <AvatarImage src={pictureUrl} alt={userName} className="transition-opacity duration-300 bg-primary" />
                <AvatarFallback className="text-2xl bg-primary text-primary-foreground">
                  {getInitials(userName)}
                </AvatarFallback>
              </Avatar>
              {uploading && (
                <div className="absolute inset-0 flex items-center justify-center bg-background/80 rounded-full">
                  <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                </div>
              )}
            </div>
            
            {pictureUrl && (
              <Button
                onClick={handleDelete}
                disabled={uploading}
                size="sm"
                variant="outline"
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Remove
              </Button>
            )}
          </div>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4 pt-4">
          <div className="flex flex-col items-center gap-4">
            <div className="text-center space-y-2">
              <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
              <p className="text-sm font-medium">Upload Your Photo</p>
              <p className="text-xs text-muted-foreground">
                JPEG, PNG, or WebP (Max 5MB)
              </p>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <Button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Choose File'}
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="avatars" className="pt-4">
          <AvatarSelector
            onSelect={handleAvatarSelect}
            selectedAvatar={pictureUrl}
            disabled={uploading}
          />
        </TabsContent>
      </Tabs>
    </Card>
  )
}
