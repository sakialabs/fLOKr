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
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'role',
            'preferred_language', 'address', 'location', 'assigned_hub',
            'arrival_date', 'preferences', 'reputation_score', 'is_mentor',
            'late_return_count', 'borrowing_restricted_until', 'created_at'
        ]
        read_only_fields = [
            'id', 'email', 'role', 'reputation_score', 'late_return_count',
            'borrowing_restricted_until', 'created_at'
        ]


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
