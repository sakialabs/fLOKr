'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDispatch } from 'react-redux'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { authService, tokenManager } from '@/lib/auth'
import { setCredentials, setLoading, setError } from '@/store/slices/authSlice'
import { Loader2, Eye, EyeOff } from 'lucide-react'

export function LoginForm() {
  const router = useRouter()
  const dispatch = useDispatch()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLocalLoading] = useState(false)
  const [error, setLocalError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)
    setLocalLoading(true)
    dispatch(setLoading(true))

    try {
      const response = await authService.login({ email, password })
      
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

      // Small delay for smooth transition
      setTimeout(() => {
        router.push('/home')
      }, 100)
    } catch (err) {
      const error = err as { response?: { data?: { non_field_errors?: string[]; detail?: string } } }
      const errorMessage =
        error.response?.data?.non_field_errors?.[0] ||
        error.response?.data?.detail ||
        'Invalid email or password'
      setLocalError(errorMessage)
      dispatch(setError(errorMessage))
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
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link
              href="/forgot-password"
              className="text-sm text-muted-foreground hover:text-primary transition-colors"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in...
            </>
          ) : (
            'Sign in'
          )}
        </Button>

        <div className="text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="text-primary hover:underline font-medium">
            Create one
          </Link>
        </div>
      </form>
    </motion.div>
  )
}
