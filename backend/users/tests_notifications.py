"""
Tests for notification system.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models_notifications import Notification, NotificationPreference, DeviceToken
from users.notifications import notification_service

User = get_user_model()


class NotificationModelTests(TestCase):
    """Test notification models."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            recipient=self.user,
            type='reservation',
            title='Test Notification',
            body='This is a test',
            data={'key': 'value'}
        )
        
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.type, 'reservation')
        self.assertFalse(notification.read)
        self.assertFalse(notification.push_sent)
    
    def test_notification_preference_defaults(self):
        """Test notification preference defaults."""
        prefs = NotificationPreference.objects.create(user=self.user)
        
        self.assertTrue(prefs.push_enabled)
        self.assertTrue(prefs.push_reservations)
        self.assertTrue(prefs.push_reminders)
        self.assertFalse(prefs.quiet_hours_enabled)
    
    def test_device_token_creation(self):
        """Test device token creation."""
        token = DeviceToken.objects.create(
            user=self.user,
            token='test_token_123',
            platform='ios',
            device_name='iPhone 13'
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.platform, 'ios')
        self.assertTrue(token.is_active)


class NotificationServiceTests(TestCase):
    """Test notification service."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_create_notification_service(self):
        """Test creating notification via service."""
        notification = notification_service.create_notification(
            recipient_id=str(self.user.id),
            notification_type='system',
            title='Test',
            body='Test notification',
            data={'test': True},
            send_push=False  # Don't send push in tests
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, 'Test')
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            recipient=self.user,
            type='system',
            title='Test',
            body='Test'
        )
        
        success = notification_service.mark_as_read(
            notification_id=str(notification.id),
            user_id=str(self.user.id)
        )
        
        self.assertTrue(success)
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        self.assertIsNotNone(notification.read_at)
    
    def test_get_unread_count(self):
        """Test getting unread count."""
        # Create 3 notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                type='system',
                title=f'Test {i}',
                body='Test'
            )
        
        count = notification_service.get_unread_count(str(self.user.id))
        self.assertEqual(count, 3)
        
        # Mark one as read
        notification = Notification.objects.first()
        notification.read = True
        notification.save()
        
        count = notification_service.get_unread_count(str(self.user.id))
        self.assertEqual(count, 2)
    
    def test_register_device(self):
        """Test registering a device token."""
        device = notification_service.register_device(
            user_id=str(self.user.id),
            token='test_token_456',
            platform='android',
            device_name='Pixel 6'
        )
        
        self.assertIsNotNone(device)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.platform, 'android')
        self.assertTrue(device.is_active)
    
    def test_unregister_device(self):
        """Test unregistering a device token."""
        device = DeviceToken.objects.create(
            user=self.user,
            token='test_token_789',
            platform='ios'
        )
        
        success = notification_service.unregister_device('test_token_789')
        
        self.assertTrue(success)
        device.refresh_from_db()
        self.assertFalse(device.is_active)
