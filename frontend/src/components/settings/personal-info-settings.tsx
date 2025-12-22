'use client'

import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { toast } from 'sonner'
import { User, Mail, Phone, MapPin, FileText, Languages, Briefcase, Loader2 } from 'lucide-react'
import { ProfilePictureUpload } from '@/components/profile/profile-picture-upload'
import { setUser } from '@/store/slices/authSlice'

interface PersonalInfoSettingsProps {
  user: {
    email?: string
    profile_picture?: string
    avatar_choice?: string
    first_name?: string
    last_name?: string
    phone?: string
    bio?: string
    address?: string
    skills?: string[]
    languages_spoken?: string[]
  }
}

export function PersonalInfoSettings({ user }: PersonalInfoSettingsProps) {
  const dispatch = useDispatch()
  const [loading, setLoading] = useState(false)
  const [profilePictureUrl, setProfilePictureUrl] = useState(user.profile_picture)
  const [formData, setFormData] = useState({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    phone: user.phone || '',
    bio: user.bio || '',
    address: user.address || '',
    skills: user.skills?.join(', ') || '',
    languages_spoken: user.languages_spoken?.join(', ') || '',
  })

  const handleProfilePictureChange = (url: string) => {
    setProfilePictureUrl(url)
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      
      // Convert comma-separated strings to arrays
      const updateData = {
        ...formData,
        skills: formData.skills ? formData.skills.split(',').map((s: string) => s.trim()).filter(Boolean) : [],
        languages_spoken: formData.languages_spoken ? formData.languages_spoken.split(',').map((l: string) => l.trim()).filter(Boolean) : [],
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to update profile')
      }

      const updatedUser = await response.json()
      dispatch(setUser(updatedUser))
      
      toast.success('Profile updated successfully!')
    } catch (error) {
      const err = error as Error
      toast.error(err.message || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Picture Card */}
        <Card>
          <CardHeader>
            <CardTitle>Profile Picture</CardTitle>
            <CardDescription>Upload your own photo or select an avatar</CardDescription>
          </CardHeader>
          <CardContent>
            <ProfilePictureUpload
              currentPictureUrl={profilePictureUrl}
              userName={`${user.first_name} ${user.last_name}`}
              onUploadSuccess={handleProfilePictureChange}
              avatarChoice={user.avatar_choice}
            />
          </CardContent>
        </Card>

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Your name and contact details</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="first_name"
                    value={formData.first_name}
                    onChange={(e) => handleChange('first_name', e.target.value)}
                    className="pl-9"
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="last_name"
                    value={formData.last_name}
                    onChange={(e) => handleChange('last_name', e.target.value)}
                    className="pl-9"
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  value={user.email}
                  className="pl-9"
                  disabled
                />
              </div>
              <p className="text-xs text-muted-foreground">Email cannot be changed</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="phone"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  className="pl-9"
                  placeholder="+1 (555) 000-0000"
                  disabled={loading}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

        {/* Bio & Additional Info */}
        <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>About You</CardTitle>
          <CardDescription>Tell the community about yourself</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bio">Bio</Label>
              <div className="relative">
                <FileText className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Textarea
                  id="bio"
                  value={formData.bio}
                  onChange={(e) => handleChange('bio', e.target.value)}
                  className="pl-9 min-h-[100px]"
                  placeholder="Share a bit about yourself..."
                  disabled={loading}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Address</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleChange('address', e.target.value)}
                  className="pl-9"
                  placeholder="City, State"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="skills">Skills</Label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="skills"
                    value={formData.skills}
                    onChange={(e) => handleChange('skills', e.target.value)}
                    className="pl-9"
                    placeholder="Cooking, Programming, etc."
                    disabled={loading}
                  />
                </div>
                <p className="text-xs text-muted-foreground">Separate with commas</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="languages_spoken">Languages</Label>
                <div className="relative">
                  <Languages className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="languages_spoken"
                    value={formData.languages_spoken}
                    onChange={(e) => handleChange('languages_spoken', e.target.value)}
                    className="pl-9"
                    placeholder="English, Spanish, etc."
                    disabled={loading}
                  />
                </div>
                <p className="text-xs text-muted-foreground">Separate with commas</p>
              </div>
            </div>

          </div>
        </CardContent>
      </Card>
      </div>

      {/* Single Save Button */}
      <div className="mt-6">
        <Button type="submit" disabled={loading} size="lg" className="w-full md:w-auto">
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Save All Changes
        </Button>
      </div>
    </form>
  )
}
