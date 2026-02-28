---
name: jaccuracyscope-refactor
description: >
  Use when continuing, executing, checking status, resuming, or reviewing the
  JaccuracyScope refactoring. Triggers on: "run refactor", "continue refactor",
  "next phase", "refactor status", "phase N", "execute round", "start refactoring",
  "resume refactoring", "what's left", "refactor progress".
  Handles phase execution, parallel agent coordination, branch management,
  hook progression, and code pattern enforcement across C and Python files.
  Do NOT use for general coding questions, new feature development, or tasks
  unrelated to the refactoring plan.
---

# JaccuracyScope Refactoring

## Autonomous Workflow

When this skill activates, execute the following procedure automatically.
Do not wait for additional user input between steps within a round.
Only pause for user confirmation between rounds.

1. Read the Phase Status table below.
2. Identify the next round to execute using the Execution Rounds table.
3. For each task in the round:
   a. Read the per-phase spec: `references/phase-{id}.md` (e.g. `phase-0-hooks.md`,
      `phase-1a-c-safety.md`). See the Phase File Map below.
   b. Create the git branch: `git checkout -b <branch-name> main`
   c. For Phase 0, copy files from `assets/` as described in the spec.
   d. Execute all changes described in the spec, following the Code Patterns below.
   e. Run verification: `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
      (add `--phase-2a` flag for Phase 2a and later).
   f. Add the hook step (if any) as a final commit.
   g. Commit all changes using conventional commit format.
4. If the round has parallel tasks (marked `||`), launch them as
   simultaneous Task agents. Include in each agent's prompt:
   - The branch name
   - The full phase spec (copy from the per-phase reference file)
   - The relevant Code Patterns section(s)
   - The verification script path and command
5. After all tasks in the round complete, update the Phase Status table
   in this file, marking completed phases as `complete`.
6. Tell the user what was completed, show any warnings, and ask:
   "Ready to proceed to Round N+1?"
7. On confirmation, repeat from step 1.

If the user says "run everything" or "full auto", execute all rounds
sequentially without pausing between them (still pause on errors).

## Phase File Map

| Phase | Reference file |
|-------|---------------|
| 0 | `references/phase-0-hooks.md` |
| 1a | `references/phase-1a-c-safety.md` |
| 1b | `references/phase-1b-thread-robustness.md` |
| 1c | `references/phase-1c-input-validation.md` |
| 2a | `references/phase-2a-config.md` |
| 2b | `references/phase-2b-consolidate.md` |
| 2c | `references/phase-2c-testing.md` |
| 2d | `references/phase-2d-docs.md` |
| 3a | `references/phase-3a-image-perf.md` |
| 3b | `references/phase-3b-gpio.md` |
| 3c | `references/phase-3c-logging.md` |
| 3d | `references/phase-3d-install.md` |

## Phase Status

Update this table as phases complete.

| Phase | Task | Branch | Status |
|-------|------|--------|--------|
| 0 | Hooks infrastructure | `refactor/0-hooks-infrastructure` | complete |
| 1a | C library safety | `refactor/1a-c-library-safety` | complete |
| 1b | Thread robustness | `refactor/1b-thread-robustness` | complete |
| 1c | Input validation | `refactor/1c-input-validation` | complete |
| 2a | Config system | `refactor/2a-config-system` | complete |
| 2b | Consolidate threaders | `refactor/2b-consolidate-threaders` | complete |
| 2c | Testing | `refactor/2c-testing` | complete |
| 2d | API docs | `refactor/2d-api-docs` | complete |
| 3a | Image performance | `refactor/3a-image-perf` | complete |
| 3b | GPIO cleanup | `refactor/3b-gpio-cleanup` | complete |
| 3c | Logging framework | `refactor/3c-logging` | complete |
| 3d | Install modernization | `refactor/3d-install-modernize` | complete |

## Prerequisites (dependency map)

- Phase 1a/1b require Phase 0 complete
- Phase 1c requires Phase 1b complete
- Phase 2a requires Phase 1c complete
- Phase 2b requires Phase 2a complete
- Phase 2c requires Phase 1a and Phase 2b complete
- Phase 2d has no dependencies beyond Phase 1
- Phase 3 requires all of Phase 2 complete

## Execution Rounds

Execute rounds in order. Tasks in the same round marked `||` run in parallel.

| Round | Tasks | Mode | Agent A files | Agent B/C/D files |
|-------|-------|------|---------------|-------------------|
| 0 | Phase 0 | single | new: `.pre-commit-config.yaml`, `.ruff.toml`, `.github/workflows/ci.yml` | -- |
| 1 | 1a `\|\|` 1b | 2 parallel | `Display/Balls/*.c`, `Display/Balls/*.h` | `Display/*.py`, `Display/disptest*.py` |
| 2 | 1c | single | `Display/BallisticThreader*.py`, `Display/disptest*.py` | -- |
| 3 | 2a `\|\|` 2d | 2 parallel | `Display/config.py` (new), `Display/disptest*.py` | `Display/README.md` (new), `Display/Balls/README.md` (new) |
| 4 | 2b | single | `Display/BallisticThreader.py` (new), `Display/CamThreader.py`, `Display/SensorThreader.py` (rename) | -- |
| 5 | 2c | single | `tests/` (new), `requirements-dev.txt` (new) | -- |
| 6 | 3a `\|\|` 3b `\|\|` 3c `\|\|` 3d | 4 parallel | 3a: `DataPlotter.py` / 3b: disptest entry/exit / 3c: `logger.py` (new) / 3d: `jaccuracyinstall.sh`, `Makefile` (new) | -- |

Parallel agents must never edit the same file. The file ownership column enforces this.

## Subagent Prompt Template

When launching a parallel Task agent, copy this template and fill in the blanks:

```
You are executing Phase {PHASE_ID} of the JaccuracyScope refactoring.

BRANCH: Create and work on `{BRANCH_NAME}` based on `main`.

FILES YOU OWN (only edit these):
{FILE_LIST from phase-specs.md}

CHANGES TO MAKE:
{PASTE the full contents of references/phase-{id}.md}

CODE PATTERNS TO FOLLOW:
{PASTE the relevant Pattern(s) from SKILL.md}

ASSET FILES TO COPY (if Phase 0):
{List any files from assets/ to copy, or "None"}

HOOK STEP (final commit, if applicable):
{PASTE hook details or "None for this phase"}

COMMIT FORMAT: type(scope): description
Allowed types: feat, fix, refactor, docs, test, chore, ci, perf, safety

VERIFICATION (run before committing):
bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh
(add --phase-2a flag for Phase 2a and later)

ERROR RECOVERY:
- If verification fails, fix the issue and re-run. Do NOT skip verification.
- If a C compilation fails, read the error output carefully -- common issues
  are missing semicolons after added guard clauses.
- If ruff reports errors, run `ruff check --fix <file>` for auto-fixable ones.
- If a git conflict occurs during branch creation, ensure you are branching
  from an up-to-date `main`.

After completing all changes, report: files modified, commits made, any warnings.
```

## Code Patterns

All agents must follow these exact patterns. Do not deviate.

### Pattern 1: Thread Locking (Phase 1b)

```python
from threading import Thread, Lock

class SomeThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._lock = Lock()
        # ... existing init code ...

    def get_output(self):
        with self._lock:
            return (self.solution, self.plotter, self.fpsaveout)

    def run(self):
        while True:
            # ... compute ...
            with self._lock:
                self.solution = result
                self.plotter = plot
                self.fpsaveout = fpsave
```

Callers use `get_output()` instead of direct attribute access:

```python
# BEFORE (forbidden after Phase 1b):
sol = BallisticThreader.thread.solution

# AFTER (required):
sol, plot, fps = BallisticThreader.thread.get_output()
```

### Pattern 2: Error Handling (Phase 1b)

```python
import logging

logger = logging.getLogger(__name__)

# Specific exception types, never bare except
try:
    self.data = self.mmc.read_data()
except OSError as e:
    logger.warning("Magnetometer read failed: %s", e, exc_info=True)
    # Use last good data or default
except Exception:
    logger.exception("Unexpected error in sensor read")
    raise
```

For transient I2C failures, retry up to 3 times:

```python
for attempt in range(3):
    try:
        value = self.accSensor.acceleration[0]
        break
    except OSError:
        if attempt == 2:
            logger.error("I2C read failed after 3 attempts")
            value = 0
        time.sleep(0.01 * (2 ** attempt))
```

Wrap every `run()` method to prevent silent thread death:

```python
def run(self):
    try:
        self._run_loop()
    except Exception:
        logger.exception("Thread %s died unexpectedly", self.__class__.__name__)
```

### Pattern 3: Input Validation (Phase 1c)

```python
VALID_RANGES = {
    'caliber': (0.17, 1.0),
    'bullet_weight_grain': (10, 1000),
    'bc7_box': (0.01, 1.5),
    'fps_box': (100, 5000),
    'Atm_altitude': (-1000, 50000),
    'Atm_pressure': (20.0, 35.0),
    'Atm_temperature': (-60, 140),
    'Atm_RelHumidity': (0.0, 1.0),
    'zerodistance': (10, 2000),
    'windspeed': (0, 100),
}

def clamp(value, key):
    lo, hi = VALID_RANGES[key]
    return max(lo, min(hi, value))
```

### Pattern 4: Configuration (Phase 2a)

```python
import json
from pathlib import Path
from dataclasses import dataclass, asdict

DISPLAY_DIR = Path(__file__).parent
CONFIG_PATH = DISPLAY_DIR / "config.json"
ASSETS_DIR = DISPLAY_DIR
LIB_DIR = DISPLAY_DIR / "Balls"

@dataclass
class ScopeConfig:
    caliber: float = 0.308
    bullet_weight_grain: int = 150
    g_model: int = 7
    bc: float = 0.242
    zero_distance: int = 100
    muzzle_velocity: int = 2600
    wind_speed: float = 0.0
    wind_direction: float = 0.0
    altitude: float = 4000.0
    pressure: float = 29.53
    temperature: float = 59.0
    humidity: float = 0.30
    focal_length: float = 77.25
    scope_height: float = 1.75

    @classmethod
    def load(cls):
        if CONFIG_PATH.exists():
            return cls(**json.loads(CONFIG_PATH.read_text()))
        return cls()

    def save(self):
        CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2))
```

Replace all `/home/pi/share/Display/` with `DISPLAY_DIR /` or `ASSETS_DIR /`.

### Pattern 5: Threader Consolidation (Phase 2b)

Stop starting threads at module import time. Export the class only:

```python
# BEFORE (forbidden after Phase 2b):
thread = BallisticThread()
thread.start()

# AFTER (required):
# In BallisticThreader.py -- just define the class, nothing at module level.
# In disptest:
from BallisticThreader import BallisticThread
bt = BallisticThread(enable_printer=True, enable_laser=True, laser_precision=10)
bt.daemon = True
bt.start()
```

### Pattern 6: Conventional Commits

```
safety(ballistics): add NULL checks to C solver retrieve functions
refactor(threads): add Lock to BallisticThread shared state
fix(sensor): replace bare except with specific OSError handling
ci(hooks): add bare-except blocker to pre-commit config
docs(display): add architecture README for Display module
```

## Hook Management

Each phase may add hooks. Always append as the **final commit** of the branch.

Procedure:
1. Complete all code changes for the phase
2. Verify code changes work (compile C, run linter)
3. Append new hook block to `.pre-commit-config.yaml`
4. Commit: `ci(hooks): add <hook-name> from phase <id>`

Hook assignments by phase (see `references/phase-specs.md` for full YAML):

| Phase | Hook(s) Added |
|-------|---------------|
| 0 | Ruff, large-file, trailing-whitespace, conventional-commits |
| 1a | Promote CI to `-Wall -Werror` |
| 1b | `no-direct-thread-access`, `no-bare-except`, `no-profanity`; expand Ruff rules |
| 2a | `no-hardcoded-paths` |
| 2c | `run-tests` (pre-push stage) |

## Branch and Merge Protocol

1. Branch from `main` (or from the phase branch if sub-branching)
2. Make changes following the patterns above
3. Add hook step as final commit (if applicable)
4. Commit using conventional commit format
5. Push and create PR: `gh pr create --title "type(scope): summary"`
6. After merge, tag if it completes a phase: `v0.N-phaseX`
7. Update the status table at the top of this file

## Error Recovery

If something goes wrong during execution:

1. **Verification script fails**: Read the output to identify which check failed.
   Fix the specific issue, re-run the script. Do NOT skip or comment out checks.
2. **C compilation error**: Usually a missing semicolon or misplaced brace from
   added guard clauses. Read `gcc` output line-by-line, fix, recompile.
3. **Ruff lint error**: Run `ruff check --fix <file>` for auto-fixable issues.
   For non-auto-fixable ones, read the error code and fix manually.
4. **Git branch conflict**: Ensure `main` is up to date (`git pull origin main`),
   then retry `git checkout -b <branch> main`.
5. **Parallel agent file conflict**: If two agents accidentally edit the same file,
   discard one agent's work on that file and redo from the file-ownership table.
6. **pre-commit hook failure on commit**: Fix the violation the hook reports, stage
   the fix, and commit again. Never use `--no-verify`.
7. **Thread deadlock introduced**: Check that no lock is held across a blocking call.
   Locks must protect only short, non-blocking reads/writes.

## Verification Checklist

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
(add `--phase-2a` for Phase 2a and later) before marking any phase complete.

Additionally confirm:

- [ ] All new hooks pass: `pre-commit run --all-files` (if hooks changed)
- [ ] Status table updated in this file

## Additional Resources

- **Per-phase specs**: `references/phase-{id}.md` -- see Phase File Map above
- **Legacy combined spec**: `references/phase-specs.md` (kept for reference)
- **Copy-ready templates**: `assets/` -- config files, CI workflow, linter config
- **Verification script**: `scripts/verify-phase.sh` -- deterministic pass/fail checks
