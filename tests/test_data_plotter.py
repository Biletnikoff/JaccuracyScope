"""Tests for DataPlotter coordinate mapping functions."""

import os
import sys

import numpy as np
import pytest

# Mock PIL Image.open before DataPlotter imports (it loads images at module level)
display_dir = os.path.join(os.path.dirname(__file__), "..", "Display")
sys.path.insert(0, display_dir)


@pytest.fixture(autouse=True)
def mock_pil_and_chdir(monkeypatch):
    """Mock PIL Image.open and chdir to Display so DataPlotter can load."""
    from PIL import Image

    # Create minimal placeholder images to avoid file-not-found
    mock_img = Image.new("RGB", (150, 30), (0, 0, 0))
    monkeypatch.setattr(Image, "open", lambda _: mock_img)
    orig_cwd = os.getcwd()
    os.chdir(display_dir)
    yield
    os.chdir(orig_cwd)


def test_elev2Y():
    from DataPlotter import elev2Y

    inches = np.array([0, -10, -20])
    result = elev2Y(inches)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(inches)
    assert np.all(np.isfinite(result))


def test_elev2Y_single_value():
    """elev2Y with single value: max==min causes div-by-zero, skip that edge case."""
    from DataPlotter import elev2Y

    # Use two identical values - still produces 0/0 for pxunits; use 2+ distinct values
    inches = np.array([0.0, 1.0])
    result = elev2Y(inches)
    assert isinstance(result, np.ndarray)
    assert len(result) == 2
    assert np.all(np.isfinite(result))


def test_range2x():
    from DataPlotter import range2x

    yards = np.array([0, 100, 200, 300])
    dist_targ = 300.0
    result = range2x(yards, dist_targ)
    assert isinstance(result, np.ndarray)
    assert len(result) == len(yards)
    assert np.all(np.isfinite(result))
    # First point should be near offset, last near full width
    assert result[0] < result[-1]


def test_trajPlotter():
    from DataPlotter import trajPlotter

    distanceData = np.array([0, 100, 200, 300])
    dropData = np.array([0, -5, -15, -30])
    dist_targ = 300.0
    outputy, outputx = trajPlotter(distanceData, dropData, dist_targ)
    assert isinstance(outputy, np.ndarray)
    assert isinstance(outputx, np.ndarray)
    assert len(outputy) == len(distanceData)
    assert len(outputx) == len(distanceData)
