from django.contrib import admin
from .models import Badge, UserBadge, Feedback, MentorshipConnection, Message


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'awarded_at']
    list_filter = ['badge__category', 'awarded_at']
    search_fields = ['user__email', 'badge__name']
    ordering = ['-awarded_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'status', 'rating', 'created_at']
    list_filter = ['type', 'status', 'created_at']
    search_fields = ['user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(MentorshipConnection)
class MentorshipConnectionAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'mentee', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'start_date']
    search_fields = ['mentor__email', 'mentee__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'connection', 'read', 'created_at']
    list_filter = ['read', 'created_at']
    search_fields = ['sender__email', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
