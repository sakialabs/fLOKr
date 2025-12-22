'use client'

import { RegisterForm } from '@/components/auth/register-form'
import { Logo } from '@/components/ui/logo'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'
import { motion } from 'framer-motion'

export default function RegisterPage() {
  return (
    <>
      <AppHeader />
      <div className="flex-1 flex items-center justify-center bg-background p-4 py-12">
      <div className="w-full max-w-2xl space-y-8">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <motion.div
              whileHover={{ scale: 1.05, rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
              className="relative"
            >
              {/* Main logo circle */}
              <div className="h-24 w-24 rounded-full bg-muted/80 backdrop-blur-sm flex items-center justify-center border-2 border-muted-foreground/20 shadow-xl">
                <Logo size={64} href="/" showBackground={false} />
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
                className="absolute inset-0 rounded-full border-2 border-muted-foreground/30"
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
                className="absolute inset-0 rounded-full border-2 border-muted-foreground/20"
              />
              
              {/* Glow effect */}
              <div className="absolute inset-0 rounded-full bg-muted/10 blur-xl" />
            </motion.div>
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Join fLOKr
          </h1>
          <p className="mt-2 text-muted-foreground">
            Connect with your community and access resources with dignity
          </p>
        </div>
        <RegisterForm />
      </div>
      </div>
      <Footer />
    </>
  )
}
