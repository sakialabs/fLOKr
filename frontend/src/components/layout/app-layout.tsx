'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LeftSidebar } from './left-sidebar'
import { RightSidebar } from './right-sidebar'
import { DynamicBreadcrumbs } from './dynamic-breadcrumbs'
import { Footer } from './footer'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Search, User, MapPin, Package } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

interface AppLayoutProps {
  children: React.ReactNode
  breadcrumbOverride?: string
}

// Responsive breakpoint for collapsing sidebars (1280px = xl breakpoint)
const COLLAPSE_BREAKPOINT = 1280

export function AppLayout({ children, breadcrumbOverride }: AppLayoutProps) {
  const router = useRouter()
  // Initialize collapsed state based on screen size
  const [leftCollapsed, setLeftCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < COLLAPSE_BREAKPOINT
    }
    return false
  })
  const [rightCollapsed, setRightCollapsed] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth < COLLAPSE_BREAKPOINT
    }
    return false
  })
  const [shouldOpenOriChat, setShouldOpenOriChat] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<{
    users: any[]
    hubs: any[]
    items: any[]
  }>({ users: [], hubs: [], items: [] })
  const searchRef = useRef<HTMLDivElement>(null)

  // Handle screen resize to auto-collapse/expand sidebars
  useEffect(() => {
    const handleResize = () => {
      const isSmallScreen = window.innerWidth < COLLAPSE_BREAKPOINT
      setLeftCollapsed(isSmallScreen)
      setRightCollapsed(isSmallScreen)
    }

    // Add debounce to avoid too many updates
    let timeoutId: NodeJS.Timeout
    const debouncedResize = () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(handleResize, 150)
    }

    window.addEventListener('resize', debouncedResize)
    return () => {
      window.removeEventListener('resize', debouncedResize)
      clearTimeout(timeoutId)
    }
  }, [])

  useEffect(() => {
    const handleOpenOriChat = () => {
      setShouldOpenOriChat(true)
      setTimeout(() => setShouldOpenOriChat(false), 100)
    }
    window.addEventListener('openOriChat', handleOpenOriChat)
    return () => window.removeEventListener('openOriChat', handleOpenOriChat)
  }, [])

  // Global search functionality
  useEffect(() => {
    const performGlobalSearch = async () => {
      if (searchQuery.trim().length < 2) {
        setShowSearchResults(false)
        setSearchResults({ users: [], hubs: [], items: [] })
        return
      }

      setIsSearching(true)
      setShowSearchResults(true)

      try {
        // Search users
        const usersResponse = await api.get('/community/data/newcomers/')
        const allUsers = Array.isArray(usersResponse.data) ? usersResponse.data : usersResponse.data.results || []
        const matchedUsers = allUsers.filter((user: any) => 
          user.name?.toLowerCase().includes(searchQuery.toLowerCase())
        ).slice(0, 5)

        // Search items
        const itemsResponse = await api.get('/inventory/items/', {
          params: { search: searchQuery }
        })
        const allItems = Array.isArray(itemsResponse.data) ? itemsResponse.data : itemsResponse.data.results || []
        const matchedItems = allItems.slice(0, 5)

        // Search hubs (mock data for now - replace with real API when available)
        const matchedHubs = [
          { id: 1, name: 'Hub #3 - Eastside', location: 'Downtown' },
          { id: 2, name: 'Hub #5 - Westside', location: 'Suburbs' },
        ].filter(hub => 
          hub.name.toLowerCase().includes(searchQuery.toLowerCase())
        )

        setSearchResults({
          users: matchedUsers,
          hubs: matchedHubs,
          items: matchedItems
        })
      } catch (error) {
        console.error('Search failed:', error)
      } finally {
        setIsSearching(false)
      }
    }

    const debounceTimer = setTimeout(performGlobalSearch, 300)
    return () => clearTimeout(debounceTimer)
  }, [searchQuery])

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleResultClick = (type: 'user' | 'hub' | 'item', id: string | number) => {
    setShowSearchResults(false)
    setSearchQuery('')
    
    if (type === 'user') {
      router.push(`/profile/${id}`)
    } else if (type === 'hub') {
      router.push(`/hubs/${id}`)
    } else if (type === 'item') {
      router.push(`/items/${id}`)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/items?search=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Left Sidebar - Navigation */}
      <LeftSidebar collapsed={leftCollapsed} onToggle={() => setLeftCollapsed(!leftCollapsed)} />

      {/* Main Content - Feed */}
      <motion.main
        layout
        className="flex-1 overflow-y-auto min-w-0"
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        {/* Global Search Header */}
        <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
          <div className="max-w-6xl mx-auto p-4 flex justify-center">
            <div ref={searchRef} className="relative w-full max-w-2xl">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search hubs, items, users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => searchQuery.length >= 2 && setShowSearchResults(true)}
                className="pl-9"
              />
              
              {/* Search Results Dropdown */}
              <AnimatePresence>
                {showSearchResults && (searchResults.users.length > 0 || searchResults.hubs.length > 0 || searchResults.items.length > 0) && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card className="absolute top-full mt-2 w-full max-h-96 overflow-y-auto shadow-lg">
                      {isSearching ? (
                        <div className="p-4 text-center text-muted-foreground">Searching...</div>
                      ) : (
                        <div className="p-2">
                          {searchResults.users.length > 0 && (
                            <div className="mb-2">
                              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground">Users</div>
                              {searchResults.users.map((user: any) => (
                                <button
                                  key={user.id}
                                  onClick={() => handleResultClick('user', user.id)}
                                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-accent rounded-md text-left"
                                >
                                  <User className="h-4 w-4 text-muted-foreground" />
                                  <span className="text-sm">{user.name}</span>
                                </button>
                              ))}
                            </div>
                          )}
                          
                          {searchResults.hubs.length > 0 && (
                            <div className="mb-2">
                              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground">Hubs</div>
                              {searchResults.hubs.map((hub: any) => (
                                <button
                                  key={hub.id}
                                  onClick={() => handleResultClick('hub', hub.id)}
                                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-accent rounded-md text-left"
                                >
                                  <MapPin className="h-4 w-4 text-muted-foreground" />
                                  <div className="flex-1">
                                    <div className="text-sm">{hub.name}</div>
                                    <div className="text-xs text-muted-foreground">{hub.location}</div>
                                  </div>
                                </button>
                              ))}
                            </div>
                          )}
                          
                          {searchResults.items.length > 0 && (
                            <div>
                              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground">Items</div>
                              {searchResults.items.map((item: any) => (
                                <button
                                  key={item.id}
                                  onClick={() => handleResultClick('item', item.id)}
                                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-accent rounded-md text-left"
                                >
                                  <Package className="h-4 w-4 text-muted-foreground" />
                                  <div className="flex-1">
                                    <div className="text-sm">{item.title}</div>
                                    <div className="text-xs text-muted-foreground">{item.category}</div>
                                  </div>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-4 md:p-6">
          {/* Breadcrumbs */}
          <div className="mb-4">
            <DynamicBreadcrumbs override={breadcrumbOverride} />
          </div>
          
          {children}
        </div>

        {/* Footer */}
        <Footer />
      </motion.main>

      {/* Right Sidebar - Friends & Chat */}
      <RightSidebar 
        collapsed={rightCollapsed} 
        onToggle={() => setRightCollapsed(!rightCollapsed)}
        shouldOpenOriChat={shouldOpenOriChat}
      />
    </div>
  )
}
