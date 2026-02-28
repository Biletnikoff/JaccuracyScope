import json
from pathlib import Path
from dataclasses import dataclass, asdict

DISPLAY_DIR = Path(__file__).parent
CONFIG_PATH = DISPLAY_DIR / "config.json"
ASSETS_DIR = DISPLAY_DIR
LIB_DIR = DISPLAY_DIR / "Balls"


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
        return cls()

    def save(self):
        CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2))
