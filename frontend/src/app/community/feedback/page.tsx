'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import { motion } from 'framer-motion'
import { AppLayout } from '@/components/layout/app-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { communityService, Feedback } from '@/lib/api-services'
import { MessageSquare, AlertTriangle, ThumbsUp, Send } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export default function FeedbackPage() {
  const router = useRouter()
  const { toast } = useToast()
  const { isAuthenticated, loading: authLoading } = useSelector((state: RootState) => state.auth)
  const [feedbackHistory, setFeedbackHistory] = useState<Feedback[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  // Form states
  const [positiveFeedback, setPositiveFeedback] = useState({
    rating: 5,
    comment: ''
  })
  const [negativeFeedback, setNegativeFeedback] = useState({
    comment: ''
  })
  const [incidentReport, setIncidentReport] = useState({
    comment: '',
    itemId: '',
    reservationId: ''
  })

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchFeedbackHistory()
    }
  }, [isAuthenticated])

  const fetchFeedbackHistory = async () => {
    try {
      const data = await communityService.getFeedback()
      setFeedbackHistory(data)
    } catch (error) {
      console.error('Error fetching feedback:', error)
    }
  }

  const handlePositiveFeedback = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!positiveFeedback.comment.trim()) {
      toast({
        title: 'Missing Information',
        description: 'Please share your positive experience',
        variant: 'destructive'
      })
      return
    }

    setSubmitting(true)
    try {
      await communityService.submitFeedback({
        type: 'positive',
        rating: positiveFeedback.rating,
        comment: positiveFeedback.comment
      })
      
      toast({
        title: '💝 Thank you!',
        description: 'Your feedback brightens our community'
      })
      
      setPositiveFeedback({ rating: 5, comment: '' })
      fetchFeedbackHistory()
    } catch (error) {
      console.error('Error submitting feedback:', error)
      toast({
        title: 'Error',
        description: 'Failed to submit feedback',
        variant: 'destructive'
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleNegativeFeedback = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!negativeFeedback.comment.trim()) {
      toast({
        title: 'Missing Information',
        description: 'Please describe the issue',
        variant: 'destructive'
      })
      return
    }

    setSubmitting(true)
    try {
      await communityService.submitFeedback({
        type: 'negative',
        comment: negativeFeedback.comment
      })
      
      toast({
        title: 'Feedback Received',
        description: 'Thank you for helping us improve'
      })
      
      setNegativeFeedback({ comment: '' })
      fetchFeedbackHistory()
    } catch (error) {
      console.error('Error submitting feedback:', error)
      toast({
        title: 'Error',
        description: 'Failed to submit feedback',
        variant: 'destructive'
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleIncidentReport = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!incidentReport.comment.trim()) {
      toast({
        title: 'Missing Information',
        description: 'Please describe the incident',
        variant: 'destructive'
      })
      return
    }

    setSubmitting(true)
    try {
      await communityService.submitFeedback({
        type: 'incident',
        comment: incidentReport.comment,
        item: incidentReport.itemId || undefined,
        reservation: incidentReport.reservationId || undefined
      })
      
      toast({
        title: 'Report Submitted',
        description: 'A steward will review this shortly'
      })
      
      setIncidentReport({ comment: '', itemId: '', reservationId: '' })
      fetchFeedbackHistory()
    } catch (error) {
      console.error('Error submitting incident:', error)
      toast({
        title: 'Error',
        description: 'Failed to submit report',
        variant: 'destructive'
      })
    } finally {
      setSubmitting(false)
    }
  }

  if (authLoading || !isAuthenticated) {
    return null
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/10 text-yellow-600'
      case 'reviewed': return 'bg-blue-500/10 text-blue-600'
      case 'resolved': return 'bg-green-500/10 text-green-600'
      default: return 'bg-gray-500/10 text-gray-600'
    }
  }

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="space-y-6"
      >
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Feedback & Reports</h1>
          <p className="text-muted-foreground">
            Share your experience and help us improve
          </p>
        </div>

        {/* Feedback Forms */}
        <Card>
          <CardHeader>
            <CardTitle>Submit Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="positive">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="positive">
                  <ThumbsUp className="h-4 w-4 mr-2" />
                  Positive
                </TabsTrigger>
                <TabsTrigger value="improvement">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Improvement
                </TabsTrigger>
                <TabsTrigger value="incident">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Incident
                </TabsTrigger>
              </TabsList>

              <TabsContent value="positive">
                <form onSubmit={handlePositiveFeedback} className="space-y-4">
                  <div>
                    <Label>Rating</Label>
                    <div className="flex gap-2 mt-2">
                      {[1, 2, 3, 4, 5].map((rating) => (
                        <button
                          key={rating}
                          type="button"
                          onClick={() => setPositiveFeedback({ ...positiveFeedback, rating })}
                          className={`text-2xl transition-transform hover:scale-110 ${
                            rating <= positiveFeedback.rating ? '' : 'opacity-30'
                          }`}
                        >
                          ⭐
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="positive-comment">What made your experience great?</Label>
                    <Textarea
                      id="positive-comment"
                      placeholder="Share your positive experience..."
                      value={positiveFeedback.comment}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPositiveFeedback({ ...positiveFeedback, comment: e.target.value })}
                      rows={4}
                      className="mt-2"
                    />
                  </div>
                  <Button type="submit" disabled={submitting}>
                    <Send className="h-4 w-4 mr-2" />
                    {submitting ? 'Submitting...' : 'Submit Feedback'}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="improvement">
                <form onSubmit={handleNegativeFeedback} className="space-y-4">
                  <div>
                    <Label htmlFor="negative-comment">How can we improve?</Label>
                    <Textarea
                      id="negative-comment"
                      placeholder="Tell us what could be better..."
                      value={negativeFeedback.comment}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNegativeFeedback({ comment: e.target.value })}
                      rows={4}
                      className="mt-2"
                    />
                  </div>
                  <Button type="submit" disabled={submitting}>
                    <Send className="h-4 w-4 mr-2" />
                    {submitting ? 'Submitting...' : 'Submit Feedback'}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="incident">
                <form onSubmit={handleIncidentReport} className="space-y-4">
                  <div>
                    <Label htmlFor="incident-comment">Describe the incident</Label>
                    <Textarea
                      id="incident-comment"
                      placeholder="Please provide details about what happened..."
                      value={incidentReport.comment}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setIncidentReport({ ...incidentReport, comment: e.target.value })}
                      rows={4}
                      className="mt-2"
                    />
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <Label htmlFor="item-id">Related Item ID (optional)</Label>
                      <Input
                        id="item-id"
                        placeholder="Item UUID"
                        value={incidentReport.itemId}
                        onChange={(e) => setIncidentReport({ ...incidentReport, itemId: e.target.value })}
                        className="mt-2"
                      />
                    </div>
                    <div>
                      <Label htmlFor="reservation-id">Related Reservation ID (optional)</Label>
                      <Input
                        id="reservation-id"
                        placeholder="Reservation UUID"
                        value={incidentReport.reservationId}
                        onChange={(e) => setIncidentReport({ ...incidentReport, reservationId: e.target.value })}
                        className="mt-2"
                      />
                    </div>
                  </div>
                  <Button type="submit" variant="destructive" disabled={submitting}>
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    {submitting ? 'Submitting...' : 'Submit Report'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Feedback History */}
        {feedbackHistory.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Your Feedback History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {feedbackHistory.map((feedback) => (
                  <div key={feedback.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Badge className={getStatusColor(feedback.status)}>
                        {feedback.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm">{feedback.comment}</p>
                    {feedback.rating && (
                      <div className="mt-2">
                        {'⭐'.repeat(feedback.rating)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </AppLayout>
  )
}
