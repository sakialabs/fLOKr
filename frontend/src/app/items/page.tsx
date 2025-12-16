'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Package, Search } from 'lucide-react'

export default function ItemsPage() {
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
      transition: { duration: 0.4 }
    }
  }

  return (
    <AppLayout>
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="space-y-6"
      >
        <motion.div variants={itemVariants} className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Available Items</h1>
            <p className="text-muted-foreground">
              Browse and reserve community resources
            </p>
          </div>
          <Button>
            <Search className="h-4 w-4 mr-2" />
            Search Items
          </Button>
        </motion.div>

        <motion.div
          variants={containerVariants}
          className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
        >
          <motion.div variants={itemVariants} whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center gap-2 min-w-0">
                  <Package className="h-5 w-5 text-primary flex-shrink-0" />
                  <CardTitle className="truncate">Clothing</CardTitle>
                </div>
                <CardDescription className="line-clamp-2">Winter coats, shoes, and more</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Coming soon</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants} whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center gap-2 min-w-0">
                  <Package className="h-5 w-5 text-primary flex-shrink-0" />
                  <CardTitle className="truncate">Household</CardTitle>
                </div>
                <CardDescription className="line-clamp-2">Furniture, kitchenware, and essentials</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Coming soon</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div variants={itemVariants} whileHover={{ scale: 1.02 }} transition={{ type: "spring", stiffness: 300 }}>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center gap-2 min-w-0">
                  <Package className="h-5 w-5 text-primary flex-shrink-0" />
                  <CardTitle className="truncate">Electronics</CardTitle>
                </div>
                <CardDescription className="line-clamp-2">Phones, laptops, and devices</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Coming soon</p>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </motion.div>
    </AppLayout>
  )
}
