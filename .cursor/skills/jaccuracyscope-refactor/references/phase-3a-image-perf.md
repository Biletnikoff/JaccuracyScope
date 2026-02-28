# Phase 3a: Image Performance

**Branch:** `refactor/3a-image-perf`

**File:** `Display/DataPlotter.py`

- Replace `draw2.point()` loops (lines 169-171, 185-189) with `ImageDraw.line()`
- Cache `Image.open()` calls in disptest scripts (compass, settings menu, loading screen)
- Use `Image.NEAREST` consistently for real-time compositing

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
