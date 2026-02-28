# Phase 3d: Installation Modernization

**Branch:** `refactor/3d-install-modernize`

**Files to modify:** `jaccuracyinstall.sh`

## New files

### requirements.txt

```
picamera2
adafruit-circuitpython-lsm6ds
numpy==1.26.4
pillow
st7789
adafruit-circuitpython-thermal-printer
adafruit-circuitpython-seesaw
```

### Makefile

```makefile
.PHONY: compile test lint install

compile:
	cd Display/Balls && gcc -fPIC -shared -o GNUball3.so exportme3.c -lm -Wall -Werror

test:
	python -m pytest tests/ -v

lint:
	ruff check Display/

install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	$(MAKE) compile
```

## Changes to jaccuracyinstall.sh

- Remove `rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED` (line 42)
- Replace with: `python3 -m venv /home/pi/share/venv`
- Auto-detect Python version: `PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")`
- Add `set -e` at top for error checking
- Replace individual `pip install` calls with `pip install -r requirements.txt`

## Tagging

After all Phase 3 branches merge:
```bash
git tag v0.4-phase3
```

## Verification

Run `bash .cursor/skills/jaccuracyscope-refactor/scripts/verify-phase.sh`
