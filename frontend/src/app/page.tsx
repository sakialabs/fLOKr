'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  Bell,
  Briefcase,
  Calendar,
  Compass,
  HandHeart,
  Handshake,
  MapPin,
  Package,
  Send,
  Users,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { RootState } from '@/store'
import { Button } from '@/components/ui/button'
import { Logo } from '@/components/ui/logo'
import { OriAvatar } from '@/components/ui/ori-avatar'
import { AppHeader } from '@/components/layout/app-header'
import { Footer } from '@/components/layout/footer'

interface ValueCard {
  title: string
  body: string
  icon: LucideIcon
  accent: string
}

interface WorkStep {
  title: string
  body: string
}

interface FeatureTile {
  term: string
  body: string
  icon: LucideIcon
}

interface NaviPrompt {
  title: string
  body: string
  icon: LucideIcon
  query: string
}

interface NaviPreviewMessage {
  speaker: 'user' | 'navi'
  text: string
}

const valueCards: ValueCard[] = [
  {
    title: 'Share Resources',
    body: 'Offer what you can. Find what you need. Share essentials like clothing, household goods, and everyday items with people nearby.',
    icon: Package,
    accent: 'text-secondary bg-secondary/10 border-secondary/20',
  },
  {
    title: 'Find Leads',
    body: 'Connect with trusted helpers who can guide, translate, support, and help you find your footing.',
    icon: HandHeart,
    accent: 'text-secondary bg-secondary/10 border-secondary/20',
  },
  {
    title: 'Follow the Loop',
    body: 'Catch Signals, join Moves, and build with Circles and Crews. Stay connected to local updates, support, and action.',
    icon: Compass,
    accent: 'text-secondary bg-secondary/10 border-secondary/20',
  },
]

const workSteps: WorkStep[] = [
  {
    title: 'Share',
    body: 'Post a Signal, offer an item, ask for help, or share what is happening around your hub.',
  },
  {
    title: 'Connect',
    body: 'Join Circles, meet Leads, and find people who understand your needs and your neighbourhood.',
  },
  {
    title: 'Move',
    body: 'Build Crews, join Moves, and turn everyday support into real-world action.',
  },
]

const featureTiles: FeatureTile[] = [
  {
    term: 'Loop',
    body: 'The main feed where your community stays connected.',
    icon: Compass,
  },
  {
    term: 'Signals',
    body: 'Updates, asks, offers, alerts, and support people can act on.',
    icon: Bell,
  },
  {
    term: 'Circles',
    body: 'Recurring groups where people gather around shared needs, places, or identities.',
    icon: Users,
  },
  {
    term: 'Crews',
    body: 'Action teams that organize help, tasks, Moves, and local support.',
    icon: Handshake,
  },
  {
    term: 'Moves',
    body: 'Workshops, drives, meetups, and actions people can join.',
    icon: Calendar,
  },
  {
    term: 'Shifts',
    body: 'Work support for job leads, wage notes, workplace red flags, and rights.',
    icon: Briefcase,
  },
  {
    term: 'Leads',
    body: 'Trusted helpers who guide, support, and coordinate with care.',
    icon: HandHeart,
  },
  {
    term: 'Hubs',
    body: 'Local places where items, support, and community activity come together.',
    icon: MapPin,
  },
]

const naviPrompts: NaviPrompt[] = [
  {
    title: 'Find resources',
    body: 'Ask what items, hubs, or support are nearby.',
    icon: Package,
    query: 'What resources, hubs, or everyday items are available near me?',
  },
  {
    title: 'Join a Circle',
    body: 'Find people gathering around shared needs.',
    icon: Users,
    query: 'Can you help me find a Circle with people who share my needs or language?',
  },
  {
    title: 'Plan a Move',
    body: 'Turn a need into a workshop, drive, or meetup.',
    icon: Calendar,
    query: 'Help me plan a Move for a workshop, drive, or meetup.',
  },
  {
    title: 'Ask about Shifts',
    body: 'Get pointed toward work support and rights help.',
    icon: Briefcase,
    query: 'Where should I start if I need work support, wage help, or rights guidance?',
  },
]

const naviPreviewMessages: NaviPreviewMessage[] = [
  {
    speaker: 'user',
    text: 'I need winter basics, translation, and a way to meet people nearby.',
  },
  {
    speaker: 'navi',
    text: 'Start with the east hub for coats and kitchen items. I can also help you join the newcomer Circle.',
  },
  {
    speaker: 'user',
    text: 'Could we turn this into a pickup day for other families too?',
  },
  {
    speaker: 'navi',
    text: 'Yes. Draft a Signal, invite a Lead, and shape it as a Move. If rights questions come up, I will point you to Shifts.',
  },
]

const naviHelperChips = ['Resources', 'Translation', 'Leads', 'Shifts']

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.09,
    },
  },
}

