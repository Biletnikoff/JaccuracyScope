"""Tests for the C GNU ballistic solver via ctypes."""

import ctypes
import os
import subprocess
import pytest

BALLS_DIR = os.path.join(os.path.dirname(__file__), "..", "Display", "Balls")
SO_PATH = os.path.join(BALLS_DIR, "GNUball3.so")


@pytest.fixture(scope="session", autouse=True)
def compile_lib():
    """Compile the C library if the .so doesn't exist or fails to load (wrong arch)."""
    need_compile = not os.path.exists(SO_PATH)
    if not need_compile:
        try:
            ctypes.CDLL(SO_PATH)
        except OSError:
            need_compile = True
            os.remove(SO_PATH)
    if need_compile:
        subprocess.run(
            ["gcc", "-fPIC", "-shared", "-o", "GNUball3.so", "exportme3.c", "-lm"],
            cwd=BALLS_DIR,
            check=True,
        )


def load_lib():
    lib = ctypes.CDLL(SO_PATH)
    lib.SolveBallistic.restype = ctypes.c_double
    lib.SolveBallistic.argtypes = [
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
    ]
    lib.free_pointer.restype = ctypes.c_int
    lib.free_pointer.argtypes = [ctypes.c_int]
    return lib


# .308 168gr SMK, G7 BC=0.242, 2600fps, 100yd zero
# Standard atmosphere: 59°F, 29.53 inHg, 0% humidity, sea level


def test_100yd_zero():
    lib = load_lib()
    moa = lib.SolveBallistic(
        0.242, 2600, 1.75, 0, 100, 0, 0, 7, 0, 100, 0, 0, 29.53, 59, 0
    )
    lib.free_pointer(1)
    # With zeroanglein=0, solver returns drop MOA; at 100yd zero expect small value
    assert abs(moa) < 10.0


def test_300yd_drop():
    lib = load_lib()
    moa = lib.SolveBallistic(
        0.242, 2600, 1.75, 0, 100, 0, 0, 7, 0, 300, 0, 0, 29.53, 59, 0
    )
    lib.free_pointer(1)
    assert 3.0 < abs(moa) < 20.0  # Reasonable MOA at 300yd


def test_1000yd_drop():
    lib = load_lib()
    moa = lib.SolveBallistic(
        0.242, 2600, 1.75, 0, 100, 0, 0, 7, 0, 1000, 0, 0, 29.53, 59, 0
    )
    lib.free_pointer(1)
    assert 20.0 < abs(moa) < 80.0  # Reasonable MOA at 1000yd
