'use client'

import { use, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { communityService, UserProfile } from '@/lib/api-services'
import { 
  User, 
  Award, 
  MessageSquare, 
  Package, 
  CheckCircle, 
  Users, 
  Globe, 
  Sparkles,
  Calendar
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export default function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter()
  const { toast } = useToast()
  const resolvedParams = use(params)
  const { isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await communityService.getUserProfile(resolvedParams.id)
      setProfile(data)
    } catch (err) {
      console.error('Failed to fetch profile:', err)
      const error = err as { response?: { data?: { error?: string } } }
      setError(error.response?.data?.error || 'Failed to load profile')
      toast({
        title: 'Error',
        description: 'Failed to load profile',
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated && resolvedParams.id) {
      fetchProfile()
    }
  }, [isAuthenticated, resolvedParams.id])

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      newcomer: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      community_member: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      steward: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
      admin: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    }
    return colors[role] || colors.newcomer
  }

  const formatRole = (role: string) => {
    return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  }

  if (!isAuthenticated || authLoading) {
    return null
  }

  return (
    <AppLayout breadcrumbOverride={profile?.full_name}>
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {loading ? (
          <ProfileSkeleton />
        ) : error ? (
          <div className="text-center py-12">
            <User className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-2xl font-semibold mb-2">Profile Not Found</h2>
            <p className="text-muted-foreground">{error}</p>
          </div>
        ) : profile ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            {/* Profile Header */}
            <Card className="p-8">
              <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
                <Avatar className="w-24 h-24 text-2xl">
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {getInitials(profile.full_name)}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <h1 className="text-3xl font-bold">{profile.full_name}</h1>
                    <Badge className={getRoleBadgeColor(profile.role)}>
                      {formatRole(profile.role)}
                    </Badge>
                    {profile.is_mentor && (
                      <Badge variant="outline" className="border-amber-500 text-amber-700 dark:text-amber-400">
                        <Sparkles className="w-3 h-3 mr-1" />
                        Mentor
                      </Badge>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      Member since {profile.member_since}
                    </div>
                    {profile.languages_spoken && (
                      <div className="flex items-center gap-1">
                        <Globe className="w-4 h-4" />
                        {Array.isArray(profile.languages_spoken) 
                          ? profile.languages_spoken.join(', ')
                          : profile.languages_spoken}
                      </div>
                    )}
                  </div>

                  {profile.bio && (
                    <p className="text-muted-foreground leading-relaxed">{profile.bio}</p>
                  )}
                </div>
              </div>
            </Card>

            {/* Skills */}
            {profile.skills && (
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  Skills & Interests
                </h2>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    const skills = profile.skills
                    let skillsArray: string[] = []
                    
                    if (Array.isArray(skills)) {
                      skillsArray = skills
                    } else if (typeof skills === 'string') {
                      skillsArray = skills.split(',').map((s: string) => s.trim())
                    }
                    
                    return skillsArray.map((skill: string, index: number) => (
                      <Badge key={index} variant="secondary">
                        {skill}
                      </Badge>
                    ))
                  })()}
                </div>
              </Card>
            )}

            {/* Contribution Stats */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Award className="w-5 h-5 text-primary" />
                Contributions
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  icon={<Package className="w-5 h-5" />}
                  label="Items Shared"
                  value={profile.contribution_stats.items_contributed}
                />
                <StatCard
                  icon={<CheckCircle className="w-5 h-5" />}
                  label="Successful Loans"
                  value={profile.contribution_stats.successful_reservations}
                />
                {profile.is_mentor && (
                  <StatCard
                    icon={<Users className="w-5 h-5" />}
                    label="Active Mentorships"
                    value={profile.contribution_stats.active_mentorships}
                  />
                )}
                <StatCard
                  icon={<MessageSquare className="w-5 h-5" />}
                  label="Positive Reviews"
                  value={profile.contribution_stats.positive_feedback_count}
                />
              </div>
            </Card>

            {/* Badges */}
            {profile.badges_earned && profile.badges_earned.length > 0 && (
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                  <Award className="w-5 h-5 text-primary" />
                  Badges Earned ({profile.badges_earned.length})
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {profile.badges_earned.slice(0, 12).map((userBadge) => (
                    <motion.div
                      key={userBadge.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex flex-col items-center gap-2 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow"
                    >
                      <div 
                        className="text-4xl p-3 rounded-full"
                        style={{ backgroundColor: `${userBadge.badge.color}20` }}
                      >
                        {userBadge.badge.icon}
                      </div>
                      <div className="text-center">
                        <p className="font-medium text-sm">{userBadge.badge.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(userBadge.awarded_at).toLocaleDateString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
                
                {profile.badges_earned.length > 12 && (
                  <p className="text-center text-sm text-muted-foreground mt-4">
                    + {profile.badges_earned.length - 12} more badges
                  </p>
                )}
              </Card>
            )}
          </motion.div>
        ) : null}
      </div>
    </AppLayout>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="flex flex-col items-center gap-2 p-4 rounded-lg border bg-card">
      <div className="text-primary">{icon}</div>
      <div className="text-center">
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </div>
    </div>
  )
}

function ProfileSkeleton() {
  return (
    <div className="space-y-8">
      <Card className="p-8">
        <div className="flex gap-6 items-center">
          <Skeleton className="w-24 h-24 rounded-full" />
          <div className="flex-1 space-y-3">
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-full max-w-md" />
          </div>
        </div>
      </Card>
      <Card className="p-6">
        <Skeleton className="h-6 w-48 mb-4" />
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </Card>
    </div>
  )
}
