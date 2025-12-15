#!/bin/bash
# fLOKr Backend Setup Script

echo "🚀 Setting up fLOKr Backend..."

# Check if conda is installed
if command -v conda &> /dev/null; then
    echo "✓ Conda found"
    
    # Create conda environment
    echo "📦 Creating conda environment 'flokr'..."
    conda env create -f backend/environment.yml
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. conda activate flokr"
    echo "2. cd backend"
    echo "3. cp .env.example .env"
    echo "4. docker-compose up -d (from project root)"
    echo "5. python manage.py migrate"
    echo "6. python manage.py runserver"
else
    echo "✗ Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi
