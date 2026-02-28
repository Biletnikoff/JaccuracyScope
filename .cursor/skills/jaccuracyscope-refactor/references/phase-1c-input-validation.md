# Phase 1c: Input Validation

**Branch:** `refactor/1c-input-validation` (branch from merged 1b)

**Files to modify:**

## Display/BallisticThreader4Printer.py (and both Laser variants)

Add `VALID_RANGES` dict and `clamp()` function (see Pattern 3 in SKILL.md).

In `run()`, before the GNU solver call (~line 527):
```python
if self.fps_box <= 0 or self.bc7_box <= 0:
    logger.warning("Invalid ballistic params: fps=%s bc=%s", self.fps_box, self.bc7_box)
    time.sleep(0.1)
    continue
```

## All disptest*.py scripts

In encoder-handling callbacks for settings menu, clamp values:
```python
BallisticThreader.thread.caliber = clamp(new_value, 'caliber')
```

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`

**Commits:**
1. `safety(ballistics): add input validation with VALID_RANGES`
2. `safety(display): clamp settings menu values at boundary`
