# Phase 3c: Logging Framework

**Branch:** `refactor/3c-logging`

## New file: Display/logger.py

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(level=logging.INFO):
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")

    file_handler = RotatingFileHandler(
        log_dir / "scope.log", maxBytes=5_000_000, backupCount=3
    )
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
```

- Call `setup_logging()` at start of each disptest entry point
- Replace all remaining `print()` calls with appropriate log levels
- FPS: `DEBUG`. Sensor warnings: `WARNING`. C failures: `ERROR`.

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
