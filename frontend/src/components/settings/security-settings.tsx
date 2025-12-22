'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { Lock, Eye, EyeOff, Loader2, ShieldCheck } from 'lucide-react'

export function SecuritySettings() {
  const [loading, setLoading] = useState(false)
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    new_password_confirm: ''
  })

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (formData.new_password !== formData.new_password_confirm) {
      toast.error('New passwords do not match')
      return
    }

    if (formData.new_password.length < 8) {
      toast.error('Password must be at least 8 characters long')
      return
    }

    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile/change-password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        const error = await response.json()
        // Handle specific error messages
        if (error.current_password) {
          throw new Error('Current password is incorrect')
        }
        throw new Error(error.detail || 'Failed to change password')
      }

      await response.json()
      
      toast.success('Password changed successfully! Please log in again.')
      
      // Clear form
      setFormData({
        current_password: '',
        new_password: '',
        new_password_confirm: ''
      })

      // Optional: logout user and redirect to login
      // setTimeout(() => {
      //   localStorage.removeItem('access_token')
      //   localStorage.removeItem('refresh_token')
      //   window.location.href = '/login'
      // }, 2000)

    } catch (error) {
      const err = error as Error
      toast.error(err.message || 'Failed to change password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <CardTitle>Change Password</CardTitle>
          </div>
          <CardDescription>
            Update your password to keep your account secure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Current Password */}
            <div className="space-y-2">
              <Label htmlFor="current_password">Current Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="current_password"
                  type={showPasswords.current ? 'text' : 'password'}
                  value={formData.current_password}
                  onChange={(e) => handleChange('current_password', e.target.value)}
                  className="pl-9 pr-10"
                  placeholder="Enter current password"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('current')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  disabled={loading}
                >
                  {showPasswords.current ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div className="space-y-2">
              <Label htmlFor="new_password">New Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="new_password"
                  type={showPasswords.new ? 'text' : 'password'}
                  value={formData.new_password}
                  onChange={(e) => handleChange('new_password', e.target.value)}
                  className="pl-9 pr-10"
                  placeholder="Enter new password"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('new')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  disabled={loading}
                >
                  {showPasswords.new ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              <p className="text-xs text-muted-foreground">
                Must be at least 8 characters long
              </p>
            </div>

            {/* Confirm New Password */}
            <div className="space-y-2">
              <Label htmlFor="new_password_confirm">Confirm New Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="new_password_confirm"
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={formData.new_password_confirm}
                  onChange={(e) => handleChange('new_password_confirm', e.target.value)}
                  className="pl-9 pr-10"
                  placeholder="Confirm new password"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('confirm')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  disabled={loading}
                >
                  {showPasswords.confirm ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            <Button type="submit" disabled={loading} className="w-full">
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Change Password
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Security Tips Card */}
      <Card>
        <CardHeader>
          <CardTitle>Security Tips</CardTitle>
          <CardDescription>Keep your account secure</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <div className="mt-0.5">•</div>
            <p>Use a unique password that you don&apos;t use anywhere else</p>
          </div>
          <div className="flex items-start gap-2">
            <div className="mt-0.5">•</div>
            <p>Make sure your password is at least 8 characters long</p>
          </div>
          <div className="flex items-start gap-2">
            <div className="mt-0.5">•</div>
            <p>Include a mix of letters, numbers, and special characters</p>
          </div>
          <div className="flex items-start gap-2">
            <div className="mt-0.5">•</div>
            <p>Don&apos;t share your password with anyone</p>
          </div>
          <div className="flex items-start gap-2">
            <div className="mt-0.5">•</div>
            <p>Change your password regularly for better security</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
