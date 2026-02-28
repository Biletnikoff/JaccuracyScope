# Phase Specifications

Detailed file lists, exact changes, and configuration contents for each phase.
Read the section for the specific phase you are executing.

---

## Phase 0: Hooks Infrastructure

**Branch:** `refactor/0-hooks-infrastructure`

**New files to create:**

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--select, "F,B001,B006", --fix]
      - id: ruff-format
        args: [--check]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: trailing-whitespace
        args: [--markdown-linebreak-ext=md]
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.1.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, refactor, docs, test, chore, ci, perf, safety]
```

### .ruff.toml

```toml
line-length = 200
target-version = "py311"

[lint]
select = ["F", "B001", "B006"]
ignore = ["F841"]

[lint.per-file-ignores]
"Display/disptest*.py" = ["F"]
```

### .github/workflows/ci.yml

```yaml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check Display/ --select "F,B001,B006"

  compile-c:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Compile ballistics library
        run: |
          cd Display/Balls
          gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall
```

**Commits:**
1. `ci(hooks): add pre-commit framework with Ruff and conventional commits`
2. `ci(github): add CI workflow for lint and C compilation`

---

## Phase 1a: C Library Safety

**Branch:** `refactor/1a-c-library-safety`

**Files to modify:**

### Display/Balls/exportme3.c

1. **Line 8**: Rename `main` to `SolveBallistic` (fix non-standard return type)
2. **Line 5**: After `double* sln;` add: `static int sln_valid = 0;`
3. **Lines 30-51**: Before each `SolveAll` call, add:
   ```c
   if (sln != NULL) { free(sln); sln = NULL; sln_valid = 0; }
   ```
4. **Lines 30-51**: Add `else return 0;` fallthrough for unhandled `G` values {2,3,4,5,6,8}
5. **Line 109**: Change `return (GetMOA(sln,Distdesired));` -- add NULL guard
6. **Lines 236-241**: In `free_pointer`, set `sln = NULL; sln_valid = 0;` after `free(sln);`

### Display/Balls/_solve.c

1. **Line 5**: After `malloc`, add:
   ```c
   if (ptr == NULL) return -1;
   ```
2. **Line 8**: Guard velocity:
   ```c
   if (Vi <= 0) return -1;
   ```
3. **Lines 29, 33-34**: Guard against `v == 0`:
   ```c
   if (v < 0.001) break;
   ```

### Display/Balls/_retrieve.c

Add to every `Get*` function (GetRange, GetPath, GetMOA, GetTime, GetWindage,
GetWindageMOA, GetVelocity, GetVx, GetVy):

```c
if (sln == NULL || yardage < 0) return 0;
```

### Display/BallisticThreader4Printer.py (and both Laser variants)

**Lines 37-38**: Update ctypes reference from `main` to `SolveBallistic`:
```python
self.GNUball = self.GNUballCLASS.SolveBallistic
```

### Verification

```bash
cd Display/Balls
gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror
```

### Hook step (final commit)

In `.github/workflows/ci.yml`, change `-Wall` to `-Wall -Werror`.

Commit: `ci(github): promote C compilation to -Wall -Werror`

---

## Phase 1b: Thread Robustness

**Branch:** `refactor/1b-thread-robustness`

**Files to modify (all in Display/):**

### CamThreader.py and CamThreaderSLOWFPS.py

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

### SensorThreaderSlowerRotaryEncodersTRY.py

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

### BallisticThreader4Printer.py (and both Laser variants)

1. Add `import logging` and `from threading import Thread, Lock`
2. Add `logger = logging.getLogger(__name__)` at module level
3. In `__init__`: add `self._lock = Lock()`
4. Wrap all writes to `self.solution`, `self.plotter`, `self.fpsaveout`,
   `self.GNUySender`, `self.maxheight` in `with self._lock:`
5. Add getter: `get_output()` returning `(solution, plotter, fpsaveout)`
6. Wrap `run()` body in `try/except Exception` with logging

### All disptest*.py scripts

Replace every direct `Threader.thread.attribute` read with getter calls:
- `CamThreader.thread.imageout` -> `CamThreader.thread.get_frame()`
- `SensorThreader.thread.pitch` -> via `SensorThreader.thread.get_orientation()`
- `BallisticThreader.thread.solution` -> via `BallisticThreader.thread.get_output()`
- `SensorThreader.thread.encoder1Output` -> via `SensorThreader.thread.get_encoders()`

**Note:** For writes TO threads (setting `ScopeMode`, `targetdistin`, etc.),
these are single-writer (main thread) so the risk is lower. Add lock protection
to setters in Phase 2b when the classes are consolidated.

### Hook step (final commit)

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

Commits:
1. `refactor(threads): add Lock and getters to CamThreader`
2. `refactor(sensor): add Lock, typed exceptions, logging to SensorThreader`
3. `refactor(ballistics): add Lock and getters to BallisticThreader variants`
4. `refactor(display): replace direct thread access with getters in disptest scripts`
5. `ci(hooks): add thread-access, bare-except, and profanity hooks`

---

## Phase 1c: Input Validation

**Branch:** `refactor/1c-input-validation` (branch from merged 1b)

**Files to modify:**

### Display/BallisticThreader4Printer.py (and both Laser variants)

Add `VALID_RANGES` dict and `clamp()` function (see Pattern 3 in SKILL.md).

In `run()`, before the GNU solver call (~line 527):
```python
if self.fps_box <= 0 or self.bc7_box <= 0:
    logger.warning("Invalid ballistic params: fps=%s bc=%s", self.fps_box, self.bc7_box)
    time.sleep(0.1)
    continue
