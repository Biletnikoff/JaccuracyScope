# Display Module

## Architecture

The Display module implements a real-time ballistic scope overlay system for the Raspberry Pi. It composites live camera feed with a heads-up display (HUD) showing ballistic solutions, sensor data, and targeting information.

### Thread Architecture

All major subsystems run as daemon threads to maximize throughput on the Pi's limited CPU:

- **CamThreader**: Captures frames from Pi Camera via picamera2. Provides thread-safe frame access via `get_frame()` and FPS via `get_fps()`.
- **SensorThreader**: Reads IMU (ISM330DHCX) + magnetometer (MMC5983MA) + rotary encoders via I2C/SPI. Provides orientation, compass heading, and encoder positions via thread-safe getters.
- **BallisticThreader**: Solves bullet trajectory via the GNU Ballistics C library (ctypes FFI). Provides solution, plot data, and FPS via `get_output()`.
- **DisplayThreader**: Drives the ST7789 240x240 SPI LCD display.
- **DataPlotter**: Renders trajectory plots as PIL images for HUD overlay.

### Configuration

- **config.py**: JSON-based configuration with `ScopeConfig` dataclass. Supports migration from legacy `.npy` format.
- **config.json**: Persisted configuration file (auto-generated).

### Entry Points

- **disptest*.py**: Main loop scripts that composite camera + HUD overlay onto the display. Different variants support different hardware configurations (printer, laser rangefinder, etc.).

### C Library

The `Balls/` subdirectory contains the GNU Ballistics solver compiled as a shared library (`GNUball3.so`). See `Balls/README.md` for the C API documentation.

## Hardware Requirements

- Raspberry Pi (tested on Pi 4)
- Pi Camera Module (via picamera2)
- ST7789 240x240 SPI Display
- ISM330DHCX IMU (I2C)
- MMC5983MA Magnetometer (I2C)
- Rotary Encoders (GPIO)
- Optional: Thermal Printer, Laser Rangefinder
