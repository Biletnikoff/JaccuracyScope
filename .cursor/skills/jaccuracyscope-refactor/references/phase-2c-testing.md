# Phase 2c: Testing

**Branch:** `refactor/2c-testing`

## New files

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

## Verification

```bash
python -m pytest tests/ -v
```

Then run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`

## Hook step (final commit)

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
