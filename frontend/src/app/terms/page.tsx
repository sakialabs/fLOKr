'use client'

import { Scale, Heart, Users, Package, AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="max-w-4xl mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-12">
            <Scale className="h-16 w-16 text-primary mx-auto mb-4" />
            <h1 className="text-4xl font-bold mb-4">Terms of Service</h1>
            <p className="text-lg text-muted-foreground">
              Simple, fair guidelines for a dignified community.
            </p>
          </div>

          <Card className="p-8 mb-8">
            <div className="prose prose-neutral dark:prose-invert max-w-none space-y-8">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Heart className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">Our Mission</h2>
                </div>
                <p className="text-muted-foreground">
                  fLOKr exists to empower refugees and newcomers by connecting them with resources, community, and support. These terms ensure our platform remains safe, respectful, and helpful for everyone. By using fLOKr, you agree to these guidelines.
                </p>
              </div>

              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Users className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">Community Values</h2>
                </div>
                <p className="text-muted-foreground mb-3">We're building a space of dignity and mutual respect. You agree to:</p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li><strong>Treat Everyone with Respect:</strong> No discrimination, harassment, or abuse based on race, religion, nationality, gender, or any other characteristic</li>
                  <li><strong>Be Honest:</strong> Provide accurate information in your profile and listings</li>
                  <li><strong>Stay Safe:</strong> Report suspicious activity, protect your personal information, and meet in public spaces for exchanges</li>
                  <li><strong>Give Back:</strong> Help others when you can—whether by sharing resources, offering mentorship, or simply being kind</li>
                </ul>
              </div>

              <div>
                <div className="flex items-center gap-3 mb-4">
                  <Package className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">Using the Platform</h2>
                </div>
                <p className="text-muted-foreground mb-3"><strong>Reservations & Transfers:</strong></p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li>Items are available at local hubs on a first-come, first-served basis</li>
                  <li>Reservations are limited to ensure fair access—honor your commitments or cancel in time for others</li>
                  <li>Return items on time to avoid late fees and maintain community trust</li>
                  <li>Items must be returned in the condition received; damage may result in replacement fees</li>
                </ul>
                <p className="text-muted-foreground mt-3 mb-3"><strong>Content & Communication:</strong></p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li>You own the content you post, but you grant us permission to display it on the platform</li>
                  <li>No spam, scams, or misleading information</li>
                  <li>Ori (our AI assistant) learns from your interactions to provide better support—all conversations are private</li>
                </ul>
              </div>

              <div>
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="h-6 w-6 text-primary" />
                  <h2 className="text-2xl font-semibold m-0">What's Not Allowed</h2>
                </div>
                <p className="text-muted-foreground mb-3">To protect our community, these actions may result in suspension or removal:</p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li>Misusing the platform for commercial purposes without authorization</li>
                  <li>Sharing or selling items that are illegal, dangerous, or prohibited</li>
                  <li>Creating fake accounts or impersonating others</li>
                  <li>Attempting to hack, scrape, or otherwise compromise the platform</li>
                  <li>Repeated late returns or failure to honor reservations</li>
                </ul>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Your Account</h2>
                <p className="text-muted-foreground">
                  You're responsible for keeping your account secure. Don't share your password, and notify us immediately if you suspect unauthorized access. You can delete your account anytime through settings—we'll miss you, but we respect your choice.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Disclaimers & Liability</h2>
                <p className="text-muted-foreground mb-3">
                  fLOKr connects people with resources, but we don't own or verify all items. While we strive to maintain a safe platform:
                </p>
                <ul className="list-disc list-inside space-y-2 text-muted-foreground ml-4">
                  <li>We're not responsible for disputes between users or damage/loss of items during transfers</li>
                  <li>Ori provides helpful guidance, but it's not a substitute for professional advice (legal, medical, financial, etc.)</li>
                  <li>We make no guarantees about item availability or platform uptime</li>
                </ul>
                <p className="text-muted-foreground mt-3">
                  Use the platform at your own risk. We're here to help, not to replace your judgment.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Changes to These Terms</h2>
                <p className="text-muted-foreground">
                  We may update these terms to improve clarity or reflect new features. We'll notify you of significant changes, and continued use means you accept the updates.
                </p>
              </div>

              <div className="pt-6 border-t">
                <p className="text-sm text-muted-foreground">
                  <strong>Last Updated:</strong> December 2025<br />
                  Questions? Email <a href="mailto:legal@flokr.org" className="text-primary hover:underline">legal@flokr.org</a>
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
      </div>
    </div>
  )
}
