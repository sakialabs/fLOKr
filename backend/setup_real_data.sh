#!/bin/bash

# fLOKr - Setup Script for Real Data Migration
# This script sets up the database with realistic seeded data

set -e

echo "=========================================="
echo "fLOKr - Real Data Setup"
echo "=========================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo "Error: This script must be run from the backend directory"
    exit 1
fi

# Check if Python environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: No virtual environment detected"
    echo "Activating environment..."
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Could not find virtual environment"
        exit 1
    fi
fi

echo "✓ Environment ready"
echo ""

# Install Faker if not already installed
echo "Installing dependencies..."
pip install faker > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Create migrations for new models
echo "Creating database migrations..."
python manage.py makemigrations
echo "✓ Migrations created"
echo ""

# Apply migrations
echo "Applying migrations..."
python manage.py migrate
echo "✓ Migrations applied"
echo ""

# Seed the database
echo "=========================================="
echo "Seeding realistic data..."
echo "=========================================="
echo ""
python manage.py seed_realistic_data

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your database now contains:"
echo "  ✓ 5 Community Hubs"
echo "  ✓ 50 Realistic Users (newcomers, members, stewards, partners)"
echo "  ✓ 100+ Inventory Items across all categories"
echo "  ✓ 50+ Reservations (active, pending, overdue, returned)"
echo "  ✓ 8 Achievement Badges"
echo "  ✓ Badge Awards"
echo "  ✓ 10+ Mentorship Connections with Messages"
echo "  ✓ 20+ Events (past and upcoming)"
echo "  ✓ 15+ Hub Announcements"
echo "  ✓ 30+ Feedback Entries"
echo ""
echo "Next steps:"
echo "  1. Start the backend server: python manage.py runserver"
echo "  2. Start the frontend: cd ../frontend && npm run dev"
echo "  3. Visit http://localhost:3000"
echo ""
echo "Happy testing! 🎉"
