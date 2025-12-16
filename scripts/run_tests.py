#!/usr/bin/env python
"""Test runner for fLOKr backend.

Usage:
    python scripts/run_tests.py              # All tests
    python scripts/run_tests.py users        # Specific app
"""
import sys
import os
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flokr.settings')
django.setup()

from django.test.utils import get_runner
from django.conf import settings


def run_tests(app_label=None):
    """Run tests for app or all apps."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
    
    if app_label:
        print(f"\n🧪 Running tests: {app_label}\n")
        return test_runner.run_tests([app_label])
    
    print(f"\n🧪 Running all tests\n")
    return test_runner.run_tests([
        'users.tests_notifications',
        'reservations.tests_tasks',
    ])


if __name__ == '__main__':
    app = sys.argv[1] if len(sys.argv) > 1 else None
    failures = run_tests(app)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed\n")
        sys.exit(1)
    
    print(f"\n✅ All tests passed!\n")
    sys.exit(0)
