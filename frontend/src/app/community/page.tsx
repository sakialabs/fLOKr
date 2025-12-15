'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { AppLayout } from '@/components/layout/app-layout'
import { CommunityFeed } from '@/components/feed/community-feed'

export default function CommunityPage() {
  const router = useRouter()
  const { isAuthenticated, loading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, loading, router])

  if (loading || !isAuthenticated) {
    return null
  }

  return (
    <AppLayout>
      <CommunityFeed />
    </AppLayout>
  )
}
