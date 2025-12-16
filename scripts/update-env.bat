@echo off
REM Update conda environment

echo ⏳ Updating fLOKr conda environment...
echo.

conda env update -f backend/environment.yml --prune

if errorlevel 1 (
    echo ⚠ Update failed, trying direct install...
    call conda activate flokr
    conda install -c conda-forge gdal geos proj -y
    if errorlevel 1 (
        echo ❌ Failed. Try manually:
        echo   conda activate flokr
        echo   conda install -c conda-forge gdal geos proj
        exit /b 1
    )
)

echo.
echo ✅ Environment updated!
echo.
echo Next:
echo   1. conda activate flokr
echo   2. scripts\checkpoint.bat
echo.
