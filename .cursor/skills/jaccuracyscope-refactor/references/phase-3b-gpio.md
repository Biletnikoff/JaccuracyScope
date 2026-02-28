# Phase 3b: GPIO Cleanup

**Branch:** `refactor/3b-gpio-cleanup`

**Files:** All disptest scripts

- Wrap main loop in `try/finally` with `GPIO.cleanup()`
- Add `signal.signal(signal.SIGTERM, handler)` for graceful shutdown
- Add `threading.Event` stop signals to all thread classes
- In each thread's `run()`: check `self._stop_event.is_set()` each iteration

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
