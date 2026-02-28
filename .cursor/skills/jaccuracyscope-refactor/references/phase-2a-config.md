# Phase 2a: Configuration System

**Branch:** `refactor/2a-config-system`

## New file: Display/config.py

Copy `assets/config-template.py` to `Display/config.py`, then add migration logic:

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

## All disptest*.py scripts (~lines 158-172)

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

## All hardcoded paths

Search for `/home/pi/share/Display/` and replace with `DISPLAY_DIR /` or
`ASSETS_DIR /` as appropriate. Key locations:

- `BallisticThreader*.py` line 35: `.CDLL("/home/pi/share/Display/GNUball3.so")`
  -> `.CDLL(str(LIB_DIR / "GNUball3.so"))`
- `disptest*.py` line 130: `Image.open("/home/pi/share/Display/LoadingScreen2.jpg")`
  -> `Image.open(str(ASSETS_DIR / "LoadingScreen2.jpg"))`
- Similar for COMPASS4.jpg, lobstermodebase2.jpg, SettingsMenuBase5.jpg, etc.

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh --phase-2a`

## Hook step (final commit)

Append to `.pre-commit-config.yaml`:
```yaml
      - id: no-hardcoded-paths
        name: Block hardcoded Pi paths
        entry: '/home/pi/share/'
        language: pygrep
        types_or: [python, shell]
```
