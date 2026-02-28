import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict

DISPLAY_DIR = Path(__file__).parent
CONFIG_PATH = DISPLAY_DIR / "config.json"
ASSETS_DIR = DISPLAY_DIR
LIB_DIR = DISPLAY_DIR / "Balls"

NPY_PATH = DISPLAY_DIR / "configData.npy"
FIELD_ORDER = [
    "caliber",
    "bullet_weight_grain",
    "g_model",
    "bc",
    "zero_distance",
    "muzzle_velocity",
    "wind_speed",
    "wind_direction",
    "altitude",
    "pressure",
    "temperature",
    "humidity",
    "focal_length",
]


@dataclass
class ScopeConfig:
    caliber: float = 0.308
    bullet_weight_grain: int = 150
    g_model: int = 7
    bc: float = 0.242
    zero_distance: int = 100
    muzzle_velocity: int = 2600
    wind_speed: float = 0.0
    wind_direction: float = 0.0
    altitude: float = 4000.0
    pressure: float = 29.53
    temperature: float = 59.0
    humidity: float = 0.30
    focal_length: float = 77.25
    scope_height: float = 1.75

    @classmethod
    def load(cls):
        if CONFIG_PATH.exists():
            return cls(**json.loads(CONFIG_PATH.read_text()))
        return None

    def save(self):
        CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2))


def migrate_from_npy():
    if not NPY_PATH.exists():
        return None
    data = np.load(NPY_PATH)
    kwargs = {field: float(data[0, i]) for i, field in enumerate(FIELD_ORDER)}
    kwargs["bullet_weight_grain"] = int(kwargs["bullet_weight_grain"])
    kwargs["g_model"] = int(kwargs["g_model"])
    kwargs["muzzle_velocity"] = int(kwargs["muzzle_velocity"])
    kwargs["zero_distance"] = int(kwargs["zero_distance"])
    config = ScopeConfig(**kwargs)
    config.save()
    return config
