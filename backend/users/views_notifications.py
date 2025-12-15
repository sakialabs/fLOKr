"""
Views for notification management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from users.models_notifications import Notification, NotificationPreference, DeviceToken
from users.serializers_notifications import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    DeviceTokenSerializer,
    DeviceTokenCreateSerializer
)
from users.notifications import notification_service


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications.
    
    Provides:
    - List user's notifications
    - Retrieve specific notification
    - Mark as read
    - Mark all as read
    - Get unread count
    """
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('recipient')
    
    @extend_schema(
        summary="Mark notification as read",
        responses={200: NotificationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        
        success = notification_service.mark_as_read(
            notification_id=str(notification.id),
            user_id=str(request.user.id)
        )
        
        if success:
            notification.refresh_from_db()
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Failed to mark as read'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @extend_schema(
        summary="Mark all notifications as read",
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all unread notifications as read."""
        count = notification_service.mark_all_as_read(
            user_id=str(request.user.id)
        )
        
        return Response({'count': count})
    
    @extend_schema(
        summary="Get unread notification count",
        responses={200: {'type': 'object', 'properties': {'count': {'type': 'integer'}}}}
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = notification_service.get_unread_count(
            user_id=str(request.user.id)
        )
        
        return Response({'count': count})
    
    @extend_schema(
        summary="List unread notifications",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get all unread notifications."""
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """
    ViewSet for notification preferences.
    
    Provides:
    - Get user's notification preferences
    - Update notification preferences
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get notification preferences",
        responses={200: NotificationPreferenceSerializer}
    )
    def list(self, request):
        """Get current user's notification preferences."""
        prefs, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(prefs)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update notification preferences",
        request=NotificationPreferenceSerializer,
        responses={200: NotificationPreferenceSerializer}
    )
    def create(self, request):
        """Update notification preferences (using POST for simplicity)."""
        prefs, created = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        
        serializer = NotificationPreferenceSerializer(
            prefs,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DeviceTokenViewSet(viewsets.ViewSet):
    """
    ViewSet for device token management.
    
    Provides:
    - Register device token
    - List user's devices
    - Unregister device token
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List user's registered devices",
        responses={200: DeviceTokenSerializer(many=True)}
    )
    def list(self, request):
        """List all registered devices for the current user."""
        devices = DeviceToken.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = DeviceTokenSerializer(devices, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Register device token",
        request=DeviceTokenCreateSerializer,
        responses={201: DeviceTokenSerializer}
    )
    def create(self, request):
        """Register a new device token for push notifications."""
        serializer = DeviceTokenCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            device = notification_service.register_device(
                user_id=str(request.user.id),
                token=serializer.validated_data['token'],
                platform=serializer.validated_data['platform'],
                device_name=serializer.validated_data.get('device_name', '')
            )
            
            response_serializer = DeviceTokenSerializer(device)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @extend_schema(
        summary="Unregister device token",
        request={'type': 'object', 'properties': {'token': {'type': 'string'}}},
        responses={200: {'type': 'object', 'properties': {'success': {'type': 'boolean'}}}}
    )
    @action(detail=False, methods=['post'])
    def unregister(self, request):
        """Unregister a device token."""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = notification_service.unregister_device(token)
        
        return Response({'success': success})
