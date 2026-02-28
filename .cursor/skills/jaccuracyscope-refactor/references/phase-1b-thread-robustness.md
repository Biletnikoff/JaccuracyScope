# Phase 1b: Thread Robustness

**Branch:** `refactor/1b-thread-robustness`

**Files to modify (all in Display/):**

## CamThreader.py and CamThreaderSLOWFPS.py

1. Add `from threading import Thread, Lock` (replace `from threading import Thread`)
2. In `__init__`: add `self._lock = Lock()`
3. In `run()`: wrap `self.imageout = ...` and `self.fpsaveout = fpsave` in `with self._lock:`
4. Add getter:
   ```python
   def get_frame(self):
       with self._lock:
           return self.imageout
   def get_fps(self):
       with self._lock:
           return self.fpsaveout
   ```
5. Wrap `run()` body in `try/except Exception` with logging

## SensorThreaderSlowerRotaryEncodersTRY.py

1. Add `import logging` and `from threading import Thread, Lock`
2. Add `logger = logging.getLogger(__name__)` at module level
3. In `__init__`: add `self._lock = Lock()`
4. Replace all 6 bare `except:` blocks:
   - **Line 195-196**: `except OSError as e: logger.warning("Magnetometer read failed: %s", e)`
   - **Line 211-214**: `except OSError: ...` with default values and logging
   - **Line 222-225**: `except OSError: ...` for gyro with default values and logging
   - **Line 259-262**: `except OSError: ...` for encoder position
   - **Line 293-296**: `except OSError as e: logger.warning("Encoder backend error: %s", e)`
5. Add I2C retry logic (3 retries with backoff) for sensor reads
6. Wrap all shared output writes in `with self._lock:`
7. Add getters: `get_orientation()`, `get_encoders()`, `get_compass()`
8. Wrap `run()` body in `try/except Exception` with logging

## BallisticThreader4Printer.py (and both Laser variants)

1. Add `import logging` and `from threading import Thread, Lock`
2. Add `logger = logging.getLogger(__name__)` at module level
3. In `__init__`: add `self._lock = Lock()`
4. Wrap all writes to `self.solution`, `self.plotter`, `self.fpsaveout`,
   `self.GNUySender`, `self.maxheight` in `with self._lock:`
5. Add getter: `get_output()` returning `(solution, plotter, fpsaveout)`
6. Wrap `run()` body in `try/except Exception` with logging

## All disptest*.py scripts

Replace every direct `Threader.thread.attribute` read with getter calls:
- `CamThreader.thread.imageout` -> `CamThreader.thread.get_frame()`
- `SensorThreader.thread.pitch` -> via `SensorThreader.thread.get_orientation()`
- `BallisticThreader.thread.solution` -> via `BallisticThreader.thread.get_output()`
- `SensorThreader.thread.encoder1Output` -> via `SensorThreader.thread.get_encoders()`

**Note:** For writes TO threads (setting `ScopeMode`, `targetdistin`, etc.),
these are single-writer (main thread) so the risk is lower. Add lock protection
to setters in Phase 2b when the classes are consolidated.

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`

## Hook step (final commit)

Append to `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: no-direct-thread-access
        name: Block direct thread attribute mutation
        entry: 'Threader\.thread\.\w+\s*='
        language: pygrep
        types: [python]
      - id: no-bare-except
        name: Block bare except clauses
        entry: 'except\s*:'
        language: pygrep
        types: [python]
      - id: no-profanity
        name: Block unprofessional comments
        entry: '(shit|fuck|wtf|cock|buttholes)'
        language: pygrep
        types_or: [python, c]
        args: [-i]
```

Update `.ruff.toml`:
```toml
select = ["E", "F", "B001", "B006"]
ignore = []
```

**Commits:**
1. `refactor(threads): add Lock and getters to CamThreader`
2. `refactor(sensor): add Lock, typed exceptions, logging to SensorThreader`
3. `refactor(ballistics): add Lock and getters to BallisticThreader variants`
4. `refactor(display): replace direct thread access with getters in disptest scripts`
5. `ci(hooks): add thread-access, bare-except, and profanity hooks`
