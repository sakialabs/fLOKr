from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'phone', 'role', 'preferred_language', 'address', 'arrival_date'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Role.NEWCOMER),
            preferred_language=validated_data.get('preferred_language', 'en'),
            address=validated_data.get('address', ''),
            arrival_date=validated_data.get('arrival_date'),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate credentials and return user."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role',
            'preferred_language', 'address', 'location', 'assigned_hub',
            'arrival_date', 'preferences', 'reputation_score', 'is_mentor',
            'late_return_count', 'borrowing_restricted_until', 'created_at',
            'bio', 'skills', 'languages_spoken', 'profile_picture', 'avatar_choice'
        ]
        read_only_fields = [
            'id', 'email', 'role', 'reputation_score', 'late_return_count',
            'borrowing_restricted_until', 'created_at'
        ]
    
    def get_profile_picture(self, obj):
        """Return absolute URL for profile picture."""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """
    Public profile serializer - dignity-first profiles.
    Shows bio, skills, languages, badges, and contribution history.
    Does NOT show private info like email, phone, address.
    """
    full_name = serializers.SerializerMethodField()
    badges_earned = serializers.SerializerMethodField()
    contribution_stats = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'role', 'bio', 'skills', 'languages_spoken',
            'is_mentor', 'badges_earned', 'contribution_stats',
            'reputation_score', 'member_since', 'preferred_language', 'profile_picture'
        ]
        read_only_fields = [
            'id', 'full_name', 'role', 'badges_earned', 'contribution_stats',
            'reputation_score', 'member_since', 'profile_picture'
        ]
    
    def get_full_name(self, obj):
        """Return user's full name."""
        return obj.get_full_name()
    
    def get_badges_earned(self, obj):
        """Get user's badges with award dates."""
        from community.models import UserBadge
        from community.serializers import UserBadgeSerializer
        
        badges = UserBadge.objects.filter(user=obj).select_related('badge').order_by('-awarded_at')[:20]
        return UserBadgeSerializer(badges, many=True).data
    
    def get_contribution_stats(self, obj):
        """Get contribution statistics - items donated, reservations, mentorships."""
        from inventory.models import InventoryItem
        from reservations.models import Reservation
        from community.models import MentorshipConnection, Feedback
        
        # Items contributed
        items_contributed = InventoryItem.objects.filter(
            donor=obj,
            status__in=['available', 'reserved', 'borrowed']
        ).count()
        
        # Successful reservations (completed)
        successful_reservations = Reservation.objects.filter(
            user=obj,
            status='completed'
        ).count()
        
        # Active mentorships (as mentor)
        active_mentorships = MentorshipConnection.objects.filter(
            mentor=obj,
            status='active'
        ).count() if obj.is_mentor else 0
        
        # Positive feedback received
        positive_feedback = Feedback.objects.filter(
            user=obj,
            type='positive',
            rating__gte=4
        ).count()
        
        return {
            'items_contributed': items_contributed,
            'successful_reservations': successful_reservations,
            'active_mentorships': active_mentorships,
            'positive_feedback_count': positive_feedback,
        }
    
    def get_member_since(self, obj):
        """Return formatted member since date."""
        return obj.created_at.strftime('%B %Y')


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that user with email exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change (authenticated users)."""
    current_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    def validate_current_password(self, value):
        """Validate that the current password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        
        # Ensure new password is different from current
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from current password."})
        
        return attrs
    
    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class OnboardingPreferencesSerializer(serializers.Serializer):
    """Serializer for onboarding preferences."""
    # Personal needs
    clothing_sizes = serializers.JSONField(required=False, help_text="Clothing sizes (shirt, pants, shoes)")
    dietary_restrictions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of dietary restrictions"
    )
    skill_interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Skills interested in learning or sharing"
    )
    
    # Language and communication
    preferred_language = serializers.CharField(max_length=10, required=False)
    languages_spoken = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Languages the user speaks"
    )
    
    # Location and arrival
    address = serializers.CharField(required=False, allow_blank=True)
    arrival_date = serializers.DateField(required=False, allow_null=True)
    
    # Interests and needs
    immediate_needs = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Immediate items or resources needed"
    )
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="General interests and hobbies"
    )
    
    # Mentorship
    seeking_mentor = serializers.BooleanField(required=False, default=False)
    mentor_preferences = serializers.JSONField(required=False, help_text="Mentor matching preferences")
    
    def update_user_preferences(self, user, validated_data):
        """Update user model with onboarding preferences."""
        # Update direct user fields
        if 'preferred_language' in validated_data:
            user.preferred_language = validated_data['preferred_language']
        if 'address' in validated_data:
            user.address = validated_data['address']
        if 'arrival_date' in validated_data:
            user.arrival_date = validated_data['arrival_date']
        
        # Update preferences JSON field
        preferences = user.preferences or {}
        
        # Store all preference data
        for key, value in validated_data.items():
            if key not in ['preferred_language', 'address', 'arrival_date']:
                preferences[key] = value
        
        user.preferences = preferences
        user.save()
        
        return user
