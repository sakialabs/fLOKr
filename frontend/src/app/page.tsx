'use client'

import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

export default function Home() {
  const router = useRouter()
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated)
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  useEffect(() => {
    if (isClient && isAuthenticated) {
      router.push('/home')
    }
  }, [isClient, isAuthenticated, router])

  if (!isClient) {
    return null // Prevent flash of content during hydration
  }

  if (isAuthenticated) {
    return null // Redirecting...
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 }
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <AppHeader />
      {/* Hero Section */}
      <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="max-w-4xl mx-auto text-center space-y-8"
        >
          <motion.div variants={itemVariants} className="space-y-6">
            <div className="flex justify-center">
              <motion.div
                whileHover={{ scale: 1.05, rotate: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="relative"
              >
                {/* Main logo circle */}
                <div className="h-32 w-32 rounded-full bg-gradient-to-br from-primary/20 via-primary/10 to-background flex items-center justify-center backdrop-blur-sm border-2 border-primary/30 shadow-2xl">
                  <Logo size={96} className="text-primary" />
                </div>
                
                {/* Animated outer ring */}
                <motion.div
                  animate={{
                    scale: [1, 1.15, 1],
                    opacity: [0.6, 0.2, 0.6],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute inset-0 rounded-full border-2 border-primary/40"
                />
                
                {/* Secondary pulse ring */}
                <motion.div
                  animate={{
                    scale: [1, 1.25, 1],
                    opacity: [0.4, 0, 0.4],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 0.5
                  }}
                  className="absolute inset-0 rounded-full border-2 border-primary/30"
                />
                
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-full bg-primary/5 blur-xl" />
              </motion.div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
              Welcome to <span className="text-primary">fLOKr</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
              Community resource sharing with dignity. Connect, share, and support each other.
            </p>
          </motion.div>

          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href="/register">Get Started</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
              <Link href="/login">Sign In</Link>
            </Button>
          </motion.div>

          <motion.div
            variants={containerVariants}
            className="grid md:grid-cols-3 gap-6 mt-16 text-left"
          >
            <motion.div variants={itemVariants} className="p-6 rounded-lg border bg-card hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Share Resources</h3>
              <p className="text-muted-foreground">
                Access essential items like clothing, household goods, and more from your community.
              </p>
            </motion.div>
            <motion.div variants={itemVariants} className="p-6 rounded-lg border bg-card hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Find Mentorship</h3>
              <p className="text-muted-foreground">
                Connect with experienced community members who can guide and support you.
              </p>
            </motion.div>
            <motion.div variants={itemVariants} className="p-6 rounded-lg border bg-card hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Build Community</h3>
              <p className="text-muted-foreground">
                Join events, share experiences, and strengthen bonds with your neighbors.
              </p>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  )
}
