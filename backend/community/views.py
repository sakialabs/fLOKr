"""
Community API Views
Provides endpoints for badges, feedback, mentorship, and community data
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from .models import Badge, UserBadge, Feedback, MentorshipConnection, Message
from .serializers import (
    BadgeSerializer,
    UserBadgeSerializer,
    FeedbackSerializer,
    MentorshipConnectionSerializer,
    MentorshipConnectionListSerializer,
    MessageSerializer
)
from users.models import User
from users.serializers import UserProfileSerializer


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for badges - read only
    """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['category', 'name']


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user badge awards
    Lists recently awarded badges for community feed
    """
    queryset = UserBadge.objects.select_related('user', 'badge').all()
    serializer_class = UserBadgeSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-awarded_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user if specified
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter recent awards (last 30 days) for community feed
        if self.request.query_params.get('recent') == 'true':
            thirty_days_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(awarded_at__gte=thirty_days_ago)
        
        return queryset


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for feedback and incident reports
    """
    queryset = Feedback.objects.select_related('user', 'item', 'reservation').all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Users can see their own feedback and positive community feedback
        if not self.request.user.role in ['steward', 'admin']:
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(type='positive', status='resolved')
            )
        
        # Filter by type
        feedback_type = self.request.query_params.get('type')
        if feedback_type:
            queryset = queryset.filter(type=feedback_type)
        
        # Filter positive feedback for community feed
        if self.request.query_params.get('positive_only') == 'true':
            queryset = queryset.filter(type='positive', rating__gte=4)
        
        return queryset
    
    def perform_create(self, serializer):
        feedback = serializer.save(user=self.request.user)
        
        # Process incident reports
        if feedback.type == 'incident':
            from .incident_service import IncidentService
            IncidentService.process_incident_report(feedback)
        
        # Award reputation for positive feedback (about someone else)
        elif feedback.type == 'positive' and feedback.rating and feedback.rating >= 4:
            # If feedback is about a reservation, award points to the borrower
            if feedback.reservation and feedback.reservation.user:
                from .reputation_service import ReputationService
                ReputationService.award_points(
                    feedback.reservation.user,
                    'positive_feedback',
                    reason=f'Received {feedback.rating}-star feedback'
                )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resolve(self, request, pk=None):
        """
        Resolve feedback (stewards/admins only).
        Requires 'resolution_notes' in request data.
        """
        from .incident_service import IncidentService
        from users.permissions import IsStewardOrAdmin
        
        # Check permissions
        if not (request.user.role in ['steward', 'admin']):
            return Response(
                {'error': 'Only stewards and admins can resolve feedback'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        if not resolution_notes:
            return Response(
                {'error': 'resolution_notes is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        IncidentService.resolve_feedback(feedback, request.user, resolution_notes)
        
        serializer = self.get_serializer(feedback)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_incidents(self, request):
        """
        Get pending incident reports (stewards/admins only).
        Filtered by hub for stewards.
        """
        from .incident_service import IncidentService
        
        if not (request.user.role in ['steward', 'admin']):
            return Response(
                {'error': 'Only stewards and admins can view incident reports'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter by hub for stewards
        hub = None
        if request.user.role == 'steward':
            hub = request.user.assigned_hub
        
        incidents = IncidentService.get_pending_incidents(hub=hub)
        serializer = self.get_serializer(incidents, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def feedback_stats(self, request):
        """
        Get feedback statistics (stewards/admins only).
        Filtered by hub for stewards.
        """
        from .incident_service import IncidentService
        
        if not (request.user.role in ['steward', 'admin']):
            return Response(
                {'error': 'Only stewards and admins can view feedback stats'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        hub = None
        if request.user.role == 'steward':
            hub = request.user.assigned_hub
        
        stats = IncidentService.get_feedback_stats(hub=hub)
        
        return Response(stats)


class MentorshipConnectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for mentorship connections
    """
    queryset = MentorshipConnection.objects.select_related('mentor', 'mentee').all()
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MentorshipConnectionListSerializer
        return MentorshipConnectionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Users see connections where they're involved
        if user.role not in ['steward', 'admin']:
            queryset = queryset.filter(Q(mentor=user) | Q(mentee=user))
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Active mentorships for community feed
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(status='active')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a mentorship connection with auto-translation"""
        from .message_service import MessageService
        
        connection = self.get_object()
        
        # Verify user is part of this connection
        if request.user not in [connection.mentor, connection.mentee]:
            return Response(
                {'error': 'You are not part of this mentorship connection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        content = request.data.get('content')
        if not content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create message with auto-translation
            message = MessageService.create_message(
                connection=connection,
                sender=request.user,
                content=content
            )
            
            # Return message with translation info
            user_lang = request.user.preferred_language or 'en'
            response_data = {
                'id': str(message.id),
                'content': content,
                'translated_content': message.translated_content,
                'created_at': message.created_at.isoformat(),
                'sender_id': str(request.user.id),
                'connection_id': str(connection.id)
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_messages_read(self, request, pk=None):
        """Mark all messages in a connection as read"""
        from .message_service import MessageService
        
        connection = self.get_object()
        
        # Verify user is part of this connection
        if request.user not in [connection.mentor, connection.mentee]:
            return Response(
                {'error': 'You are not part of this mentorship connection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mark messages as read
        MessageService.mark_messages_read(connection, request.user)
        
        return Response({'status': 'messages marked as read'})
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get conversation history with auto-translated content.
        Messages are returned in the user's preferred language.
        """
        from .message_service import MessageService
        
        connection = self.get_object()
        
        # Verify user is part of this connection
        if request.user not in [connection.mentor, connection.mentee]:
            return Response(
                {'error': 'You are not part of this mentorship connection'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get message limit from query params
        limit = int(request.query_params.get('limit', 50))
        
        # Get conversation history with translations
        messages = MessageService.get_conversation_history(
            connection=connection,
            requesting_user=request.user,
            limit=limit
        )
        
        return Response({
            'connection_id': str(connection.id),
            'message_count': len(messages),
            'messages': messages
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages for current user"""
        from .message_service import MessageService
        
        unread = MessageService.get_unread_count(request.user)
        
        return Response({
            'unread_count': unread
        })
    
    @action(detail=False, methods=['get'])
    def find_matches(self, request):
        """
        Find potential mentors for the current user.
        Returns list of mentors with match scores and reasons.
        """
        from .mentorship_service import MentorshipMatchingService
        
        # Get match limit from query params
        limit = int(request.query_params.get('limit', 10))
        
        # Find potential mentors
        matches = MentorshipMatchingService.find_potential_mentors(
            request.user,
            max_results=limit
        )
        
        # Format response
        response_data = []
        for match in matches:
            mentor = match['mentor']
            response_data.append({
                'mentor_id': str(mentor.id),
                'mentor_name': mentor.get_full_name(),
                'mentor_email': mentor.email,
                'hub': mentor.assigned_hub.name if mentor.assigned_hub else None,
                'language': mentor.preferred_language,
                'reputation': mentor.reputation_score,
                'match_score': match['score'],
                'match_reasons': match['reasons']
            })
        
        return Response({
            'matches': response_data,
            'count': len(response_data)
        })
    
    @action(detail=False, methods=['get'])
    def find_mentors(self, request):
        """
        Find mentors by language or interests.
        Simple search endpoint without scoring.
        """
        languages = request.query_params.getlist('languages')
        interests = request.query_params.getlist('interests')
        
        # Find mentors (users with is_mentor=True)
        mentors = User.objects.filter(is_mentor=True)
        
        # Filter by languages if specified
        if languages:
            mentors = mentors.filter(
                Q(preferred_language__in=languages) |
                Q(languages_spoken__overlap=languages)
            )
        
        # Filter by interests (in preferences JSON field)
        if interests:
            mentors = mentors.filter(
                preferences__skill_interests__overlap=interests
            )
        
        # Use UserProfileSerializer for consistent format
        from users.serializers import UserPublicProfileSerializer
        serializer = UserPublicProfileSerializer(mentors[:20], many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def request_mentor(self, request):
        """
        Request a mentorship connection with a specific mentor.
        Requires 'mentor_id' in request data.
        """
        from .mentorship_service import MentorshipMatchingService
        
        mentor_id = request.data.get('mentor_id')
        if not mentor_id:
            return Response(
                {'error': 'mentor_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            connection = MentorshipMatchingService.create_connection(
                mentor_id=mentor_id,
                mentee_id=request.user.id
            )
            
            serializer = self.get_serializer(connection)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response(
                {'error': 'Mentor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        Accept a mentorship connection request.
        Only the mentor can accept.
        """
        from .mentorship_service import MentorshipMatchingService
        
        try:
            connection = MentorshipMatchingService.accept_connection(
                connection_id=pk,
                mentor_user=request.user
            )
            
            serializer = self.get_serializer(connection)
            return Response(serializer.data)
        
        except MentorshipConnection.DoesNotExist:
            return Response(
                {'error': 'Connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """
        Decline a mentorship connection request.
        Only the mentor can decline.
        """
        from .mentorship_service import MentorshipMatchingService
        
        try:
            connection = MentorshipMatchingService.decline_connection(
                connection_id=pk,
                mentor_user=request.user
            )
            
            serializer = self.get_serializer(connection)
            return Response(serializer.data)
        
        except MentorshipConnection.DoesNotExist:
            return Response(
                {'error': 'Connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CommunityDataViewSet(viewsets.ViewSet):
    """
    ViewSet for aggregated community data
    Provides endpoints for newcomers, recent activity, etc.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def newcomers(self, request):
        """Get recent newcomers who joined in the last 7 days"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        newcomers = User.objects.filter(
            role='newcomer',
            date_joined__gte=seven_days_ago
        ).select_related('assigned_hub').order_by('-date_joined')
        
        # Add days since joined
        data = []
        for user in newcomers:
            days_ago = (timezone.now() - user.date_joined).days
            data.append({
                'id': str(user.id),
                'name': user.get_full_name(),
                'joined_days_ago': days_ago,
                'hub': user.assigned_hub.name if user.assigned_hub else 'No hub assigned',
                'language': user.preferred_language
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def recent_badges(self, request):
        """Get recently awarded badges for community feed"""
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_badges = UserBadge.objects.filter(
            awarded_at__gte=thirty_days_ago
        ).select_related('user', 'badge').order_by('-awarded_at')[:10]
        
        serializer = UserBadgeSerializer(recent_badges, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def success_stories(self, request):
        """Get positive feedback/success stories for community feed"""
        success_stories = Feedback.objects.filter(
            type='positive',
            rating__gte=4,
            status='resolved'
        ).select_related('user', 'item').order_by('-created_at')[:10]
        
        serializer = FeedbackSerializer(success_stories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mentorship_opportunities(self, request):
        """Get available mentorship opportunities"""
        # Active mentorships
        active_mentorships = MentorshipConnection.objects.filter(
            status='active'
        ).select_related('mentor', 'mentee').order_by('-start_date')[:5]
        
        # Pending requests
        pending_requests = MentorshipConnection.objects.filter(
            status='requested'
        ).select_related('mentor', 'mentee').count()
        
        serializer = MentorshipConnectionListSerializer(active_mentorships, many=True)
        return Response({
            'active_mentorships': serializer.data,
            'pending_requests': pending_requests
        })


class ReputationViewSet(viewsets.ViewSet):
    """
    ViewSet for dignity-first reputation system.
    Private scores + optional community highlights (no public rankings).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_reputation(self, request):
        """
        Get current user's personal reputation summary.
        Private view - only shows their own score.
        """
        from .reputation_service import ReputationService
        
        summary = ReputationService.get_personal_reputation_summary(request.user)
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def community_highlights(self, request):
        """
        Get optional community highlights - celebrates contributors without ranking.
        This is NOT a leaderboard - no numbers, no rankings, just gentle celebration.
        """
        from .reputation_service import ReputationService
        
        limit = int(request.query_params.get('limit', 10))
        highlights = ReputationService.get_community_highlights(limit=limit)
        
        return Response({
            'highlights': highlights,
            'note': 'These are people who have been helping lately. No rankings, just appreciation.'
        })
