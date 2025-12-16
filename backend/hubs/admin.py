from django.contrib import admin
from .models import Hub, Event, Announcement


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'status', 'current_inventory_count', 'capacity', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['stewards']
    ordering = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'hub', 'event_type', 'event_date', 'organizer', 'created_at']
    list_filter = ['event_type', 'hub']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-event_date']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'hub', 'priority', 'author', 'active_until', 'created_at']
    list_filter = ['priority', 'hub']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
