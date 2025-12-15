from django.contrib import admin
from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'hub', 'category', 'condition', 'quantity_available', 'quantity_total', 'status', 'created_at']
    list_filter = ['status', 'condition', 'category', 'hub']
    search_fields = ['name', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
