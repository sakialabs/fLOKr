"""
Tests for Celery tasks.

These tests verify that background tasks execute correctly without
requiring a running Celery worker (tasks run synchronously in tests).
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from reservations.models import Reservation
from reservations.tasks import (
    expire_pending_reservations,
    send_pickup_reminders,
    send_return_reminders,
    send_overdue_reminders,
)
from inventory.models import InventoryItem
from hubs.models import Hub

User = get_user_model()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ReservationTaskTests(TestCase):
    """Test reservation background tasks."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=User.Role.NEWCOMER
        )
        
        # Create test hub
        self.hub = Hub.objects.create(
            name='Test Hub',
            address='123 Test St',
            location='POINT(-79.8711 43.2557)',  # Hamilton, ON
            status=Hub.Status.ACTIVE
        )
        
        # Create test item
        self.item = InventoryItem.objects.create(
            hub=self.hub,
            name='Test Item',
            description='A test item',
            category='clothing',
            quantity_total=5,
            quantity_available=5,
            status=InventoryItem.Status.ACTIVE
        )
    
    def test_expire_pending_reservations_past_pickup_date(self):
        """Test that pending reservations past pickup date are expired."""
        # Create a pending reservation with pickup date in the past
        yesterday = timezone.now().date() - timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PENDING,
            pickup_date=yesterday,
            expected_return_date=yesterday + timedelta(days=7)
        )
        
        # Item should have reduced availability
        self.item.quantity_available = 4
        self.item.save()
        
        # Run the task
        with patch('reservations.tasks.send_expiration_notification.delay') as mock_notify:
            result = expire_pending_reservations()
        
        # Verify reservation was cancelled
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CANCELLED)
        
        # Verify inventory was restored
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity_available, 5)
        
        # Verify notification was sent
        mock_notify.assert_called_once()
        
        # Verify result
        self.assertEqual(result['expired'], 1)
        self.assertEqual(result['failed'], 0)
    
    def test_expire_pending_reservations_future_pickup_date(self):
        """Test that pending reservations with future pickup date are not expired."""
        # Create a pending reservation with pickup date in the future
        tomorrow = timezone.now().date() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PENDING,
            pickup_date=tomorrow,
            expected_return_date=tomorrow + timedelta(days=7)
        )
        
        # Run the task
        result = expire_pending_reservations()
        
        # Verify reservation was NOT cancelled
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.PENDING)
        
        # Verify no reservations were expired
        self.assertEqual(result['expired'], 0)
    
    def test_send_pickup_reminders_for_tomorrow(self):
        """Test that pickup reminders are sent for reservations tomorrow."""
        # Create a confirmed reservation with pickup date tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.CONFIRMED,
            pickup_date=tomorrow,
            expected_return_date=tomorrow + timedelta(days=7)
        )
        
        # Run the task
        with patch('reservations.tasks.send_pickup_reminder_notification.delay') as mock_notify:
            result = send_pickup_reminders()
        
        # Verify notification was sent
        mock_notify.assert_called_once()
        call_kwargs = mock_notify.call_args[1]
        self.assertEqual(call_kwargs['user_email'], self.user.email)
        self.assertEqual(call_kwargs['item_name'], self.item.name)
        
        # Verify result
        self.assertEqual(result['reminders_sent'], 1)
        self.assertEqual(result['failed'], 0)
    
    def test_send_return_reminders_for_tomorrow(self):
        """Test that return reminders are sent for items due tomorrow."""
        # Create a picked-up reservation with return date tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PICKED_UP,
            pickup_date=timezone.now().date(),
            expected_return_date=tomorrow
        )
        
        # Run the task
        with patch('reservations.tasks.send_return_reminder_notification.delay') as mock_notify:
            result = send_return_reminders()
        
        # Verify notification was sent
        mock_notify.assert_called_once()
        call_kwargs = mock_notify.call_args[1]
        self.assertEqual(call_kwargs['user_email'], self.user.email)
        self.assertEqual(call_kwargs['item_name'], self.item.name)
        
        # Verify result
        self.assertEqual(result['reminders_sent'], 1)
    
    def test_send_overdue_reminders_updates_status(self):
        """Test that overdue reminders update reservation status to OVERDUE."""
        # Create a picked-up reservation that's overdue
        yesterday = timezone.now().date() - timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PICKED_UP,
            pickup_date=yesterday - timedelta(days=7),
            expected_return_date=yesterday
        )
        
        # Run the task
        with patch('reservations.tasks.send_overdue_notification.delay') as mock_notify:
            result = send_overdue_reminders()
        
        # Verify status was updated to OVERDUE
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.OVERDUE)
        
        # Verify notification was sent
        mock_notify.assert_called_once()
        
        # Verify result
        self.assertEqual(result['status_updated'], 1)
        self.assertEqual(result['reminders_sent'], 1)
    
    def test_send_overdue_reminders_escalation(self):
        """Test that overdue reminders are sent at correct intervals."""
        today = timezone.now().date()
        
        # Create reservations at different overdue intervals
        test_cases = [
            (1, True),   # 1 day overdue - should send
            (2, False),  # 2 days overdue - should not send
            (3, True),   # 3 days overdue - should send
            (4, False),  # 4 days overdue - should not send
            (7, True),   # 7 days overdue - should send
            (14, True),  # 14 days overdue - should send (weekly)
        ]
        
        for days_overdue, should_send in test_cases:
            with self.subTest(days_overdue=days_overdue):
                # Create overdue reservation
                reservation = Reservation.objects.create(
                    user=self.user,
                    item=self.item,
                    hub=self.hub,
                    quantity=1,
                    status=Reservation.Status.OVERDUE,
                    pickup_date=today - timedelta(days=days_overdue + 7),
                    expected_return_date=today - timedelta(days=days_overdue)
                )
                
                # Run the task
                with patch('reservations.tasks.send_overdue_notification.delay') as mock_notify:
                    send_overdue_reminders()
                
                # Verify notification was sent or not based on interval
                if should_send:
                    self.assertTrue(mock_notify.called)
                else:
                    self.assertFalse(mock_notify.called)
                
                # Clean up
                reservation.delete()
    
    def test_overdue_reminders_notify_stewards_after_3_days(self):
        """Test that stewards are notified for items 3+ days overdue."""
        # Add steward to hub
        steward = User.objects.create_user(
            email='steward@example.com',
            password='testpass123',
            first_name='Steward',
            last_name='User',
            role=User.Role.STEWARD
        )
        self.hub.stewards.add(steward)
        
        # Create reservation 3 days overdue
        three_days_ago = timezone.now().date() - timedelta(days=3)
        reservation = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.OVERDUE,
            pickup_date=three_days_ago - timedelta(days=7),
            expected_return_date=three_days_ago
        )
        
        # Run the task
        with patch('reservations.tasks.send_overdue_notification.delay'):
            with patch('reservations.tasks.notify_stewards_overdue.delay') as mock_steward_notify:
                send_overdue_reminders()
        
        # Verify steward notification was sent
        mock_steward_notify.assert_called_once()
        call_kwargs = mock_steward_notify.call_args[1]
        self.assertEqual(call_kwargs['hub_id'], str(self.hub.id))
        self.assertEqual(call_kwargs['days_overdue'], 3)
    
    def test_multiple_reservations_processed_correctly(self):
        """Test that multiple reservations are processed in one task run."""
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Create multiple expired reservations
        for i in range(3):
            Reservation.objects.create(
                user=self.user,
                item=self.item,
                hub=self.hub,
                quantity=1,
                status=Reservation.Status.PENDING,
                pickup_date=yesterday,
                expected_return_date=yesterday + timedelta(days=7)
            )
        
        # Reduce availability
        self.item.quantity_available = 2
        self.item.save()
        
        # Run the task
        with patch('reservations.tasks.send_expiration_notification.delay'):
            result = expire_pending_reservations()
        
        # Verify all reservations were expired
        self.assertEqual(result['expired'], 3)
        
        # Verify inventory was fully restored
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity_available, 5)
    
    def test_task_handles_errors_gracefully(self):
        """Test that task continues processing even if one reservation fails."""
        yesterday = timezone.now().date() - timedelta(days=1)
        
        # Create two expired reservations
        reservation1 = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PENDING,
            pickup_date=yesterday,
            expected_return_date=yesterday + timedelta(days=7)
        )
        
        reservation2 = Reservation.objects.create(
            user=self.user,
            item=self.item,
            hub=self.hub,
            quantity=1,
            status=Reservation.Status.PENDING,
            pickup_date=yesterday,
            expected_return_date=yesterday + timedelta(days=7)
        )
        
        # Mock notification to fail for first reservation
        def side_effect(*args, **kwargs):
            if kwargs.get('reservation_id') == str(reservation1.id):
                raise Exception("Notification failed")
        
        with patch('reservations.tasks.send_expiration_notification.delay', side_effect=side_effect):
            result = expire_pending_reservations()
        
        # Both reservations should still be cancelled despite notification failure
        reservation1.refresh_from_db()
        reservation2.refresh_from_db()
        self.assertEqual(reservation1.status, Reservation.Status.CANCELLED)
        self.assertEqual(reservation2.status, Reservation.Status.CANCELLED)


@pytest.mark.django_db
class TestTaskConfiguration:
    """Test task configuration and setup."""
    
    def test_periodic_tasks_configured(self):
        """Test that periodic tasks are properly configured in settings."""
        from django.conf import settings
        
        beat_schedule = settings.CELERY_BEAT_SCHEDULE
        
        # Verify all required tasks are configured
        required_tasks = [
            'expire-pending-reservations',
            'send-pickup-reminders',
            'send-return-reminders',
            'send-overdue-reminders',
            'generate-reservation-report',
            'cleanup-old-reservations',
        ]
        
        for task_name in required_tasks:
            assert task_name in beat_schedule, f"Task {task_name} not configured"
            assert 'task' in beat_schedule[task_name]
            assert 'schedule' in beat_schedule[task_name]
