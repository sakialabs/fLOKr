from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
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
        user = reservation.user
        is_late = reservation.actual_return_date > reservation.expected_return_date
        
        if is_late:
            # Use late return service to handle penalties
            from .late_return_service import LateReturnService
            LateReturnService.apply_late_return_penalty(user, reservation)
        else:
            # Award reputation for on-time return
            from community.reputation_service import ReputationService
            ReputationService.award_points(user, 'on_time_return')
            
            # Check for consecutive on-time returns
            recent_returns = Reservation.objects.filter(
                user=user,
                status='returned',
                actual_return_date__lte=models.F('expected_return_date')
            ).order_by('-actual_return_date')[:5]
            
            if recent_returns.count() >= 5:
                ReputationService.award_points(user, 'consecutive_returns')
        
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
    @action(detail=False, methods=['get'])
    def restriction_status(self, request):
        """Get current user's borrowing restriction status."""
        from .late_return_service import LateReturnService
        
        status_info = LateReturnService.get_restriction_status(request.user)
        return Response(status_info)
    
    @action(detail=False, methods=['post'], permission_classes=[IsStewardOrAdmin])
    def lift_restriction(self, request):
        """
        Lift a user's borrowing restriction (stewards/admins only).
        Requires 'user_id' and optional 'reason' in request data.
        """
        from .late_return_service import LateReturnService
        from django.contrib.auth import get_user_model
        
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', 'Lifted by steward')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            User = get_user_model()
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        success = LateReturnService.lift_restriction(user, lifted_by=request.user, reason=reason)
        
        if success:
            return Response({
                'message': f'Borrowing restriction lifted for {user.get_full_name()}',
                'user_id': str(user.id),
                'reason': reason
            })
        else:
            return Response(
                {'error': 'User does not have an active restriction'},
                status=status.HTTP_400_BAD_REQUEST
            )