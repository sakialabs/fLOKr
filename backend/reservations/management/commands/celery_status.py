"""
Management command to check Celery worker and task status.

Usage:
    python manage.py celery_status
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from celery import current_app
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule


class Command(BaseCommand):
    help = 'Display Celery worker status and scheduled tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== Celery Status ===\n'))
        
        # Check worker status
        self.check_workers()
        
        # Check scheduled tasks
        self.check_scheduled_tasks()
        
        # Check recent task results
        self.check_recent_tasks()

    def check_workers(self):
        """Check if Celery workers are running."""
        self.stdout.write(self.style.HTTP_INFO('\n--- Active Workers ---'))
        
        try:
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                for worker, info in stats.items():
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {worker}')
                    )
                    self.stdout.write(f"  Pool: {info.get('pool', {}).get('implementation', 'N/A')}")
                    self.stdout.write(f"  Max concurrency: {info.get('pool', {}).get('max-concurrency', 'N/A')}")
            else:
                self.stdout.write(
                    self.style.ERROR('✗ No active workers found')
                )
                self.stdout.write(
                    self.style.WARNING('  Start a worker with: celery -A flokr worker -l info')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error checking workers: {str(e)}')
            )

    def check_scheduled_tasks(self):
        """Check scheduled periodic tasks."""
        self.stdout.write(self.style.HTTP_INFO('\n--- Scheduled Periodic Tasks ---'))
        
        try:
            tasks = PeriodicTask.objects.filter(enabled=True)
            
            if tasks.exists():
                for task in tasks:
                    status = '✓' if task.enabled else '✗'
                    self.stdout.write(
                        self.style.SUCCESS(f'{status} {task.name}')
                    )
                    self.stdout.write(f'  Task: {task.task}')
                    
                    if task.crontab:
                        self.stdout.write(f'  Schedule: {task.crontab}')
                    elif task.interval:
                        self.stdout.write(f'  Schedule: Every {task.interval}')
                    
                    if task.last_run_at:
                        self.stdout.write(f'  Last run: {task.last_run_at}')
                    else:
                        self.stdout.write('  Last run: Never')
                    
                    self.stdout.write('')
            else:
                self.stdout.write(
                    self.style.WARNING('No scheduled tasks found')
                )
                self.stdout.write(
                    self.style.WARNING('  Run migrations to create default schedules')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error checking scheduled tasks: {str(e)}')
            )

    def check_recent_tasks(self):
        """Check recent task execution."""
        self.stdout.write(self.style.HTTP_INFO('\n--- Recent Task Activity ---'))
        
        try:
            inspect = current_app.control.inspect()
            
            # Active tasks
            active = inspect.active()
            if active:
                active_count = sum(len(tasks) for tasks in active.values())
                self.stdout.write(
                    self.style.SUCCESS(f'Active tasks: {active_count}')
                )
            else:
                self.stdout.write('Active tasks: 0')
            
            # Scheduled tasks
            scheduled = inspect.scheduled()
            if scheduled:
                scheduled_count = sum(len(tasks) for tasks in scheduled.values())
                self.stdout.write(
                    self.style.SUCCESS(f'Scheduled tasks: {scheduled_count}')
                )
            else:
                self.stdout.write('Scheduled tasks: 0')
            
            # Reserved tasks
            reserved = inspect.reserved()
            if reserved:
                reserved_count = sum(len(tasks) for tasks in reserved.values())
                self.stdout.write(
                    self.style.SUCCESS(f'Reserved tasks: {reserved_count}')
                )
            else:
                self.stdout.write('Reserved tasks: 0')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error checking recent tasks: {str(e)}')
            )
        
        self.stdout.write('')
