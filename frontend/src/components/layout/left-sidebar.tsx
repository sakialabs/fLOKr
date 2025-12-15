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
  User,
} from 'lucide-react'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'

interface LeftSidebarProps {
  collapsed: boolean
  onToggle: () => void
}

const navItems = [
  { href: '/home', label: 'Home', icon: Home },
  { href: '/reservations', label: 'My Reservations', icon: Calendar },
  { href: '/items', label: 'My Items', icon: Package },
  { href: '/hubs', label: 'Hubs', icon: MapPin },
  { href: '/community', label: 'Community', icon: Users },
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
      animate={{ width: collapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="border-r border-border bg-card flex flex-col"
    >
      {/* Header with Logo and Toggle */}
      <div className="p-4 border-b border-border">
        {!collapsed && (
          <div className="flex items-center justify-between mb-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Link href="/home" className="flex items-center gap-3 group">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/20 transition-colors">
                  <Logo size={24} className="group-hover:opacity-80 transition-opacity" />
                </div>
                <h1 className="text-2xl font-bold text-primary cursor-pointer group-hover:opacity-80 transition-opacity">
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
            className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
          >
            <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold flex-shrink-0">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user.email}
              </p>
            </div>
            <ThemeToggle />
          </motion.div>
        )}

        {collapsed && user && (
          <div className="flex flex-col items-center gap-3 mt-2">
            <div className="h-12 w-12 rounded-full bg-primary flex items-center justify-center text-primary-foreground font-semibold">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <div className="flex justify-center">
              <ThemeToggle />
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6">
        <div className="space-y-3 px-3">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <Link key={item.href} href={item.href}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`flex items-center ${collapsed ? 'justify-center' : 'gap-3'} px-3 py-3.5 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="text-sm font-medium"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </motion.div>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Logout Button */}
      <div className="border-t border-border p-4">
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
