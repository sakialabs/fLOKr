"""
Celery configuration for flokr project.

This module configures Celery for background task processing including:
- Automatic task discovery from Django apps
- Task result backend configuration
- Beat scheduler for periodic tasks
- Logging and monitoring setup
"""
import os
import logging
from celery import Celery
from celery.signals import (
    task_prerun,
    task_postrun,
    task_failure,
    task_success,
    worker_ready,
)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flokr.settings')

app = Celery('flokr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

logger = logging.getLogger(__name__)


# ============================================================================
# Celery Signals for Monitoring and Logging
# ============================================================================

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when a task starts."""
    logger.info(
        f"Task started: {task.name} [ID: {task_id}]",
        extra={
            'task_name': task.name,
            'task_id': task_id,
            'args': args,
            'kwargs': kwargs,
        }
    )


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, state=None, **extra):
    """Log when a task completes."""
    logger.info(
        f"Task completed: {task.name} [ID: {task_id}] - State: {state}",
        extra={
            'task_name': task.name,
            'task_id': task_id,
            'state': state,
            'result': retval,
        }
    )


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, **extra):
    """Log when a task fails."""
    logger.error(
        f"Task failed: {sender.name} [ID: {task_id}] - Exception: {exception}",
        extra={
            'task_name': sender.name,
            'task_id': task_id,
            'exception': str(exception),
            'traceback': traceback,
        },
        exc_info=True
    )


@task_success.connect
def task_success_handler(sender=None, result=None, **extra):
    """Log successful task completion with result."""
    logger.debug(
        f"Task succeeded: {sender.name}",
        extra={
            'task_name': sender.name,
            'result': result,
        }
    )


@worker_ready.connect
def worker_ready_handler(sender=None, **extra):
    """Log when Celery worker is ready."""
    logger.info(
        "Celery worker is ready and waiting for tasks",
        extra={'worker': sender.hostname if sender else 'unknown'}
    )


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
    logger.info(f"Debug task executed: {self.request!r}")


@app.task(bind=True)
def health_check(self):
    """Health check task for monitoring."""
    return {
        'status': 'healthy',
        'worker': self.request.hostname,
        'task_id': self.request.id,
    }
