from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema
from .models import Reservation
from .serializers import (
    ReservationSerializer,
    ReservationListSerializer,
    ReservationCreateSerializer
)
from users.permissions import IsStewardOrAdmin


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet for Reservation management."""
    queryset = Reservation.objects.select_related('user', 'item', 'hub').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        elif self.action == 'create':
            return ReservationCreateSerializer
        return ReservationSerializer
    
    def get_queryset(self):
        """Filter reservations based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all
        if user.role == 'admin':
            return queryset
        
        # Stewards see reservations for their hubs
        if user.role == 'steward':
            return queryset.filter(hub__stewards=user)
        
        # Regular users see only their own reservations
        return queryset.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        """Mark reservation as picked up (stewards only)."""
        reservation = self.get_object()
        
        if reservation.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed reservations can be picked up'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'picked_up'
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def return_item(self, request, pk=None):
        """Mark item as returned (stewards only)."""
        reservation = self.get_object()
        
        if reservation.status != 'picked_up':
            return Response(
                {'error': 'Only picked up items can be returned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'returned'
        reservation.actual_return_date = timezone.now().date()
        reservation.save()
        
        # Return quantity to inventory
        item = reservation.item
        item.quantity_available += reservation.quantity
        item.save()
        
        # Check if return is late
        if reservation.actual_return_date > reservation.expected_return_date:
            user = reservation.user
            user.late_return_count += 1
            
            # Restrict borrowing after 3 late returns
            if user.late_return_count >= 3:
                user.borrowing_restricted_until = timezone.now() + timedelta(days=30)
            
            user.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel reservation."""
        reservation = self.get_object()
        
        # Only user or steward can cancel
        if reservation.user != request.user and request.user.role not in ['steward', 'admin']:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if reservation.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Only pending or confirmed reservations can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        # Return quantity to inventory
        item = reservation.item
        item.quantity_available += reservation.quantity
        item.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def request_extension(self, request, pk=None):
        """Request extension for reservation."""
        reservation = self.get_object()
        
        if reservation.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if reservation.status != 'picked_up':
            return Response(
                {'error': 'Only picked up items can request extension'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.extension_requested = True
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve_extension(self, request, pk=None):
        """Approve extension request (stewards only)."""
        reservation = self.get_object()
        
        if not reservation.extension_requested:
            return Response(
                {'error': 'No extension request found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_return_date = request.data.get('new_return_date')
        if not new_return_date:
            return Response(
                {'error': 'new_return_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.extension_approved = True
        reservation.expected_return_date = new_return_date
        reservation.save()
        
        serializer = self.get_serializer(reservation)
        return Response(serializer.data)
