'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '@/store'
import { logout } from '@/store/slices/authSlice'
import { tokenManager } from '@/lib/auth'
import {
  Home,
  Calendar,
  Package,
  MapPin,
  Users,
  Settings,
  Menu,
  X,
  LogOut,
  Shield,
  BarChart3,
  ClipboardCheck,
  MessageCircle,
  Award,
  Sparkles,
  MessageSquare,
} from 'lucide-react'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'

interface LeftSidebarProps {
  collapsed: boolean
  onToggle: () => void
}

const baseNavItems = [
  { href: '/home', label: 'My Home', icon: Home, roles: ['all'] },
  { href: '/reservations', label: 'My Reservations', icon: Calendar, roles: ['all'] },
  { href: '/items', label: 'Available Items', icon: Package, roles: ['all'] },
  { href: '/hubs', label: 'Hubs', icon: MapPin, roles: ['all'] },
  { href: '/community/leaderboard', label: 'Community Highlights', icon: Sparkles, roles: ['all'] },
  { href: '/community/mentorship', label: 'Mentorship', icon: Users, roles: ['all'] },
  { href: '/community/feedback', label: 'Feedback', icon: MessageSquare, roles: ['all'] },
]

const stewardNavItems = [
  { href: '/dashboard/steward', label: 'Steward Dashboard', icon: ClipboardCheck, roles: ['steward'] },
]

const adminNavItems = [
  { href: '/dashboard/admin', label: 'Admin Dashboard', icon: Shield, roles: ['admin'] },
  { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart3, roles: ['admin'] },
]

export function LeftSidebar({ collapsed, onToggle }: LeftSidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const dispatch = useDispatch()
  const user = useSelector((state: RootState) => state.auth.user)

  const getAvatarUrl = () => {
    if (!user) return null
    
    if (user.avatar_choice) {
      return `/avatars/${user.avatar_choice}.png`
    }
    
    if (user.profile_picture && user.profile_picture.trim()) {
      return user.profile_picture
    }
    
    return null
  }

  const getInitials = () => {
    if (!user) return '?'
    
    const firstInitial = user.first_name?.[0]?.toUpperCase() || ''
    const lastInitial = user.last_name?.[0]?.toUpperCase() || ''
    
    return firstInitial + lastInitial || '?'
  }

  const handleLogout = () => {
    tokenManager.clearTokens()
    dispatch(logout())
    router.push('/login')
  }

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 256 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="border-r border-border bg-card flex flex-col flex-shrink-0"
    >
      {/* Header with Logo and Toggle */}
      <div className="p-3 border-b border-border flex-shrink-0">
        {!collapsed && (
          <div className="flex items-center justify-between mb-3">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="min-w-0 flex-1"
            >
              <Link href="/home" className="flex items-center gap-2 group min-w-0">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                  <Logo size={20} className="group-hover:opacity-80 transition-opacity" />
                </div>
                <h1 className="text-xl font-bold text-primary cursor-pointer group-hover:opacity-80 transition-opacity truncate">
                  fLOKr
                </h1>
              </Link>
            </motion.div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="hover:bg-muted"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
        )}
        
        {collapsed && (
          <div className="flex flex-col items-center gap-3 mb-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="hover:bg-muted"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <Link href="/home" className="group">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <Logo size={24} className="group-hover:opacity-80 transition-opacity" />
              </div>
            </Link>
          </div>
        )}

        {/* User Profile Card */}
        {!collapsed && user && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 p-2 rounded-lg bg-muted/50"
          >
            <button
              onClick={() => router.push('/profile')}
              className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-semibold flex-shrink-0 cursor-pointer hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-300 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#D97A5B]"
              style={{
                backgroundImage: getAvatarUrl() ? `url(${getAvatarUrl()})` : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              {!getAvatarUrl() && `${user.first_name[0]}${user.last_name[0]}`}
            </button>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold truncate">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-[10px] text-muted-foreground truncate">
                {user.email}
              </p>
            </div>
            <div className="flex-shrink-0">
              <ThemeToggle />
            </div>
          </motion.div>
        )}

        {collapsed && user && (
          <div className="flex flex-col items-center gap-2 mt-2">
            <button
              onClick={() => router.push('/profile')}
              className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-semibold cursor-pointer hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-300 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#D97A5B]"
              style={{
                backgroundImage: getAvatarUrl() ? `url(${getAvatarUrl()})` : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              {!getAvatarUrl() && getInitials()}
            </button>
            <div className="flex justify-center">
              <ThemeToggle />
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <div className="space-y-1 px-2">
          {/* Base Navigation */}
          {baseNavItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <button
                key={item.href}
                onClick={() => router.push(item.href)}
                className={`w-full flex items-center ${collapsed ? 'justify-center' : 'gap-2'} px-2 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                }`}
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                {!collapsed && (
                  <span className="text-sm font-medium truncate">
                    {item.label}
                  </span>
                )}
              </button>
            )
          })}

          {/* Steward Navigation */}
          {user && (user.role === 'steward' || user.role === 'admin') && (
            <>
              {!collapsed && (
                <div className="pt-4 pb-2">
                  <p className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Steward
                  </p>
                </div>
              )}
              {stewardNavItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                
                return (
                  <button
                    key={item.href}
                    onClick={() => router.push(item.href)}
                    className={`w-full flex items-center ${collapsed ? 'justify-center' : 'gap-2'} px-2 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    }`}
                  >
                    <Icon className="h-4 w-4 flex-shrink-0" />
                    {!collapsed && (
                      <span className="text-sm font-medium truncate">
                        {item.label}
                      </span>
                    )}
                  </button>
                )
              })}
            </>
          )}

          {/* Admin Navigation */}
          {user && user.role === 'admin' && (
            <>
              {!collapsed && (
                <div className="pt-4 pb-2">
                  <p className="px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Admin
                  </p>
                </div>
              )}
              {adminNavItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                
                return (
                  <button
                    key={item.href}
                    onClick={() => router.push(item.href)}
                    className={`w-full flex items-center ${collapsed ? 'justify-center' : 'gap-2'} px-2 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    }`}
                  >
                    <Icon className="h-4 w-4 flex-shrink-0" />
                    {!collapsed && (
                      <span className="text-sm font-medium truncate">
                        {item.label}
                      </span>
                    )}
                  </button>
                )
              })}
            </>
          )}
        </div>
      </nav>

      {/* Footer: Settings & Logout */}
      <div className="border-t border-border p-3 flex-shrink-0">
        <div className="space-y-1">
          {/* Settings Button */}
          <button
            onClick={() => router.push('/settings')}
            className={`w-full flex items-center ${
              collapsed ? 'justify-center' : 'gap-2'
            } px-2 py-2 rounded-lg transition-colors ${
              pathname === '/settings'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            }`}
          >
            <Settings className="h-4 w-4 flex-shrink-0" />
            {!collapsed && (
              <span className="text-sm font-medium truncate">Settings</span>
            )}
          </button>

          {/* Logout Button */}
          {!collapsed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="w-full justify-start text-muted-foreground hover:text-foreground"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          )}
          {collapsed && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="w-full"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </motion.aside>
  )
}
