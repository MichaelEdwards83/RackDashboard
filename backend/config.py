import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "temp_unit": "F",
    "temp_thresholds": {
        "global": {
            "warning": 80.0,
            "critical": 90.0
        },
        "sensors": {}  # Format: "sensor_id": {"warning": 80.0, "critical": 90.0}
    },
    "sensor_names": {}, # Format: "sensor_id": "Custom Name"
    "ntp_server": "pool.ntp.org",
    "location": {
        "auto": True,
        "latitude": 0.0,
        "longitude": 0.0,
        "name": "Unknown"
    },
    "mock_mode": False,
    "sensor_order": []
}

class ConfigManager:
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f)
                    self._recursive_update(self._config, saved)
            except Exception as e:
                print(f"Error loading config: {e}")

    def _recursive_update(self, base: Dict, update: Dict):
        for k, v in update.items():
            if isinstance(v, dict) and k in base:
                self._recursive_update(base[k], v)
            else:
                base[k] = v

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        self._config[key] = value
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return self._config

    def update_all(self, new_config: Dict[str, Any]):
        self._recursive_update(self._config, new_config)
        self.save()

    def get_thresholds(self, sensor_id: str) -> Dict[str, float]:
        """Get thresholds for a specific sensor, falling back to global if not set."""
        base = self._config["temp_thresholds"]
        
        # Check specific sensor overrides
        if sensor_id in base["sensors"]:
            return base["sensors"][sensor_id]
        
        # Fallback to global
        return base["global"]

CONFIG = ConfigManager()
