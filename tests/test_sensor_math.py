"""Tests for SensorThreader heading calculation."""

import math
import os
import sys
import types

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Display"))


@pytest.fixture
def sensor_with_known_calibration():
    """Create a minimal object with convertToheading bound and known calibration."""
    try:
        from SensorThreader import SensorThread
    except ImportError:
        pytest.skip("SensorThreader dependencies (board, etc.) not available")

    # Create object with calibration attrs without running SensorThread.__init__
    class MinimalSensor:
        xoffset = 371.0
        yoffset = -2326.5
        zoffset = -117.50
        xscale = 7808.0
        yscale = 7643.50
        zscale = 7807.50
        declinationAngle = 10 - 7.85 - 3  # -0.85

    obj = MinimalSensor()
    obj.convertToheading = types.MethodType(SensorThread.convertToheading, obj)
    return obj


def test_heading_in_range(sensor_with_known_calibration):
    """Heading should be in [0, 360) for any valid input."""
    sensor = sensor_with_known_calibration
    heading = sensor.convertToheading(0, 0, 0)
    assert 0 <= heading < 360


def test_heading_deterministic(sensor_with_known_calibration):
    """Same inputs should produce same heading."""
    sensor = sensor_with_known_calibration
    h1 = sensor.convertToheading(100, 200, 50)
    h2 = sensor.convertToheading(100, 200, 50)
    assert h1 == h2


def test_heading_formula_consistency(sensor_with_known_calibration):
    """Verify the atan2-based formula produces valid degrees."""
    sensor = sensor_with_known_calibration
    # Use raw values that normalize to known direction
    raw_x, raw_y, raw_z = 371.0, -2326.5, -117.5  # Normalized to (0,0,0) -> atan2 edge case
    heading = sensor.convertToheading(raw_x, raw_y, raw_z)
    assert 0 <= heading < 360
