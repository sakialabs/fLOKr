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
} from 'lucide-react'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'

interface LeftSidebarProps {
  collapsed: boolean
  onToggle: () => void
}

const navItems = [
  { href: '/home', label: 'My Home', icon: Home },
  { href: '/reservations', label: 'My Reservations', icon: Calendar },
  { href: '/items', label: 'My Items', icon: Package },
  { href: '/hubs', label: 'Hubs', icon: MapPin },
  { href: '/community', label: 'Community Space', icon: Users },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export function LeftSidebar({ collapsed, onToggle }: LeftSidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const dispatch = useDispatch()
  const user = useSelector((state: RootState) => state.auth.user)

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
              className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-semibold flex-shrink-0 cursor-pointer hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#D97A5B]"
            >
              {user.first_name[0]}{user.last_name[0]}
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
              className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-xs font-semibold cursor-pointer hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all duration-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#D97A5B]"
            >
              {user.first_name[0]}{user.last_name[0]}
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
          {navItems.map((item) => {
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
        </div>
      </nav>

      {/* Logout Button */}
      <div className="border-t border-border p-3 flex-shrink-0">
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
    </motion.aside>
  )
}