```

### All disptest*.py scripts

In encoder-handling callbacks for settings menu, clamp values:
```python
BallisticThreader.thread.caliber = clamp(new_value, 'caliber')
```

**Commits:**
1. `safety(ballistics): add input validation with VALID_RANGES`
2. `safety(display): clamp settings menu values at boundary`

---

## Phase 2a: Configuration System

**Branch:** `refactor/2a-config-system`

**New file:** `Display/config.py` (see Pattern 4 in SKILL.md for full content)

**Migration logic** (add to `config.py`):

```python
import numpy as np

NPY_PATH = DISPLAY_DIR / "configData.npy"
FIELD_ORDER = [
    'caliber', 'bullet_weight_grain', 'g_model', 'bc', 'zero_distance',
    'muzzle_velocity', 'wind_speed', 'wind_direction', 'altitude',
    'pressure', 'temperature', 'humidity', 'focal_length',
]

def migrate_from_npy():
    if not NPY_PATH.exists():
        return None
    data = np.load(NPY_PATH)
    kwargs = {field: float(data[0, i]) for i, field in enumerate(FIELD_ORDER)}
    kwargs['bullet_weight_grain'] = int(kwargs['bullet_weight_grain'])
    kwargs['g_model'] = int(kwargs['g_model'])
    kwargs['muzzle_velocity'] = int(kwargs['muzzle_velocity'])
    kwargs['zero_distance'] = int(kwargs['zero_distance'])
    config = ScopeConfig(**kwargs)
    config.save()
    return config
```

**Files to modify:**

### All disptest*.py scripts (~lines 158-172)

Replace:
```python
Loaddata = load("/home/pi/share/Display/configData.npy")
BallisticThreader.thread.caliber = Loaddata[0,0]
# ... 12 more positional accesses ...
```

With:
```python
from config import ScopeConfig, migrate_from_npy, DISPLAY_DIR, ASSETS_DIR, LIB_DIR

cfg = ScopeConfig.load() or migrate_from_npy() or ScopeConfig()
BallisticThreader.thread.caliber = cfg.caliber
BallisticThreader.thread.bullet_weight_grain = cfg.bullet_weight_grain
# ... named field accesses ...
```

Replace save logic (~line 2330):
```python
cfg = ScopeConfig(caliber=BallisticThreader.thread.caliber, ...)
cfg.save()
```

### All hardcoded paths

Search for `/home/pi/share/Display/` and replace with `DISPLAY_DIR /` or
`ASSETS_DIR /` as appropriate. Key locations:

- `BallisticThreader*.py` line 35: `.CDLL("/home/pi/share/Display/GNUball3.so")`
  -> `.CDLL(str(LIB_DIR / "GNUball3.so"))`
- `disptest*.py` line 130: `Image.open("/home/pi/share/Display/LoadingScreen2.jpg")`
  -> `Image.open(str(ASSETS_DIR / "LoadingScreen2.jpg"))`
- Similar for COMPASS4.jpg, lobstermodebase2.jpg, SettingsMenuBase5.jpg, etc.

### Hook step (final commit)

Append to `.pre-commit-config.yaml`:
```yaml
      - id: no-hardcoded-paths
        name: Block hardcoded Pi paths
        entry: '/home/pi/share/'
        language: pygrep
        types_or: [python, shell]
```

---

## Phase 2b: Consolidate Threaders

**Branch:** `refactor/2b-consolidate-threaders`

**New file:** `Display/BallisticThreader.py`

Create single class with feature flags:
```python
class BallisticThread(Thread):
    def __init__(self, enable_printer=False, enable_laser=False, laser_precision=1):
