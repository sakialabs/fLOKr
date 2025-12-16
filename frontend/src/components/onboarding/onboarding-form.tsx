'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDispatch, useSelector } from 'react-redux'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { authService, OnboardingPreferences } from '@/lib/auth'
import { setUser } from '@/store/slices/authSlice'
import { RootState } from '@/store'
import { Loader2, Plus, X } from 'lucide-react'
import { toast } from 'sonner'

const DIETARY_OPTIONS = [
  'Vegetarian',
  'Vegan',
  'Halal',
  'Kosher',
  'Gluten-free',
  'Dairy-free',
  'Nut allergy',
]

const IMMEDIATE_NEEDS_OPTIONS = [
  'Winter clothing',
  'Kitchen essentials',
  'Bedding',
  'Furniture',
  'Electronics',
  'School supplies',
  'Work attire',
]

const SKILL_OPTIONS = [
  'Cooking',
  'Language exchange',
  'Computer skills',
  'Childcare',
  'Home repair',
  'Gardening',
  'Arts & crafts',
]

export function OnboardingForm() {
  const router = useRouter()
  const dispatch = useDispatch()
  const user = useSelector((state: RootState) => state.auth.user)
  
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [preferences, setPreferences] = useState<OnboardingPreferences>({
    dietary_restrictions: [],
    immediate_needs: [],
    skill_interests: [],
    interests: [],
    languages_spoken: [],
    seeking_mentor: false,
  })

  const updatePreference = (key: keyof OnboardingPreferences, value: any) => {
    setPreferences((prev) => ({ ...prev, [key]: value }))
  }

  const toggleArrayItem = (key: keyof OnboardingPreferences, item: string) => {
    const currentArray = (preferences[key] as string[]) || []
    const newArray = currentArray.includes(item)
      ? currentArray.filter((i) => i !== item)
      : [...currentArray, item]
    updatePreference(key, newArray)
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const updatedUser = await authService.saveOnboardingPreferences(preferences)
      dispatch(setUser(updatedUser))
      toast.success('Welcome to fLOKr! Your profile is all set.')
      router.push('/dashboard')
    } catch (error: any) {
      toast.error('Failed to save preferences. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const renderStep1 = () => (
    <Card>
      <CardHeader>
        <CardTitle>Tell us about yourself</CardTitle>
        <CardDescription>
          Help us personalize your experience and connect you with the right resources
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {user?.role === 'newcomer' && (
          <div className="space-y-2">
            <Label htmlFor="arrival_date">When did you arrive?</Label>
            <Input
              id="arrival_date"
              type="date"
              value={preferences.arrival_date || ''}
              onChange={(e) => updatePreference('arrival_date', e.target.value)}
              required
            />
            <p className="text-sm text-muted-foreground">
              This helps us provide timely recommendations for your settling-in journey
            </p>
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="address">Your address</Label>
          <Textarea
            id="address"
            placeholder="123 Main St, Hamilton, ON L8P 4R5"
            value={preferences.address || ''}
            onChange={(e) => updatePreference('address', e.target.value)}
            rows={2}
            required
          />
          <p className="text-sm text-muted-foreground">
            📍 We'll connect you with your nearest community hub and local mentors
          </p>
        </div>

        <div className="space-y-2">
          <Label>Languages you speak</Label>
          <div className="flex flex-wrap gap-2">
            {['English', 'French', 'Spanish', 'Arabic', 'Mandarin', 'Urdu', 'Tagalog', 'Other'].map((lang) => (
              <Badge
                key={lang}
                variant={preferences.languages_spoken?.includes(lang) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleArrayItem('languages_spoken', lang)}
              >
                {lang}
              </Badge>
            ))}
          </div>
          <p className="text-sm text-muted-foreground">
            🌍 This helps us match you with mentors who speak your language
          </p>
        </div>

        <Button onClick={() => setStep(2)} className="w-full">
          Continue
        </Button>
      </CardContent>
    </Card>
  )

  const renderStep2 = () => (
    <Card>
      <CardHeader>
        <CardTitle>What do you need right now?</CardTitle>
        <CardDescription>
          Select items you need most urgently - we'll help you find them
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Immediate needs</Label>
          <div className="flex flex-wrap gap-2">
            {IMMEDIATE_NEEDS_OPTIONS.map((need) => (
              <Badge
                key={need}
                variant={preferences.immediate_needs?.includes(need) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleArrayItem('immediate_needs', need)}
              >
                {need}
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Dietary preferences (optional)</Label>
          <div className="flex flex-wrap gap-2">
            {DIETARY_OPTIONS.map((diet) => (
              <Badge
                key={diet}
                variant={preferences.dietary_restrictions?.includes(diet) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleArrayItem('dietary_restrictions', diet)}
              >
                {diet}
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="clothing_sizes">Clothing sizes (optional)</Label>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <Label htmlFor="shirt_size" className="text-xs text-muted-foreground">
                Shirt
              </Label>
              <Input
                id="shirt_size"
                placeholder="M"
                value={preferences.clothing_sizes?.shirt || ''}
                onChange={(e) =>
                  updatePreference('clothing_sizes', {
                    ...preferences.clothing_sizes,
                    shirt: e.target.value,
                  })
                }
              />
            </div>
            <div>
              <Label htmlFor="pants_size" className="text-xs text-muted-foreground">
                Pants
              </Label>
              <Input
                id="pants_size"
                placeholder="32"
                value={preferences.clothing_sizes?.pants || ''}
                onChange={(e) =>
                  updatePreference('clothing_sizes', {
                    ...preferences.clothing_sizes,
                    pants: e.target.value,
                  })
                }
              />
            </div>
            <div>
              <Label htmlFor="shoes_size" className="text-xs text-muted-foreground">
                Shoes
              </Label>
              <Input
                id="shoes_size"
                placeholder="10"
                value={preferences.clothing_sizes?.shoes || ''}
                onChange={(e) =>
                  updatePreference('clothing_sizes', {
                    ...preferences.clothing_sizes,
                    shoes: e.target.value,
                  })
                }
              />
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
            Back
          </Button>
          <Button onClick={() => setStep(3)} className="flex-1">
            Continue
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderStep3 = () => (
    <Card>
      <CardHeader>
        <CardTitle>Connect with your community</CardTitle>
        <CardDescription>
          Share your skills and interests to find mentors and make connections
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Skills you'd like to learn or share</Label>
          <div className="flex flex-wrap gap-2">
            {SKILL_OPTIONS.map((skill) => (
              <Badge
                key={skill}
                variant={preferences.skill_interests?.includes(skill) ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => toggleArrayItem('skill_interests', skill)}
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="seeking_mentor">Would you like a mentor?</Label>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="seeking_mentor"
              checked={preferences.seeking_mentor}
              onChange={(e) => updatePreference('seeking_mentor', e.target.checked)}
              className="h-4 w-4 rounded border-gray-300"
            />
            <label htmlFor="seeking_mentor" className="text-sm text-muted-foreground">
              Yes, connect me with a local mentor who can help me navigate my new city
            </label>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setStep(2)} className="flex-1">
            Back
          </Button>
          <Button onClick={handleSubmit} disabled={loading} className="flex-1">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Complete Setup'
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6">
      {/* Progress indicator */}
      <div className="flex items-center justify-center gap-2">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={`h-2 w-16 rounded-full transition-colors ${
              s === step ? 'bg-primary' : s < step ? 'bg-primary/50' : 'bg-muted'
            }`}
          />
        ))}
      </div>

      {/* Step content */}
      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}

      {/* Skip option */}
      <div className="text-center">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard')}
          className="text-muted-foreground"
        >
          Skip for now
        </Button>
      </div>
    </div>
  )
}
