from django.contrib import admin
from .models import InventoryItem, InventoryTransfer


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'hub', 'category', 'condition', 'quantity_available', 'quantity_total', 'status', 'created_at']
    list_filter = ['status', 'condition', 'category', 'hub']
    search_fields = ['name', 'description', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(InventoryTransfer)
class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ['item', 'from_hub', 'to_hub', 'quantity', 'status', 'initiated_by', 'created_at']
    list_filter = ['status', 'from_hub', 'to_hub']
    search_fields = ['item__name', 'reason', 'notes']
    readonly_fields = ['created_at', 'approved_at', 'completed_at', 'updated_at']
