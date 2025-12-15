@echo off
REM Update conda environment with new dependencies

echo ================================
echo Updating fLOKr Conda Environment
echo ================================
echo.

echo This will update your conda environment with GDAL and other GIS libraries.
echo.

echo Step 1: Updating environment...
conda env update -f backend/environment.yml --prune

if errorlevel 1 (
    echo.
    echo ❌ Update failed. Trying alternative method...
    echo.
    echo Activating environment and installing packages directly...
    call conda activate flokr
    conda install -c conda-forge gdal geos proj -y
    
    if errorlevel 1 (
        echo.
        echo ❌ Installation failed.
        echo.
        echo Please try manually:
        echo   conda activate flokr
        echo   conda install -c conda-forge gdal geos proj
        exit /b 1
    )
)

echo.
echo ================================
echo ✅ Environment Updated!
echo ================================
echo.
echo Next steps:
echo 1. conda activate flokr
echo 2. Verify GDAL: python -c "from osgeo import gdal; print(gdal.__version__)"
echo 3. Run checkpoint: scripts\checkpoint.bat
echo.
