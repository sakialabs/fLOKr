# Development Scripts

## 🐳 Docker (Recommended)

**Single command interface:**
```bash
./scripts/docker.sh [command]    # Mac/Linux
scripts\docker.bat [command]     # Windows
```

**Commands:**
| Command | Description |
|---------|-------------|
| `start` | Start all services |
| `stop` | Stop all services |
| `restart` | Restart services |
| `logs` | View logs |
| `shell` | Django shell |
| `bash` | Container bash |
| `test` | Run tests |
| `migrate` | Run migrations |
| `clean` | Remove all |
| `status` | Show status |

**Quick start:**
```bash
./scripts/docker.sh start    # Start
./scripts/docker.sh logs     # Watch
./scripts/docker.sh test     # Test
./scripts/docker.sh stop     # Stop
```

## 🐍 Local Development

**Setup:**
```bash
./scripts/setup-backend.sh    # Initial setup
./scripts/update-env.sh       # Update deps
```

**Testing:**
```bash
python scripts/run_tests.py        # All tests
python scripts/run_tests.py users  # Specific app
```

**Verification:**
```bash
./scripts/checkpoint.sh       # Verify milestone
```

**Multi-service:**
```bash
scripts\start-all.bat         # Start backend + frontend + mobile (Windows)
```

## 📝 Notes

- Run from project root
- Make executable: `chmod +x scripts/*.sh`
- See [DOCKER.md](../DOCKER.md) for details
