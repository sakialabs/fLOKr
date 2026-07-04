'use client'

import { Bug, Github, MessageCircle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'
import { GITHUB_ISSUES_URL, GITHUB_REPO_URL } from '@/lib/project-links'

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
                  <Github className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">GitHub Repo</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      For general inquiries, support requests, or partnership opportunities while the public site is not live yet
                    </p>
                    <a href={GITHUB_REPO_URL} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                      Open GitHub repo
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                  <Bug className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Report an Issue</h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      Found a bug, broken flow, or confusing copy? Open an issue and include the page or steps.
                    </p>
                    <a href={GITHUB_ISSUES_URL} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                      Open GitHub issues
                    </a>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg bg-muted/50">
                  <MessageCircle className="h-6 w-6 text-primary mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Community Help</h3>
                    <p className="text-sm text-muted-foreground">
                      Connect with Navi, our community guide, or reach out to Leads through the platform. For urgent matters, please contact your local hub or community coordinator.
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
