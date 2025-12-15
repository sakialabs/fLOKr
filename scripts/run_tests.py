#!/usr/bin/env python
"""
Test runner script for fLOKr backend.

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py users        # Run users app tests
    python scripts/run_tests.py reservations # Run reservations app tests
"""
import sys
import os
import django

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flokr.settings')
django.setup()

from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings


def run_tests(app_label=None):
    """Run tests for specified app or all apps."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    if app_label:
        print(f"\n{'='*60}")
        print(f"Running tests for: {app_label}")
        print(f"{'='*60}\n")
        failures = test_runner.run_tests([app_label])
    else:
        print(f"\n{'='*60}")
        print(f"Running all tests")
        print(f"{'='*60}\n")
        failures = test_runner.run_tests([
            'users.tests_notifications',
            'reservations.tests_tasks',
        ])
    
    return failures


if __name__ == '__main__':
    app_label = sys.argv[1] if len(sys.argv) > 1 else None
    failures = run_tests(app_label)
    
    if failures:
        print(f"\n{'='*60}")
        print(f"❌ {failures} test(s) failed")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print(f"✅ All tests passed!")
        print(f"{'='*60}\n")
        sys.exit(0)
