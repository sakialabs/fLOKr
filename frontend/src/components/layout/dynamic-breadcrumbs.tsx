'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Fragment } from 'react'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'

const routeNames: Record<string, string> = {
  home: 'Home',
  items: 'Items',
  reservations: 'Reservations',
  hubs: 'Hubs',
  community: 'Community',
  profile: 'Profile',
  settings: 'Settings',
  onboarding: 'Onboarding',
  dashboard: 'Dashboard',
  steward: 'Steward',
  admin: 'Admin',
  ori: 'Ori AI',
}

interface DynamicBreadcrumbsProps {
  override?: string
}

export function DynamicBreadcrumbs({ override }: DynamicBreadcrumbsProps = {}) {
  const pathname = usePathname()
  
  // Don't show breadcrumbs on root paths
  if (pathname === '/' || pathname === '/login' || pathname === '/register') {
    return null
  }

  const paths = pathname.split('/').filter(Boolean)
  
  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link href="/home" className="flex items-center gap-1">
              <span>Dashboard</span>
            </Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        
        {paths.map((path, index) => {
          const href = `/${paths.slice(0, index + 1).join('/')}`
          const isLast = index === paths.length - 1
          // Use override for the last breadcrumb if provided, otherwise use route name
          const name = (isLast && override) ? override : (routeNames[path] || path.charAt(0).toUpperCase() + path.slice(1))
          
          return (
            <Fragment key={href}>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                {isLast ? (
                  <BreadcrumbPage>{name}</BreadcrumbPage>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link href={href}>{name}</Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </Fragment>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}
