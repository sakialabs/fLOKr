from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_mentor', 'reputation_score', 'created_at']
    list_filter = ['role', 'is_mentor', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'address', 'location')}),
        ('Role & Permissions', {'fields': ('role', 'is_mentor', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Platform Data', {'fields': ('assigned_hub', 'arrival_date', 'preferred_language', 'preferences', 'reputation_score', 'late_return_count', 'borrowing_restricted_until')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
