"""
Management command to set up periodic tasks in the database.

This command creates the periodic task schedules defined in settings.py
in the django-celery-beat database tables.

Usage:
    python manage.py setup_periodic_tasks
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Set up periodic tasks for Celery Beat'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Setting up Periodic Tasks ===\n'))
        
        # Get the beat schedule from settings
        beat_schedule = getattr(settings, 'CELERY_BEAT_SCHEDULE', {})
        
        if not beat_schedule:
            self.stdout.write(
                self.style.WARNING('No CELERY_BEAT_SCHEDULE found in settings')
            )
            return
        
        created_count = 0
        updated_count = 0
        
        for task_name, task_config in beat_schedule.items():
            try:
                # Extract schedule information
                schedule = task_config.get('schedule')
                task_path = task_config.get('task')
                options = task_config.get('options', {})
                
                if not schedule or not task_path:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Invalid config for {task_name}')
                    )
                    continue
                
                # Create or get crontab schedule
                if hasattr(schedule, 'minute'):
                    # It's a crontab schedule
                    crontab, _ = CrontabSchedule.objects.get_or_create(
                        minute=schedule.minute,
                        hour=schedule.hour,
                        day_of_week=schedule.day_of_week,
                        day_of_month=schedule.day_of_month,
                        month_of_year=schedule.month_of_year,
                    )
                    
                    # Create or update periodic task
                    task, created = PeriodicTask.objects.update_or_create(
                        name=task_name,
                        defaults={
                            'task': task_path,
                            'crontab': crontab,
                            'enabled': True,
                            'expires': options.get('expires'),
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Created: {task_name}')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'↻ Updated: {task_name}')
                        )
                    
                    self.stdout.write(f'  Task: {task_path}')
                    self.stdout.write(f'  Schedule: {crontab}')
                    self.stdout.write('')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error setting up {task_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} created, {updated_count} updated'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\nStart Celery Beat with: celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler'
            )
        )
        self.stdout.write('')
