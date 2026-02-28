"""Tests for ScopeConfig and clamp boundaries."""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Display"))


def test_scope_config_defaults():
    from config import ScopeConfig

    cfg = ScopeConfig()
    assert cfg.caliber == 0.308
    assert cfg.muzzle_velocity == 2600


def test_scope_config_roundtrip(tmp_path, monkeypatch):
    import config

    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "config.json")
    from config import ScopeConfig

    cfg = ScopeConfig(caliber=0.223, muzzle_velocity=3200)
    cfg.save()
    loaded = ScopeConfig.load()
    assert loaded is not None
    assert loaded.caliber == 0.223
    assert loaded.muzzle_velocity == 3200


def test_clamp_boundaries(monkeypatch):
    """Test clamp using VALID_RANGES - mock deps to avoid serial/adafruit/images."""
    import sys
    from unittest.mock import MagicMock

    from PIL import Image

    mock_img = Image.new("RGB", (150, 30), (0, 0, 0))
    monkeypatch.setattr(Image, "open", lambda _: mock_img)
    for mod in ["serial", "adafruit_thermal_printer"]:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()
    try:
        from BallisticThreader import clamp
    finally:
        for mod in ["serial", "adafruit_thermal_printer"]:
            sys.modules.pop(mod, None)
    assert clamp(0.1, "caliber") == 0.17  # Below min
    assert clamp(2.0, "caliber") == 1.0  # Above max
    assert clamp(0.308, "caliber") == 0.308  # In range