```

Differences between old variants to parameterize:
- Printer init: gated by `enable_printer` flag
- Laser serial init: gated by `enable_laser` flag
- Laser rounding: `self.laser_precision` (1 for L variant, 10 for P variant)
- Branding: always "Jaccuracy Scope"

**Also consolidate:**
- `CamThreader.py` + `CamThreaderSLOWFPS.py` -> single `CamThreader.py`
  with `fps_mode` parameter ('fast' or 'slow')
- Rename `SensorThreaderSlowerRotaryEncodersTRY.py` -> `SensorThreader.py`

**Delete after consolidation:**
- `BallisticThreader4Printer.py`
- `BallisticThreader4PrinterAndLaserL.py`
- `BallisticThreader4PrinterAndLaserP.py`
- `CamThreaderSLOWFPS.py`
- `SensorThreaderSlowerRotaryEncodersTRY.py`

**Remove module-level thread start** from all threaders (see Pattern 5 in SKILL.md).

**Update all disptest*.py imports** to use new unified modules with feature flags.

---

## Phase 2c: Testing

**Branch:** `refactor/2c-testing`

**New files:**

### tests/test_ballistics.py

Test GNU solver against known .308 168gr SMK ballistic tables:
- 100 yards: near-zero drop (zeroed)
- 300 yards: ~12-15 MOA drop
- 500 yards: ~25-30 MOA drop
- 1000 yards: ~55-65 MOA drop

Load compiled `.so` via ctypes, call `SolveBallistic`, verify `HandMeMOA` outputs.

### tests/test_config.py

- Test `ScopeConfig.load()` with no file (returns defaults)
- Test `ScopeConfig.save()` and `load()` roundtrip
- Test `migrate_from_npy()` with a test `.npy` file
- Test validation `clamp()` at boundaries

### tests/test_data_plotter.py

- Test `elev2Y()` with known inch values
- Test `range2x()` with known yard values
- Test `trajPlotter()` returns correct shapes

### tests/test_sensor_math.py

- Test `convertToheading()` with known raw magnetometer values
- Test heading wraps correctly at 0/360 boundary

### requirements-dev.txt

```
pytest>=7.0
numpy>=1.26
pillow>=10.0
```

### Hook step (final commit)

Append pre-push hook to `.pre-commit-config.yaml`:
```yaml
      - id: run-tests
        name: Run pytest suite
        entry: bash -c 'python -m pytest tests/ -x -q'
        language: system
        stages: [pre-push]
        pass_filenames: false
```

Add CI test job to `.github/workflows/ci.yml`:
```yaml
  test:
    runs-on: ubuntu-latest
    needs: [lint, compile-c]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Compile C library
        run: cd Display/Balls && gcc -fPIC -shared -o GNUball3.so exportme3.c -lm
      - run: pip install pytest numpy pillow
      - run: python -m pytest tests/ -v
```

Remove `Display/disptest*.py` per-file-ignore from `.ruff.toml`.

---

## Phase 2d: API Documentation

**Branch:** `refactor/2d-api-docs`

Add docstrings and type hints to all public methods in:
- `BallisticThreader.py` (consolidated)
- `CamThreader.py` (consolidated)
- `SensorThreader.py` (renamed)
- `DisplayThreader.py`
- `DataPlotter.py`
- `config.py`

Create `Display/README.md` with architecture overview.
Create `Display/Balls/README.md` with C library API docs.

---

## Phase 3a: Image Performance

**Branch:** `refactor/3a-image-perf`

**File:** `Display/DataPlotter.py`

- Replace `draw2.point()` loops (lines 169-171, 185-189) with `ImageDraw.line()`
- Cache `Image.open()` calls in disptest scripts (compass, settings menu, loading screen)
- Use `Image.NEAREST` consistently for real-time compositing

---

## Phase 3b: GPIO Cleanup

**Branch:** `refactor/3b-gpio-cleanup`

**Files:** All disptest scripts

- Wrap main loop in `try/finally` with `GPIO.cleanup()`
- Add `signal.signal(signal.SIGTERM, handler)` for graceful shutdown
- Add `threading.Event` stop signals to all thread classes
- In each thread's `run()`: check `self._stop_event.is_set()` each iteration

---

## Phase 3c: Logging Framework

**Branch:** `refactor/3c-logging`

**New file:** `Display/logger.py`

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

---

## Phase 3d: Installation Modernization

**Branch:** `refactor/3d-install-modernize`

**Files to modify:** `jaccuracyinstall.sh`

**New files:**

### requirements.txt

```
picamera2
adafruit-circuitpython-lsm6ds
numpy==1.26.4
pillow
st7789
adafruit-circuitpython-thermal-printer
adafruit-circuitpython-seesaw
```

### Makefile

```makefile
.PHONY: compile test lint install

compile:
	cd Display/Balls && gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror

test:
	python -m pytest tests/ -v

lint:
	ruff check Display/

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	$(MAKE) compile
```

**Changes to jaccuracyinstall.sh:**

- Remove `rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED` (line 42)
- Replace with: `python3 -m venv /home/pi/share/venv`
- Auto-detect Python version: `PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")`
- Add `set -e` at top for error checking
- Replace individual `pip install` calls with `pip install -r requirements.txt`

---

## Tagging Convention

After merging each phase branch to main:

```bash
git tag v0.1-phase0    # After Phase 0
git tag v0.2-phase1    # After all of Phase 1 (1a + 1b + 1c)
git tag v0.3-phase2    # After all of Phase 2
git tag v0.4-phase3    # After all of Phase 3
```
