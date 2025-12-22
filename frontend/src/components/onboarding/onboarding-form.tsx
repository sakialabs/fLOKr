'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDispatch, useSelector } from 'react-redux'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { PhoneNumberInput } from '@/components/ui/phone-input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { authService, OnboardingPreferences } from '@/lib/auth'
import { setUser } from '@/store/slices/authSlice'
import { RootState } from '@/store'
import { Loader2, X, User } from 'lucide-react'
import { toast } from 'sonner'
import { AvatarSelector } from '@/components/profile/avatar-selector'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { communityService } from '@/lib/api-services'

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

const CANADIAN_PROVINCES = [
  { code: 'ON', name: 'Ontario' },
  { code: 'BC', name: 'British Columbia' },
  { code: 'AB', name: 'Alberta' },
  { code: 'QC', name: 'Quebec' },
  { code: 'NS', name: 'Nova Scotia' },
  { code: 'NB', name: 'New Brunswick' },
  { code: 'MB', name: 'Manitoba' },
  { code: 'PE', name: 'Prince Edward Island' },
  { code: 'SK', name: 'Saskatchewan' },
  { code: 'NL', name: 'Newfoundland and Labrador' },
  { code: 'YT', name: 'Yukon' },
  { code: 'NT', name: 'Northwest Territories' },
  { code: 'NU', name: 'Nunavut' },
]

const COUNTRIES = [
  { code: 'CA', name: 'Canada' },
  { code: 'US', name: 'United States' },
]

export function OnboardingForm() {
  const router = useRouter()
  const dispatch = useDispatch()
  const user = useSelector((state: RootState) => state.auth.user)
  
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [selectedAvatar, setSelectedAvatar] = useState<string>('')
  const [customUpload, setCustomUpload] = useState<File | null>(null)
  const [preferences, setPreferences] = useState<OnboardingPreferences>({
    dietary_restrictions: [],
    immediate_needs: [],
    skill_interests: [],
    interests: [],
    languages_spoken: [],
    seeking_mentor: false,
    phone: '',
    address_country: 'CA',
    address_province: 'ON',
    address_street: '',
    address_city: '',
    address_postal_code: '',
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error('Please upload a JPEG, PNG, or WebP image')
      return
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image must be less than 5MB')
      return
    }

    setCustomUpload(file)
    setSelectedAvatar('') // Clear avatar selection if uploading custom
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      // Upload profile picture if selected
      if (customUpload) {
        try {
          await communityService.uploadProfilePicture(customUpload)
          toast.success('Profile picture uploaded!')
        } catch {
          toast.error('Failed to upload profile picture, but continuing...')
        }
      }

      const updatedUser = await authService.saveOnboardingPreferences(preferences)
      dispatch(setUser(updatedUser))
      toast.success('Welcome to fLOKr! Your profile is all set.')
      router.push('/dashboard')
    } catch {
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

        <div className="space-y-4">
          <Label>Your address</Label>
          <p className="text-sm text-muted-foreground -mt-2">
            📍 We&apos;ll connect you with your nearest community hub and local mentors
          </p>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="address_country">Country</Label>
              <Select
                value={preferences.address_country || 'CA'}
                onValueChange={(value) => updatePreference('address_country', value)}
                required
              >
                <option value="">Select country</option>
                {COUNTRIES.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name}
                  </option>
                ))}
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="address_province">Province</Label>
              <Select
                value={preferences.address_province || 'ON'}
                onValueChange={(value) => updatePreference('address_province', value)}
                required
              >
                <option value="">Select province</option>
                {CANADIAN_PROVINCES.map((province) => (
                  <option key={province.code} value={province.code}>
                    {province.name}
                  </option>
                ))}
              </Select>
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="address_street">Street Address</Label>
            <Input
              id="address_street"
              placeholder="123 Main Street, Apt 4B"
              value={preferences.address_street || ''}
              onChange={(e) => updatePreference('address_street', e.target.value)}
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="address_city">City</Label>
              <Input
                id="address_city"
                placeholder="Hamilton"
                value={preferences.address_city || ''}
                onChange={(e) => updatePreference('address_city', e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="address_postal_code">Postal Code</Label>
              <Input
                id="address_postal_code"
                placeholder="L8P 4R5"
                value={preferences.address_postal_code || ''}
                onChange={(e) => updatePreference('address_postal_code', e.target.value)}
                required
              />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="phone">Phone Number</Label>
          <PhoneNumberInput
            value={preferences.phone || ''}
            onChange={(value) => updatePreference('phone', value || '')}
          />
          <p className="text-sm text-muted-foreground">
            📱 We&apos;ll use this to notify you about hub events and urgent updates
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
        <CardTitle>Add a profile picture</CardTitle>
        <CardDescription>
          Help others recognize you in the community (you can skip this step)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Preview */}
        <div className="flex justify-center">
          <Avatar className="h-32 w-32">
            {customUpload ? (
              <AvatarImage src={URL.createObjectURL(customUpload)} alt="Preview" />
            ) : selectedAvatar ? (
              <AvatarImage src={selectedAvatar} alt="Selected avatar" />
            ) : (
              <AvatarFallback className="bg-primary/10 text-4xl">
                <User className="h-16 w-16 text-muted-foreground" />
              </AvatarFallback>
            )}
          </Avatar>
        </div>

        {/* Upload Option */}
        <div className="space-y-2">
          <Label htmlFor="picture_upload">Upload your own photo</Label>
          <div className="flex items-center gap-3">
            <Input
              id="picture_upload"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleFileChange}
              className="cursor-pointer"
            />
            {customUpload && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCustomUpload(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            JPEG, PNG, or WebP (max 5MB)
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or choose an avatar</span>
          </div>
        </div>

        {/* Avatar Selector */}
        <AvatarSelector
          selectedAvatar={selectedAvatar}
          onSelect={(avatar) => {
            setSelectedAvatar(avatar)
            setCustomUpload(null) // Clear custom upload if selecting avatar
          }}
        />

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
        <CardTitle>What do you need right now?</CardTitle>
        <CardDescription>
          Select items you need most urgently - we&apos;ll help you find them
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
          <Button variant="outline" onClick={() => setStep(2)} className="flex-1">
            Back
          </Button>
          <Button onClick={() => setStep(4)} className="flex-1">
            Continue
          </Button>
        </div>
      </CardContent>
    </Card>
  )

  const renderStep4 = () => (
    <Card>
      <CardHeader>
        <CardTitle>Join the community</CardTitle>
        <CardDescription>
          Connect with others and share your skills
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Skills you&apos;d like to share</Label>
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

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Looking for a mentor?</Label>
              <p className="text-sm text-muted-foreground">
                We&apos;ll match you with experienced community members
              </p>
            </div>
            <input
              type="checkbox"
              checked={preferences.seeking_mentor || false}
              onChange={(e) => updatePreference('seeking_mentor', e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setStep(3)} className="flex-1">
            Back
          </Button>
          <Button onClick={handleSubmit} disabled={loading} className="flex-1">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Complete'
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
        {[1, 2, 3, 4].map((s) => (
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
      {step === 4 && renderStep4()}

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
