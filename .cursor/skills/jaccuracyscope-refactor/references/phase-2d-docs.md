# Phase 2d: API Documentation

**Branch:** `refactor/2d-api-docs`

Add docstrings and type hints to all public methods in:
- `BallisticThreader.py` (consolidated)
- `CamThreader.py` (consolidated)
- `SensorThreader.py` (renamed)
- `DisplayThreader.py`
- `DataPlotter.py`
- `config.py`

Create `Display/README.md` with architecture overview:

```markdown
# Display Module

## Architecture

- **CamThreader**: Captures frames from Pi Camera via picamera2
- **SensorThreader**: Reads IMU (ISM330DHCX) + magnetometer (MMC5983) + rotary encoders via I2C
- **BallisticThreader**: Solves trajectory via GNU Ballistics C library (ctypes)
- **DisplayThreader**: Drives ST7789 240x240 SPI display
- **DataPlotter**: Renders trajectory plots as PIL images
- **config**: JSON-based configuration with migration from legacy .npy format
- **disptest*.py**: Main loop compositing camera + HUD overlay onto display
```

Create `Display/Balls/README.md` with C library API documentation
(document all functions from `ballistics.h`).

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
