# Phase 2b: Consolidate Threaders

**Branch:** `refactor/2b-consolidate-threaders`

## New file: Display/BallisticThreader.py

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

## Also consolidate

- `CamThreader.py` + `CamThreaderSLOWFPS.py` -> single `CamThreader.py`
  with `fps_mode` parameter ('fast' or 'slow')
- Rename `SensorThreaderSlowerRotaryEncodersTRY.py` -> `SensorThreader.py`

## Delete after consolidation

- `BallisticThreader4Printer.py`
- `BallisticThreader4PrinterAndLaserL.py`
- `BallisticThreader4PrinterAndLaserP.py`
- `CamThreaderSLOWFPS.py`
- `SensorThreaderSlowerRotaryEncodersTRY.py`

**Remove module-level thread start** from all threaders (see Pattern 5 in SKILL.md).

**Update all disptest*.py imports** to use new unified modules with feature flags.

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
