'use client'

import { Mail, MessageCircle, Users } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-background">
      <AppHeader />
      <div className="max-w-3xl mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Get in Touch</h1>
            <p className="text-lg text-muted-foreground">
              We&apos;re here to help you thrive in your new community.
            </p>
          </div>

          <Card className="p-8 mb-8">
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold mb-4">Contact Us</h2>
                <p className="text-muted-foreground mb-6">
                  fLOKr exists to empower refugees and newcomers with dignity and community support. Whether you need help, have questions, or want to contribute to our mission, we&apos;d love to hear from you.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                  <Mail className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Email Support</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      For general inquiries, support requests, or partnership opportunities
                    </p>
                    <a href="mailto:support@flokr.org" className="text-primary hover:underline">
                      support@flokr.org
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                  <MessageCircle className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Community Help</h3>
                    <p className="text-sm text-muted-foreground">
                      Connect with Ori, our AI assistant, or reach out to community mentors through the platform for immediate support and guidance.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                  <Users className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Response Time</h3>
                    <p className="text-sm text-muted-foreground">
                      We typically respond within 24-48 hours. For urgent matters, please reach out through your local hub or community coordinator.
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-6 border-t">
                <p className="text-sm text-muted-foreground">
                  Together, we build communities where everyone belongs. Your voice matters, and we&apos;re committed to supporting your journey with respect and care.
                </p>
              </div>
            </div>
          </Card>

          <div className="text-center">
            <Button 
              onClick={() => window.history.back()}
              variant="outline"
            >
              Back to Platform
            </Button>
          </div>
        </motion.div>
      </div>      <Footer />    </div>
  )
}
