from django.contrib import admin
from .models import Partner, DemandForecast


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'subscription_tier', 'status', 'subscription_start', 'subscription_end', 'created_at']
    list_filter = ['subscription_tier', 'status']
    search_fields = ['organization_name', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['organization_name']


@admin.register(DemandForecast)
class DemandForecastAdmin(admin.ModelAdmin):
    list_display = ['hub', 'category', 'forecast_date', 'predicted_demand', 'actual_demand', 'confidence_score', 'created_at']
    list_filter = ['hub', 'category', 'forecast_date']
    search_fields = ['hub__name', 'category']
    readonly_fields = ['created_at']
    ordering = ['-forecast_date']
