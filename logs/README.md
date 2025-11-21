# Logs Directory

This directory contains test execution logs and debugging output.

## Log Files

- **test_run_output.log** - Most recent pytest execution output
- **test_*.log** - Individual test execution logs (if configured)

## Generating Logs

### Console Output to File
```bash
pytest tests/ -v -s > logs/test_run_$(date +%Y%m%d_%H%M%S).log 2>&1
```

### With Timestamps
```bash
pytest tests/ -v -s | tee logs/test_run_$(date +%Y%m%d_%H%M%S).log
```

### Standard Run
```bash
pytest tests/ > logs/test_run_output.log 2>&1
```

## Viewing Logs

```bash
# View most recent log
cat logs/test_run_output.log

# View with pagination
less logs/test_run_output.log

# View last 50 lines
tail -50 logs/test_run_output.log

# Follow log in real-time (if running in background)
tail -f logs/test_run_output.log
```

## Log Rotation

Logs are not automatically rotated. For log rotation:

```bash
# Keep only last 5 logs
ls -t logs/test_run_*.log | tail -n +6 | xargs rm -f
```

## Note

Log files are excluded from version control via `.gitignore`.
