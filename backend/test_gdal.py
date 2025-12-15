"""
Quick script to test GDAL configuration
"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("GDAL Configuration Test")
print("=" * 60)

# Check conda environment
conda_prefix = os.environ.get('CONDA_PREFIX')
print(f"\n1. CONDA_PREFIX: {conda_prefix}")

if conda_prefix:
    gdal_path = Path(conda_prefix) / 'Library' / 'bin'
    gdal_data = Path(conda_prefix) / 'Library' / 'share' / 'gdal'
    proj_lib = Path(conda_prefix) / 'Library' / 'share' / 'proj'
    
    print(f"\n2. Expected GDAL paths:")
    print(f"   - Library/bin: {gdal_path} (exists: {gdal_path.exists()})")
    print(f"   - GDAL_DATA: {gdal_data} (exists: {gdal_data.exists()})")
    print(f"   - PROJ_LIB: {proj_lib} (exists: {proj_lib.exists()})")
    
    # Try to import GDAL
    print(f"\n3. Testing GDAL import...")
    try:
        from osgeo import gdal
        print(f"   ✓ GDAL imported successfully!")
        print(f"   ✓ GDAL version: {gdal.__version__}")
    except Exception as e:
        print(f"   ✗ GDAL import failed: {e}")
    
    # Try Django GIS
    print(f"\n4. Testing Django GIS...")
    try:
        # Set up paths
        os.environ['PATH'] = str(gdal_path) + os.pathsep + os.environ.get('PATH', '')
        os.environ['GDAL_DATA'] = str(gdal_data)
        os.environ['PROJ_LIB'] = str(proj_lib)
        
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flokr.settings')
        django.setup()
        
        from django.contrib.gis.gdal import HAS_GDAL
        print(f"   ✓ Django GIS GDAL available: {HAS_GDAL}")
        
        if HAS_GDAL:
            from django.contrib.gis.gdal import GDAL_VERSION
            print(f"   ✓ Django sees GDAL version: {GDAL_VERSION}")
    except Exception as e:
        print(f"   ✗ Django GIS failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
