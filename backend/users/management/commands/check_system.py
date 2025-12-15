"""
Management command to check system health and configuration.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models_notifications import Notification, NotificationPreference, DeviceToken
from reservations.models import Reservation
from inventory.models import InventoryItem
from hubs.models import Hub

User = get_user_model()


class Command(BaseCommand):
    help = 'Check system health and display statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== fLOKr System Status ===\n'))
        
        # Database connectivity
        self.check_database()
        
        # Model counts
        self.check_models()
        
        # Notification system
        self.check_notifications()
        
        self.stdout.write(self.style.SUCCESS('\n✓ System check complete!\n'))
    
    def check_database(self):
        """Check database connectivity."""
        self.stdout.write(self.style.HTTP_INFO('--- Database ---'))
        try:
            User.objects.count()
            self.stdout.write(self.style.SUCCESS('✓ Database connected'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database error: {e}'))
    
    def check_models(self):
        """Check model counts."""
        self.stdout.write(self.style.HTTP_INFO('\n--- Data Counts ---'))
        
        counts = {
            'Users': User.objects.count(),
            'Hubs': Hub.objects.count(),
            'Inventory Items': InventoryItem.objects.count(),
            'Reservations': Reservation.objects.count(),
            'Notifications': Notification.objects.count(),
            'Device Tokens': DeviceToken.objects.count(),
        }
        
        for model, count in counts.items():
            self.stdout.write(f'{model}: {count}')
    
    def check_notifications(self):
        """Check notification system."""
        self.stdout.write(self.style.HTTP_INFO('\n--- Notification System ---'))
        
        # Check if Firebase is configured
        try:
            from users.notifications import notification_service
            if notification_service.firebase_initialized:
                self.stdout.write(self.style.SUCCESS('✓ Firebase initialized'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Firebase not initialized (using console logging)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Notification service error: {e}'))
        
        # Check notification preferences
        prefs_count = NotificationPreference.objects.count()
        self.stdout.write(f'Notification preferences: {prefs_count}')
        
        # Check active devices
        active_devices = DeviceToken.objects.filter(is_active=True).count()
        self.stdout.write(f'Active devices: {active_devices}')
