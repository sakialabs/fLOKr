from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'hub', 'status', 'pickup_date', 'expected_return_date', 'actual_return_date', 'created_at']
    list_filter = ['status', 'hub', 'pickup_date', 'expected_return_date']
    search_fields = ['user__email', 'item__name']
    readonly_fields = ['created_at', 'updated_at', 'reservation_date']
    ordering = ['-created_at']
