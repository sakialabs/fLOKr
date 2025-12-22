'use client'

import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { toast } from 'sonner'
import { Globe, Sun, Loader2 } from 'lucide-react'
import { setUser } from '@/store/slices/authSlice'

interface PreferencesSettingsProps {
  user: {
    preferred_language?: string
    is_mentor?: boolean
  }
}

export function PreferencesSettings({ user }: PreferencesSettingsProps) {
  const dispatch = useDispatch()
  const [loading, setLoading] = useState(false)
  const [preferences, setPreferences] = useState({
    preferred_language: user.preferred_language || 'en',
    is_mentor: user.is_mentor || false,
  })

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español (Spanish)' },
    { code: 'ar', name: 'العربية (Arabic)' },
    { code: 'fr', name: 'Français (French)' },
    { code: 'zh', name: '中文 (Chinese)' },
    { code: 'ur', name: 'اردو (Urdu)' },
    { code: 'so', name: 'Soomaali (Somali)' },
    { code: 'am', name: 'አማርኛ (Amharic)' },
    { code: 'ru', name: 'Русский (Russian)' },
    { code: 'fa', name: 'فارسی (Persian)' },
    { code: 'sw', name: 'Kiswahili (Swahili)' },
  ]

  const handleLanguageChange = (value: string) => {
    setPreferences(prev => ({ ...prev, preferred_language: value }))
  }

  const handleMentorToggle = (checked: boolean) => {
    setPreferences(prev => ({ ...prev, is_mentor: checked }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(preferences)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to update preferences')
      }

      const updatedUser = await response.json()
      dispatch(setUser(updatedUser))
      
      toast.success('Preferences updated successfully!')
    } catch (error) {
      const err = error as Error
      toast.error(err.message || 'Failed to update preferences')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid gap-6">
      {/* Language Preferences */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-primary" />
            <CardTitle>Language</CardTitle>
          </div>
          <CardDescription>
            Choose your preferred language for the app
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="language">Preferred Language</Label>
              <Select
                value={preferences.preferred_language}
                onValueChange={handleLanguageChange}
                disabled={loading}
              >
                <SelectTrigger id="language">
                  <SelectValue placeholder="Select a language" />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                This will be used for notifications and interface translations
              </p>
            </div>

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Language Preference
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Mentorship Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Mentorship</CardTitle>
          <CardDescription>
            Help newcomers by becoming a mentor
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5 flex-1">
                <Label htmlFor="mentor-toggle">Available as Mentor</Label>
                <p className="text-sm text-muted-foreground">
                  Allow newcomers to request mentorship from you
                </p>
              </div>
              <Switch
                id="mentor-toggle"
                checked={preferences.is_mentor}
                onCheckedChange={handleMentorToggle}
                disabled={loading}
              />
            </div>

            {preferences.is_mentor && (
              <div className="rounded-lg bg-muted p-4 space-y-2">
                <p className="text-sm font-medium">As a mentor, you can:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>Share your experience and knowledge with newcomers</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>Help them navigate the community and resources</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>Build meaningful connections and give back</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span>
                    <span>Earn community recognition badges</span>
                  </li>
                </ul>
              </div>
            )}

            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Mentorship Preference
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Display Preferences (Coming Soon) */}
      <Card className="opacity-60">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sun className="h-5 w-5" />
            <CardTitle>Display</CardTitle>
          </div>
          <CardDescription>
            Customize how the app looks (Coming soon)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between opacity-50">
            <div className="space-y-0.5">
              <Label>Theme</Label>
              <p className="text-sm text-muted-foreground">
                Choose light or dark mode
              </p>
            </div>
            <Button variant="outline" size="sm" disabled>
              Auto
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
