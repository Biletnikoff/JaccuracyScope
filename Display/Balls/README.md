# Ballistics C Library

GNU Ballistics solver compiled as a shared library for Python ctypes integration.

## Building

```bash
cd Display/Balls
gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror
```

## API (exportme3.c)

### `double SolveBallistic(double bc, double v, double sh, double angle, double zero, double windspeed, double windangle, int G, double zeroanglein, double targetDistance, int justangle, double altitude, double pressure, double temperature, double relHum)`

Main entry point. Solves the ballistic trajectory and returns the MOA correction at the target distance.

**Parameters:**
- `bc` - Ballistic coefficient
- `v` - Muzzle velocity (fps)
- `sh` - Scope height above bore (inches)
- `angle` - Shooting angle (degrees)
- `zero` - Zero range (yards)
- `windspeed` - Wind speed (mph)
- `windangle` - Wind angle (degrees, 0 = headwind)
- `G` - Drag model (1 = G1, 7 = G7)
- `zeroanglein` - Pre-computed zero angle (0 to auto-calculate)
- `targetDistance` - Target distance (yards)
- `justangle` - If 1, only compute zero angle
- `altitude` - Altitude (feet)
- `pressure` - Barometric pressure (inHg)
- `temperature` - Temperature (°F)
- `relHum` - Relative humidity (0.0-1.0)

**Returns:** MOA correction at target distance, or zero angle if `justangle == 1`.

### Retrieve Functions

After calling `SolveBallistic`, these functions retrieve data at a given yardage (uses internal solution pointer):

- `HandMeXdistance(int yardage)` - Range in yards (wraps `GetRange`)
- `HandMeYdistance(int yardage)` - Bullet path (inches) (wraps `GetPath`)
- `HandMeMOA(int yardage)` - MOA correction (wraps `GetMOA`)
- `HandMeTime(int yardage)` - Time of flight (seconds) (wraps `GetTime`)
- `HandMeWindage(int yardage)` - Wind drift (inches) (wraps `GetWindage`)
- `HandMeWindageMOA(int yardage)` - Wind drift (MOA) (wraps `GetWindageMOA`)
- `HandMeVelocity(int yardage)` - Velocity (fps) (wraps `GetVelocity`)

The underlying `GetRange`, `GetPath`, `GetMOA`, etc. (in `_retrieve.c`) return 0 if solution is NULL or yardage is negative.

### `int free_pointer(int hi)`

Frees the solution memory. Must be called after retrieving all needed data. The `hi` parameter is unused.

## Source Files

- `exportme3.c` - Main entry point and retrieve functions (compiled to .so)
- `_solve.c` - Core trajectory solver (included by exportme3.c via ballistics.h)
- `_retrieve.c` - Data retrieval functions (included by ballistics.h)
- `ballistics.h` - Header with drag model tables and includes
- `example2.c`, `example3_addingPlotter.c` - Development examples
