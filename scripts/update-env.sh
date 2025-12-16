#!/bin/bash
# Update conda environment

set -e

echo "⏳ Updating fLOKr conda environment..."
echo ""

if ! conda env update -f backend/environment.yml --prune; then
    echo "⚠ Update failed, trying direct install..."
    conda activate flokr
    conda install -c conda-forge gdal geos proj -y || {
        echo "❌ Failed. Try manually:"
        echo "  conda activate flokr"
        echo "  conda install -c conda-forge gdal geos proj"
        exit 1
    }
fi

echo ""
echo "✅ Environment updated!"
echo ""
echo "Next:"
echo "  1. conda activate flokr"
echo "  2. ./scripts/checkpoint.sh"
echo ""
