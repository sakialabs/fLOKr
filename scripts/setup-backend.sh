#!/bin/bash
# Backend setup with conda

set -e

echo "🚀 Setting up fLOKr backend..."

if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found"
    echo "Install from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Conda found"
echo "📦 Creating environment..."
conda env create -f backend/environment.yml

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next:"
echo "  1. conda activate flokr"
echo "  2. ./scripts/docker.sh start"
echo ""
