# fLOKr Scripts

Utility scripts for development, testing, and deployment.

## Setup Scripts

### `setup-backend.sh`
Initial backend setup with conda environment.

**Usage:**
```bash
./scripts/setup-backend.sh
```

**What it does:**
- Checks for conda installation
- Creates `flokr` conda environment
- Installs all Python dependencies
- Provides next steps

### `update-env.bat` / `update-env.sh`
Update existing conda environment with new dependencies (like GDAL).

**Usage:**
```bash
# Windows
scripts\update-env.bat

# Mac/Linux
./scripts/update-env.sh
```

**What it does:**
- Updates conda environment from environment.yml
- Installs GDAL, GEOS, PROJ for GIS support
- Falls back to direct installation if update fails
- Verifies installation

## Testing Scripts

### `run_tests.py`
Run backend tests with custom test runner.

**Usage:**
```bash
# Run all tests
python scripts/run_tests.py

# Run specific app tests
python scripts/run_tests.py users
python scripts/run_tests.py reservations
```

**What it does:**
- Runs Django test suite
- Shows detailed output (verbosity=2)
- Returns exit code 0 on success, 1 on failure

## Checkpoint Scripts

### `checkpoint.bat` (Windows)
Comprehensive verification for Checkpoint 1.

**Usage:**
```bash
scripts\checkpoint.bat
```

### `checkpoint.sh` (Mac/Linux)
Comprehensive verification for Checkpoint 1.

**Usage:**
```bash
./scripts/checkpoint.sh
```

**What they do:**
1. Check database connectivity
2. Run migrations
3. Setup Celery periodic tasks
4. Run system health check
5. Execute all tests (18 tests total)
6. Display next steps

**Expected output:**
```
✓ Database OK
✓ Migrations OK
✓ Periodic tasks OK
✓ System check complete
✓ Tests passed (18 tests)
✅ Checkpoint 1 Complete!
```

## Making Scripts Executable

### Mac/Linux
```bash
chmod +x scripts/*.sh
```

### Windows
Scripts with `.bat` extension are executable by default.

## Troubleshooting

**"Permission denied" on Mac/Linux:**
```bash
chmod +x scripts/checkpoint.sh
chmod +x scripts/setup-backend.sh
```

**"Command not found" for Python scripts:**
```bash
# Make sure you're in project root
python scripts/run_tests.py
```

**Scripts can't find backend:**
All scripts are designed to run from the project root directory.