const itemVariants = {
  hidden: { y: 12 },
  visible: {
    y: 0,
    transition: { duration: 0.5 },
  },
}

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
    return null
  }

  if (isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <AppHeader />

      <main className="flex-1 overflow-x-hidden">
        <section className="relative border-b border-border/70">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,hsl(var(--primary)/0.18),transparent_34%),linear-gradient(180deg,hsl(var(--background)),hsl(var(--muted)/0.28))]" />
          <div className="relative container mx-auto px-4 py-16 sm:py-20 lg:py-24">
            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="mx-auto flex w-full max-w-5xl flex-col items-center text-center"
            >
              <motion.div variants={itemVariants} className="relative mb-8">
                <div className="relative flex h-28 w-28 items-center justify-center rounded-full border border-primary/30 bg-background/80 p-2 shadow-2xl shadow-primary/10 backdrop-blur md:h-32 md:w-32">
                  <Logo size={112} animate />
                </div>
              </motion.div>

              <motion.h1
                variants={itemVariants}
                className="w-full max-w-[22rem] px-1 text-3xl font-bold leading-tight sm:max-w-4xl sm:text-5xl lg:text-6xl"
              >
                <span className="block sm:inline">Share goods.</span>{' '}
                <span className="block sm:inline">Find leads.</span>{' '}
                <span className="block sm:inline">Join crews.</span>{' '}
                <span className="block sm:inline">Make moves.</span>
              </motion.h1>

              <motion.p
                variants={itemVariants}
                className="mt-6 w-full max-w-[22rem] break-words px-1 text-base leading-7 text-muted-foreground sm:max-w-3xl sm:text-xl sm:leading-8"
              >
                fLOKr helps neighbors share everyday items, ask for help, and coordinate local support from one place.
                The Loop shows what people need, what people can offer, and what is happening nearby.
              </motion.p>

              <motion.div
                variants={itemVariants}
                className="mt-8 flex w-full max-w-[22rem] flex-col items-center justify-center gap-3 sm:w-auto sm:max-w-none sm:flex-row"
              >
                <Button asChild size="lg" className="w-full sm:w-auto">
                  <Link href="/register">
                    Get Started
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="w-full border-primary/25 bg-background/70 hover:bg-primary/10 sm:w-auto">
                  <Link href="/loop">Open the Loop</Link>
                </Button>
              </motion.div>
            </motion.div>

            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
              className="mx-auto mt-12 grid max-w-6xl min-w-0 gap-4 md:grid-cols-3"
            >
              {valueCards.map((card) => {
                const Icon = card.icon

                return (
                  <motion.article
                    key={card.title}
                    variants={itemVariants}
                    whileHover={{ y: -4 }}
                    className="group min-w-0 rounded-lg border border-border bg-card p-6 shadow-sm transition-colors hover:border-secondary/45 hover:bg-card/90 hover:shadow-secondary/10"
                  >
                    <div className={`mb-5 flex h-11 w-11 items-center justify-center rounded-lg border ${card.accent}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <h2 className="text-xl font-semibold">{card.title}</h2>
                    <p className="mt-3 break-words leading-7 text-muted-foreground">{card.body}</p>
                  </motion.article>
                )
              })}
            </motion.div>
          </div>
        </section>

        <section className="border-y border-border/70 bg-muted/25 py-16 sm:py-20">
          <div className="container mx-auto px-4">
            <div className="mx-auto max-w-3xl text-center">
              <h2 className="text-3xl font-bold sm:text-4xl">Ask, offer, connect, and act.</h2>
              <p className="mt-4 text-lg leading-8 text-muted-foreground">
                Post what you need or can share, find the right people, and coordinate the next step with your local hub.
              </p>
            </div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              variants={containerVariants}
              className="mt-10 grid gap-4 md:grid-cols-3"
            >
              {workSteps.map((step, index) => (
                <motion.article
                  key={step.title}
                  variants={itemVariants}
                  className="relative rounded-lg border border-border bg-background p-6"
                >
                  <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
                    {index + 1}
                  </div>
                  <h3 className="text-xl font-semibold">{step.title}</h3>
                  <p className="mt-3 leading-7 text-muted-foreground">{step.body}</p>
                </motion.article>
              ))}
            </motion.div>
          </div>
        </section>

        <section className="bg-background py-16 sm:py-20">
          <div className="container mx-auto px-4">
            <div className="mx-auto max-w-3xl text-center">
              <h2 className="text-3xl font-bold sm:text-4xl">Know what people need, what you can offer, and who can help.</h2>
              <p className="mt-4 text-lg leading-8 text-muted-foreground">
                The Loop is the shared community board. Signals are posts for requests, offers, updates, and alerts.
                Leads are trusted helpers who can guide people toward the next step.
              </p>
            </div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              variants={containerVariants}
              className="mt-10 grid auto-rows-fr gap-4 sm:grid-cols-2 lg:grid-cols-4"
            >
              {featureTiles.map((feature) => {
                const Icon = feature.icon

                return (
                  <motion.article
                    key={feature.term}
                    variants={itemVariants}
                    className="flex h-full flex-col rounded-lg border border-border bg-card p-5 transition-colors hover:border-secondary/40 hover:bg-muted/20"
                  >
                    <div className="mb-4 flex items-center gap-3">
                      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary/10 text-secondary">
                        <Icon className="h-4 w-4" />
                      </span>
                      <h3 className="text-lg font-semibold">{feature.term}</h3>
                    </div>
                    <p className="text-sm leading-6 text-muted-foreground">{feature.body}</p>
                  </motion.article>
                )
              })}
            </motion.div>
          </div>
        </section>

        <section className="border-y border-border/70 bg-muted/25 py-16 sm:py-20">
          <div className="container mx-auto px-4">
            <div className="mx-auto max-w-3xl text-center">
              <OriAvatar size="lg" animated className="mx-auto mb-5" />
              <h2 className="text-3xl font-bold leading-tight sm:text-4xl">
                Ask Navi for the next useful step.
              </h2>
              <p className="mt-4 text-lg leading-8 text-muted-foreground">
                Ask Navi about resources, hubs, support, Moves, translation, and work questions. Navi can guide you to essentials, Leads, Circles, and Shifts, with Lexi helping when rights or legal questions come up.
              </p>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5 }}
              className="mx-auto mt-10 flex max-w-6xl flex-col gap-6 rounded-lg border border-primary/20 bg-card p-5 shadow-xl shadow-primary/5 sm:p-7"
            >
              <div className="grid items-stretch gap-6 lg:grid-cols-[0.9fr_1.1fr]">
                <div className="min-w-0 rounded-lg border border-border/70 bg-background/55 p-4 shadow-sm">
                  <div className="space-y-3">
                    {naviPreviewMessages.map((message, index) => (
                      <motion.div
                        key={`${message.speaker}-${message.text}`}
                        initial={{ opacity: 0, y: 8 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: '-80px' }}
                        transition={{ delay: index * 0.18, duration: 0.35 }}
                        className={`flex items-end gap-2 ${
                          message.speaker === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.speaker === 'navi' && <OriAvatar size="sm" />}
                        <p
                          className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                            message.speaker === 'user'
                              ? 'rounded-br-md bg-primary text-primary-foreground'
                              : 'rounded-bl-md border border-border/70 bg-card text-card-foreground'
                          }`}
                        >
                          {message.text}
                        </p>
                        {message.speaker === 'user' && (
                          <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full border border-secondary/20 bg-secondary/10 shadow-sm">
                            <Image
                              src="/avatars/avatar1.png"
                              alt=""
                              width={32}
                              height={32}
                              className="h-full w-full object-cover"
                            />
                          </span>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>

                <div className="flex min-w-0 flex-col gap-4">
                  <div className="grid min-w-0 gap-2 sm:grid-cols-2">
                    {naviPrompts.map((prompt) => {
                      const Icon = prompt.icon

                      return (
                        <Link
                          key={prompt.title}
                          href={`/navi?prompt=${encodeURIComponent(prompt.query)}`}
                          aria-label={`${prompt.title}: ${prompt.body}`}
                          className="group flex min-h-24 items-start gap-3 rounded-md border border-border/60 bg-background/45 p-3 transition-colors hover:border-secondary/35 hover:bg-background/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary/45 focus-visible:ring-offset-2 focus-visible:ring-offset-card"
                        >
                          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-secondary/10 text-secondary">
                            <Icon className="h-4 w-4" />
                          </span>
                          <span className="min-w-0">
                            <span className="block font-semibold">{prompt.title}</span>
                            <span className="mt-1 block text-sm leading-6 text-muted-foreground">{prompt.body}</span>
                          </span>
                        </Link>
                      )
                    })}
                  </div>

                  <div className="rounded-lg border border-secondary/20 bg-background/50 p-4">
                    <p className="text-sm leading-6 text-muted-foreground">
                      Navi ties together practical support, local people, and the next step when a question crosses
                      more than one part of fLOKr.
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {naviHelperChips.map((chip) => (
                        <span
                          key={chip}
                          className="rounded-full border border-secondary/20 bg-secondary/10 px-3 py-1 text-xs font-semibold text-secondary"
                        >
                          {chip}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="mt-auto rounded-lg border border-border/70 bg-background/55 p-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-sm leading-6 text-muted-foreground">
                        Start with a prompt or ask Navi in your own words.
                      </p>
                      <Button asChild size="lg" className="w-full sm:w-auto">
                        <Link href="/navi">
                          Chat with Navi
                          <Send className="h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="bg-background py-16 sm:py-20">
          <div className="container mx-auto px-4">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-80px' }}
              variants={containerVariants}
              className="mx-auto max-w-4xl text-center"
            >
              <motion.h2 variants={itemVariants} className="text-3xl font-bold leading-tight sm:text-4xl">
                Find what you need. Share what you can. Move with your people.
              </motion.h2>
              <motion.p variants={itemVariants} className="mt-5 text-lg leading-8 text-muted-foreground">
                Join fLOKr to connect with local resources, trusted support, and community action in one place.
              </motion.p>
              <motion.div variants={itemVariants} className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
                <Button asChild size="lg" className="w-full sm:w-auto">
                  <Link href="/register">Get Started</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                  <Link href="/loop">Open the Loop</Link>
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
