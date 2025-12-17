from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserPublicProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    OnboardingPreferencesSerializer,
)


class RegisterView(APIView):
    """User registration endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Register a new user account."""
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Authenticate user and return JWT tokens."""
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user, context={'request': request}).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={'refresh': 'string'},
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid token"),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Blacklist the refresh token to logout user."""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    """User profile endpoint."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: UserProfileSerializer,
        },
        tags=['User Profile']
    )
    def get(self, request):
        """Get current user profile."""
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['User Profile']
    )
    def put(self, request):
        """Update current user profile."""
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePictureUploadView(APIView):
    """Profile picture upload endpoint."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'profile_picture': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Profile picture uploaded successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['User Profile']
    )
    def post(self, request):
        """Upload a profile picture."""
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No profile picture provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile_picture = request.FILES['profile_picture']
        
        # Validate file size (max 5MB)
        if profile_picture.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File size must be less than 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if profile_picture.content_type not in allowed_types:
            return Response(
                {'error': 'Only JPEG, PNG, and WebP images are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the profile picture
        request.user.profile_picture = profile_picture
        request.user.save()
        
        # Build absolute URL
        profile_picture_url = None
        if request.user.profile_picture:
            profile_picture_url = request.build_absolute_uri(request.user.profile_picture.url)
        
        return Response({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': profile_picture_url
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Profile picture deleted successfully"),
        },
        tags=['User Profile']
    )
    def delete(self, request):
        """Delete the profile picture."""
        if request.user.profile_picture:
            request.user.profile_picture.delete()
            request.user.save()
            return Response(
                {'message': 'Profile picture deleted successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'No profile picture to delete'},
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetRequestView(APIView):
    """Password reset request endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiResponse(description="Password reset email sent"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # In production, this would be your frontend URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            # Send email (in development, this will print to console)
            send_mail(
                subject='Password Reset Request - fLOKr',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response(
                {'message': 'Password reset email sent'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Password reset confirmation endpoint."""
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            400: OpenApiResponse(description="Invalid token or validation error"),
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Reset password with token."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                uid = request.data.get('uid')
                token = serializer.validated_data['token']
                password = serializer.validated_data['password']
                
                # Decode user ID
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                
                # Verify token
                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    
                    return Response(
                        {'message': 'Password reset successful'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'Invalid or expired token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Password change endpoint for authenticated users."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['User Profile']
    )
    def post(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'message': 'Password changed successfully. Please log in again with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OnboardingView(APIView):
    """User onboarding preferences endpoint."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=OnboardingPreferencesSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        tags=['Onboarding']
    )
    def post(self, request):
        """Save onboarding preferences and update user profile."""
        serializer = OnboardingPreferencesSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update user with preferences
            user = serializer.update_user_preferences(request.user, serializer.validated_data)
            
            # Return updated user profile
            profile_serializer = UserProfileSerializer(user)
            
            return Response({
                'message': 'Onboarding completed successfully',
                'user': profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        responses={
            200: OnboardingPreferencesSerializer,
        },
        tags=['Onboarding']
    )
    def get(self, request):
        """Get current onboarding preferences."""
        user = request.user
        
        # Extract preferences from user model
        preferences = user.preferences or {}
        preferences['preferred_language'] = user.preferred_language
        preferences['address'] = user.address
        preferences['arrival_date'] = user.arrival_date
        
        serializer = OnboardingPreferencesSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardView(APIView):
    """Personal dashboard data endpoint."""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Dashboard data"),
        },
        tags=['Dashboard']
    )
    def get(self, request):
        """Get personalized dashboard data for My Home page."""
        from reservations.models import Reservation
        from inventory.models import InventoryItem
        from datetime import date, timedelta
        
        user = request.user
        today = date.today()
        week_from_now = today + timedelta(days=7)
        
        # Active reservations (picked up items)
        active_reservations = Reservation.objects.filter(
            user=user,
            status='picked_up'
        ).select_related('item', 'hub').order_by('expected_return_date')
        
        # Upcoming returns (due within next 7 days)
        upcoming_returns = active_reservations.filter(
            expected_return_date__lte=week_from_now
        )
        
        # Overdue items
        overdue_items = active_reservations.filter(
            expected_return_date__lt=today
        )
        
        # Pending reservations (awaiting pickup)
        pending_reservations = Reservation.objects.filter(
            user=user,
            status__in=['pending', 'confirmed']
        ).select_related('item', 'hub').order_by('pickup_date')
        
        # Ready for pickup
        ready_for_pickup = pending_reservations.filter(
            status='confirmed',
            pickup_date__lte=today
        )
        
        # Personal stats
        total_borrowed = Reservation.objects.filter(
            user=user,
            status__in=['returned', 'picked_up']
        ).count()
        
        on_time_returns = Reservation.objects.filter(
            user=user,
            status='returned',
            actual_return_date__lte=models.F('expected_return_date')
        ).count()
        
        # Serialize data
        from reservations.serializers import ReservationSerializer
        
        dashboard_data = {
            'summary': {
                'upcoming_returns_count': upcoming_returns.count(),
                'overdue_count': overdue_items.count(),
                'ready_for_pickup_count': ready_for_pickup.count(),
                'active_reservations_count': active_reservations.count(),
                'total_borrowed': total_borrowed,
                'on_time_returns': on_time_returns,
            },
            'active_reservations': ReservationSerializer(active_reservations[:5], many=True).data,
            'upcoming_returns': ReservationSerializer(upcoming_returns, many=True).data,
            'pending_reservations': ReservationSerializer(pending_reservations[:5], many=True).data,
            'overdue_items': ReservationSerializer(overdue_items, many=True).data,
        }
        
        return Response(dashboard_data, status=status.HTTP_200_OK)


class PublicProfileView(APIView):
    """
    Public profile viewing endpoint.
    Dignity-first profiles: bio, skills, languages, badges, contributions.
    NO private data (email, phone, address).
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: UserPublicProfileSerializer,
            404: OpenApiResponse(description="User not found"),
        },
        tags=['User Profile']
    )
    def get(self, request, user_id):
        """View any user's public profile."""
        try:
            user = User.objects.get(id=user_id)
            serializer = UserPublicProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

