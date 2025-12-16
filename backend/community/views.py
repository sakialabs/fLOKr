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
        serializer.save(user=self.request.user)


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
        """Send a message in a mentorship connection"""
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
        
        message = Message.objects.create(
            connection=connection,
            sender=request.user,
            content=content
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_messages_read(self, request, pk=None):
        """Mark all messages in a connection as read"""
        connection = self.get_object()
        
        # Mark messages sent by the other person as read
        Message.objects.filter(
            connection=connection
        ).exclude(sender=request.user).update(read=True)
        
        return Response({'status': 'messages marked as read'})


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

