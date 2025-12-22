'use client'

import { Badge as BadgeType, UserBadge } from '@/lib/api-services'
import { Card, CardContent } from '@/components/ui/card'
import { motion } from 'framer-motion'
import { Lock } from 'lucide-react'

interface BadgeDisplayProps {
  userBadges: UserBadge[]
  allBadges?: BadgeType[]
  showLocked?: boolean
}

export function BadgeDisplay({ userBadges, allBadges = [], showLocked = true }: BadgeDisplayProps) {
  const earnedBadgeIds = new Set(userBadges.map(ub => ub.badge.id))
  
  const categories = {
    'arrival': 'Arrival & Belonging',
    'contribution': 'Contribution & Care',
    'community': 'Community Energy',
    'trust': 'Steward & Trust',
    'milestone': 'Milestone',
    'mentorship': 'Mentorship'
  }

  const badgesByCategory = userBadges.reduce((acc, ub) => {
    const cat = ub.badge.category
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(ub)
    return acc
  }, {} as Record<string, UserBadge[]>)

  const lockedBadges = allBadges.filter(b => !earnedBadgeIds.has(b.id))

  return (
    <div className="space-y-6">
      {/* Earned Badges by Category */}
      {Object.entries(badgesByCategory).map(([category, badges]) => (
        <div key={category} className="space-y-3">
          <h3 className="text-lg font-semibold">{categories[category as keyof typeof categories] || category}</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {badges.map((userBadge) => (
              <motion.div
                key={userBadge.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0 }}
              >
                <Card 
                  className="group cursor-pointer hover:shadow-lg transition-all duration-200"
                  style={{ borderColor: userBadge.badge.color }}
                >
                  <CardContent className="p-4 text-center">
                    <div 
                      className="text-5xl mb-2 transform group-hover:scale-110 transition-transform"
                      style={{ color: userBadge.badge.color }}
                    >
                      {userBadge.badge.icon}
                    </div>
                    <h4 className="font-semibold text-sm mb-1">{userBadge.badge.name}</h4>
                    <p className="text-xs text-muted-foreground mb-2">{userBadge.badge.description}</p>
                    {userBadge.awarded_reason && (
                      <p className="text-xs italic text-primary/80 mt-2 border-t pt-2">
                        &quot;{userBadge.awarded_reason}&quot;
                      </p>
                    )}
                    <div className="text-xs text-muted-foreground mt-2">
                      {new Date(userBadge.awarded_at).toLocaleDateString('en-US', { 
                        month: 'short', 
                        year: 'numeric' 
                      })}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      ))}

      {/* Locked Badges (Coming Soon) */}
      {showLocked && lockedBadges.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-muted-foreground">Coming Soon</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {lockedBadges.slice(0, 8).map((badge) => (
              <Card key={badge.id} className="opacity-50">
                <CardContent className="p-4 text-center">
                  <div className="text-4xl mb-2 filter grayscale">
                    {badge.icon}
                  </div>
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <Lock className="h-3 w-3" />
                    <h4 className="font-semibold text-sm">???</h4>
                  </div>
                  <p className="text-xs text-muted-foreground">{badge.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* No Badges Yet */}
      {userBadges.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-6xl mb-4">🌱</div>
            <h3 className="text-lg font-semibold mb-2">Your Badge Journey Begins</h3>
            <p className="text-muted-foreground">
              Earn badges by contributing to the community, helping others, and being a reliable member.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
