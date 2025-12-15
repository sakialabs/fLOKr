from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.gis.db import models as gis_models
from django.db import models
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model for fLOKr platform."""
    
    class Role(models.TextChoices):
        NEWCOMER = 'newcomer', 'Newcomer'
        COMMUNITY_MEMBER = 'community_member', 'Community Member'
        STEWARD = 'steward', 'Steward'
        ADMIN = 'admin', 'Admin'
        PARTNER = 'partner', 'Partner'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.NEWCOMER)
    preferred_language = models.CharField(max_length=10, default='en')
    address = models.TextField(blank=True)
    location = gis_models.PointField(null=True, blank=True, geography=True)
    assigned_hub = models.ForeignKey('hubs.Hub', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_users')
    arrival_date = models.DateField(null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    reputation_score = models.IntegerField(default=0)
    is_mentor = models.BooleanField(default=False)
    late_return_count = models.IntegerField(default=0)
    borrowing_restricted_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override username to make it optional
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
