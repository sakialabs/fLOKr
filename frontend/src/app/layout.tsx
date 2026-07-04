import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ClientLayout } from '@/components/client-layout'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'fLOKr | Share, Connect, Move',
  description: 'Supporting newcomers through shared resources, Loop Signals, local Moves, and trusted Leads',
  icons: {
    icon: { url: '/goose.png', type: 'image/png' },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
  )
}
