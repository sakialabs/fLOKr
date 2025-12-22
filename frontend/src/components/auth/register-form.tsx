'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useDispatch } from 'react-redux'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { authService, tokenManager, RegisterData } from '@/lib/auth'
import { setCredentials, setLoading, setError } from '@/store/slices/authSlice'
import { validatePassword, PasswordStrength } from '@/lib/password-strength'
import { useToast } from '@/hooks/use-toast'
import { Loader2, Eye, EyeOff, Check, X, Shield } from 'lucide-react'

export function RegisterForm() {
  const router = useRouter()
  const dispatch = useDispatch()
  const { toast } = useToast()
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    role: 'newcomer',
    preferred_language: 'en',
    address: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLocalLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength | null>(null)
  const [passwordTouched, setPasswordTouched] = useState(false)

  // Detect autofilled password and validate it
  useEffect(() => {
    const checkAutofill = () => {
      if (formData.password && !passwordTouched) {
        setPasswordTouched(true)
        setPasswordStrength(validatePassword(formData.password))
      }
    }
    // Check after a short delay to catch autofill
    const timer = setTimeout(checkAutofill, 500)
    return () => clearTimeout(timer)
  }, [formData.password, passwordTouched])

  const handleChange = (field: keyof RegisterData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    
    // Validate password strength in real-time
    if (field === 'password') {
      setPasswordTouched(true)
      if (value) {
        setPasswordStrength(validatePassword(value))
      } else {
        setPasswordStrength(null)
      }
    }
    
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    // Password strength validation - only check if all requirements are met
    const strength = validatePassword(formData.password)
    if (!strength.isValid) {
      newErrors.password = 'Please meet all password requirements: ' + strength.feedback.join(', ')
    }

    // Password match validation
    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match'
    }

    // Required fields
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required'
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required'
    }
    if (formData.address && !formData.address.trim()) {
      newErrors.address = 'Address is required'
    } else if (!formData.address) {
      newErrors.address = 'Address is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate form
    if (!validateForm()) {
      toast({
        title: 'Validation Error',
        description: 'Please fix the errors in the form',
        variant: 'destructive'
      })
      return
    }

    setErrors({})
    setLocalLoading(true)
    dispatch(setLoading(true))

    try {
      // Remove optional fields that will be collected during onboarding
      const { ...registrationData } = formData
      const response = await authService.register(registrationData)
      
      // Store tokens
      tokenManager.setTokens(response.tokens.access, response.tokens.refresh)
      
      // Update Redux store
      dispatch(
        setCredentials({
          user: response.user,
          accessToken: response.tokens.access,
          refreshToken: response.tokens.refresh,
        })
      )

      // Success toast
      toast({
        title: '🎉 Welcome to fLOKr!',
        description: `Account created successfully for ${formData.first_name}. Let's get you set up!`
      })

      // Small delay to show toast before redirect
      setTimeout(() => {
        router.push('/onboarding')
      }, 1000)
    } catch (err) {
      const error = err as { response?: { data?: Record<string, unknown>; status?: number } }
      console.error('❌ Registration error:', error)
      console.error('Error details:', {
        response: error.response,
        data: error.response?.data,
        status: error.response?.status
      })
      
      const errorData = error.response?.data
      
      if (errorData) {
        // Parse backend errors
        const parsedErrors: Record<string, string> = {}
        let errorMessage = 'Registration failed. Please check the form.'
        const errorDetails: string[] = []
        
        // Handle different error formats from backend
        if (typeof errorData === 'object') {
          Object.keys(errorData).forEach(key => {
            const value = errorData[key]
            if (Array.isArray(value)) {
              parsedErrors[key] = value[0]
              errorDetails.push(`${key}: ${value[0]}`)
            } else if (typeof value === 'string') {
              parsedErrors[key] = value
              errorDetails.push(`${key}: ${value}`)
            }
          })
          
          console.log('📝 Parsed errors:', parsedErrors)
          console.log('📋 Error details:', errorDetails)
          
          // Create user-friendly error message
          if (parsedErrors.email) {
            errorMessage = parsedErrors.email.includes('already') || parsedErrors.email.includes('exists')
              ? '❌ This email is already registered. Try logging in instead!'
              : parsedErrors.email
          } else if (parsedErrors.password) {
            errorMessage = parsedErrors.password
          } else if (parsedErrors.password_confirm) {
            errorMessage = parsedErrors.password_confirm
          } else if (errorDetails.length > 0) {
            // Show all errors in the toast
            errorMessage = errorDetails.join(' • ')
          } else {
            const firstError = Object.values(parsedErrors)[0]
            errorMessage = firstError || errorMessage
          }
          
          setErrors(parsedErrors)
        } else if (typeof errorData === 'string') {
          errorMessage = errorData
          setErrors({ general: errorData })
        }
        
        // Show descriptive error toast
        toast({
          title: 'Registration Failed',
          description: errorMessage,
          variant: 'destructive'
        })
      } else {
        // Network or unknown error
        const errorMessage = 'Network error. Please check your connection and try again.'
        setErrors({ general: errorMessage })
        toast({
          title: 'Connection Error',
          description: errorMessage,
          variant: 'destructive'
        })
      }
      dispatch(setError('Registration failed'))
    } finally {
      setLocalLoading(false)
      dispatch(setLoading(false))
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-lg border bg-card p-8 shadow-sm"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {errors.general && (
          <Alert variant="destructive">
            <AlertDescription>{errors.general}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="first_name">First Name</Label>
            <Input
              id="first_name"
              type="text"
              placeholder="Maria"
              value={formData.first_name}
              onChange={(e) => handleChange('first_name', e.target.value)}
              required
              disabled={loading}
            />
            {errors.first_name && (
              <p className="text-sm text-destructive">{errors.first_name}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="last_name">Last Name</Label>
            <Input
              id="last_name"
              type="text"
              placeholder="Garcia"
              value={formData.last_name}
              onChange={(e) => handleChange('last_name', e.target.value)}
              required
              disabled={loading}
            />
            {errors.last_name && (
              <p className="text-sm text-destructive">{errors.last_name}</p>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="your@email.com"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            required
            disabled={loading}
          />
          {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="role">I am a...</Label>
          <Select
            value={formData.role}
            onValueChange={(value) => handleChange('role', value)}
            disabled={loading}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select your role" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newcomer">Newcomer (seeking resources)</SelectItem>
              <SelectItem value="community_member">Community Member (offering support)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="address">Address</Label>
          <Input
            id="address"
            type="text"
            placeholder="123 Main St, Hamilton, ON"
            value={formData.address}
            onChange={(e) => handleChange('address', e.target.value)}
            required
            disabled={loading}
          />
          <p className="text-xs text-muted-foreground">
            We&apos;ll use this to connect you with your nearest community hub and local mentors
          </p>
          {errors.address && <p className="text-sm text-destructive">{errors.address}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Password
            </div>
          </Label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              required
              disabled={loading}
              className="pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              disabled={loading}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          
          {/* Password Strength Indicator */}
          {passwordTouched && formData.password && passwordStrength && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-300"
                    style={{ 
                      width: `${(passwordStrength.score / 5) * 100}%`,
                      backgroundColor: passwordStrength.score <= 1 ? '#ef4444' : 
                                      passwordStrength.score <= 3 ? '#f97316' : 
                                      passwordStrength.score === 4 ? '#eab308' : 
                                      passwordStrength.score === 5 ? '#22c55e' : '#10b981'
                    }}
                  />
                </div>
                <span className="text-xs font-medium">{passwordStrength.label}</span>
              </div>
              
              {passwordStrength.feedback.length > 0 && (
                <div className="space-y-1">
                  {passwordStrength.feedback.map((tip, index) => (
                    <div key={index} className="flex items-center gap-2 text-xs text-muted-foreground">
                      <X className="h-3 w-3 text-red-500" />
                      {tip}
                    </div>
                  ))}
                </div>
              )}
              
              {passwordStrength.isValid && (
                <div className="flex items-center gap-2 text-xs text-green-600">
                  <Check className="h-3 w-3" />
                  All requirements met! ✓
                </div>
              )}
            </div>
          )}
          
          {!passwordTouched && (
            <div className="space-y-1 text-xs text-muted-foreground">
              <p className="font-medium">Password requirements:</p>
              <ul className="space-y-0.5 pl-4">
                <li>• At least 8 characters (12+ recommended)</li>
                <li>• Mix of uppercase and lowercase letters</li>
                <li>• At least one number</li>
                <li>• At least one special character (!@#$%^&*)</li>
              </ul>
            </div>
          )}
          
          {errors.password && (
            <p className="text-sm text-destructive">{errors.password}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password_confirm">Confirm Password</Label>
          <div className="relative">
            <Input
              id="password_confirm"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={formData.password_confirm}
              onChange={(e) => handleChange('password_confirm', e.target.value)}
              required
              disabled={loading}
              className="pr-10"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              disabled={loading}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.password_confirm && (
            <p className="text-sm text-destructive">{errors.password_confirm}</p>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating account...
            </>
          ) : (
            'Create account'
          )}
        </Button>

        <div className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link href="/login" className="text-primary hover:underline font-medium">
            Sign in
          </Link>
        </div>
      </form>
    </motion.div>
  )
}
