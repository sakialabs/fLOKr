from django.contrib import admin
from .models import Hub


@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'status', 'current_inventory_count', 'capacity', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['stewards']
    ordering = ['name']
