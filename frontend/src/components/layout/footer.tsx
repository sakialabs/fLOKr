'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Heart } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mt-auto">
      <div className="container mx-auto px-4 py-3">
        <div className="flex flex-col gap-1.5">
          {/* Row 1: Copyright (left) and Links (right) */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-2">
            {/* Copyright */}
            <motion.span
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-muted-foreground"
            >
              © {currentYear} fLOKr. All rights reserved.
            </motion.span>

            {/* Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="flex flex-wrap items-center justify-center gap-4 text-sm"
            >
              <Link
                href="/about"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                About
              </Link>
              <span className="text-muted-foreground/50">•</span>
              <Link
                href="/contact"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                Contact
              </Link>
              <span className="text-muted-foreground/50">•</span>
              <Link
                href="/privacy"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                Privacy
              </Link>
              <span className="text-muted-foreground/50">•</span>
              <Link
                href="/terms"
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                Terms
              </Link>
            </motion.div>
          </div>

          {/* Row 2: Message (centered) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-center justify-center"
          >
            <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
              Built with <Heart className="h-3.5 w-3.5 text-red-500 fill-red-500" /> for community, dignity, and respect
            </span>
          </motion.div>
        </div>
      </div>
    </footer>
  )
}
