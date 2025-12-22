'use client'

import { Shield, Eye, Lock, Heart, ArrowLeft } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'
import { motion } from 'framer-motion'
import Link from 'next/link'

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-background">
      <AppHeader />
      <div className="max-w-4xl mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Button asChild variant="ghost" size="sm" className="mb-6">
            <Link href="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Platform
            </Link>
          </Button>
          
          <div className="text-center mb-12">
            <Shield className="h-16 w-16 text-primary mx-auto mb-4" />
            <h1 className="text-4xl font-bold mb-4">Privacy Policy</h1>
            <p className="text-lg text-muted-foreground">
              Your trust is sacred. We protect your data with care and transparency.
            </p>
          </div>

          <Card className="p-8 mb-8">
            <div className="prose prose-neutral dark:prose-invert max-w-none space-y-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Heart className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">Our Commitment</h2>
                </div>
                <p className="text-muted-foreground">
                  fLOKr exists to empower refugees and newcomers with dignity. We collect only what&apos;s necessary to serve you, never sell your data, and treat your information with the respect you deserve. Your privacy is not just policy—it&apos;s principle.
                </p>
              </div>

              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">What We Collect</h2>
                </div>
                <p className="text-muted-foreground mb-3">We collect minimal information to provide you with community services:</p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li><strong>Account Information:</strong> Name, email, phone, language preferences, and profile details you choose to share</li>
                  <li><strong>Platform Activity:</strong> Items you list, reserve, or transfer; hubs you join; connections you make</li>
                  <li><strong>Communication:</strong> Messages with Ori (our AI assistant), community interactions, and support requests</li>
                  <li><strong>Technical Data:</strong> Device info, IP address, and usage patterns to improve security and service quality</li>
                </ul>
              </div>

              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Lock className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">How We Use Your Data</h2>
                </div>
                <p className="text-muted-foreground mb-3">Your information serves one purpose: helping you thrive.</p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li><strong>Service Delivery:</strong> Connect you with resources, enable reservations, facilitate community support</li>
                  <li><strong>Personalization:</strong> Ori learns your preferences to provide helpful, relevant guidance</li>
                  <li><strong>Safety:</strong> Prevent fraud, ensure fair access, and maintain community trust</li>
                  <li><strong>Improvement:</strong> Understand how the platform is used to build better features</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                  We <strong>never</strong> sell your data, share it with advertisers, or use it for purposes beyond serving our community.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
                <p className="text-muted-foreground mb-3">You have complete control over your information:</p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li><strong>Access:</strong> View all data we hold about you</li>
                  <li><strong>Correction:</strong> Update or correct your information anytime</li>
                  <li><strong>Deletion:</strong> Request removal of your account and data</li>
                  <li><strong>Portability:</strong> Download your data in a standard format</li>
                  <li><strong>Objection:</strong> Opt out of specific data uses</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                  Contact us at <a href="mailto:privacy@flokr.org" className="text-primary hover:underline">privacy@flokr.org</a> to exercise any of these rights.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
                <p className="text-muted-foreground">
                  We protect your information with industry-standard encryption, secure servers, and regular security audits. While no system is 100% secure, we take every reasonable measure to safeguard your data.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Children&apos;s Privacy</h2>
                <p className="text-muted-foreground">
                  fLOKr is intended for users 16 and older. We do not knowingly collect information from children under 16. If you believe a child has created an account, please contact us immediately.
                </p>
              </div>

              <div className="pt-6 border-t">
                <p className="text-sm text-muted-foreground">
                  <strong>Last Updated:</strong> December 2025<br />
                  Questions? Email <a href="mailto:privacy@flokr.org" className="text-primary hover:underline">privacy@flokr.org</a>
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
