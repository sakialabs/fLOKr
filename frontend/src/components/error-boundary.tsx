'use client'

import { Component, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    
    // Check if it's a ChunkLoadError
    if (error.name === 'ChunkLoadError' || error.message.includes('Loading chunk')) {
      console.log('ChunkLoadError detected - attempting reload')
    }
  }

  handleReload = () => {
    window.location.reload()
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      const isChunkError = 
        this.state.error?.name === 'ChunkLoadError' || 
        this.state.error?.message.includes('Loading chunk')

      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
          <div className="w-full max-w-md space-y-4">
            <Alert variant="destructive">
              <AlertDescription>
                {isChunkError ? (
                  <>
                    <p className="font-semibold mb-2">Failed to load application resources</p>
                    <p className="text-sm mb-4">
                      This usually happens when the application was updated. Please reload the page.
                    </p>
                  </>
                ) : (
                  <>
                    <p className="font-semibold mb-2">Something went wrong</p>
                    <p className="text-sm mb-4">
                      {this.state.error?.message || 'An unexpected error occurred'}
                    </p>
                  </>
                )}
              </AlertDescription>
            </Alert>
            
            <div className="flex gap-2">
              <Button onClick={this.handleReload} className="flex-1">
                Reload Page
              </Button>
              {!isChunkError && (
                <Button onClick={this.handleReset} variant="outline" className="flex-1">
                  Try Again
                </Button>
              )}
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
