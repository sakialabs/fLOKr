'use client'

import { OnboardingForm } from '@/components/onboarding/onboarding-form'
import { motion } from 'framer-motion'

export default function OnboardingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl space-y-8"
      >
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold tracking-tight text-foreground">
            Welcome to fLOKr
          </h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Let&apos;s personalize your experience
          </p>
        </motion.div>
        <OnboardingForm />
      </motion.div>
    </div>
  )
}
