import { NextResponse } from 'next/server'

export function middleware() {
  // Note: Middleware runs on the server and can't access localStorage
  // We'll handle auth checks on the client side instead

  // Just allow all routes - auth will be handled client-side
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
