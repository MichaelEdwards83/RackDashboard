import random
import time
import os
from typing import List, Dict
from config import CONFIG

# Try to import w1thermsensor, fail gracefully if not on Pi/installed
try:
    from w1thermsensor import W1ThermSensor, Sensor as W1SensorType
    HAS_W1 = True
except Exception:
    # Catches ImportError AND w1thermsensor.errors.KernelModuleLoadError
    HAS_W1 = False

class SensorManager:
    def __init__(self):
        self.mock_mode = CONFIG.get("mock_mode")
        self.sensors = []
        self._last_readings = [0.0] * 5
        
        # Check if we are physically capable of 1-wire
        # (Very basic check, better to rely on config or import)
        if not HAS_W1 and not self.mock_mode:
            print("w1thermsensor not found, forcing Mock Mode")
            self.mock_mode = True

        if not self.mock_mode:
            self._init_real_sensors()

    def _init_real_sensors(self):
        try:
            # Discover available sensors
            # In a real deployment, we might want to map specific IDs to specific slots
            # For now, we just take the first 5 found
            found_sensors = W1ThermSensor.get_available_sensors()
            self.sensors = found_sensors[:5]
            if len(self.sensors) < 5:
                print(f"Warning: Only found {len(self.sensors)} sensors. Filling rest with placeholders/mock.")
        except Exception as e:
            print(f"Error initializing 1-wire sensors: {e}. Switching to Mock Mode.")
            self.mock_mode = True

    def get_temperatures(self) -> List[Dict[str, Any]]:
        readings = []
        
        if self.mock_mode:
            # Generate realistic fluctuating data
            # Base temps slightly different for each "probe"
            bases = [22.0, 24.5, 28.0, 19.5, 31.0]
            current_time = time.time()
            
            for i in range(5):
                # Sine wave fluctuation + random noise
                variation = math.sin(current_time * 0.1 + i) * 0.5 + random.uniform(-0.1, 0.1)
                temp = bases[i] + variation
                
                # Convert to F if configured
                if CONFIG.get("temp_unit") == "F":
                    temp = (temp * 9/5) + 32
                    
                self._last_readings[i] = round(temp, 1)
                sensor_id = f"mock-{i+1}"
                
                # Get custom name or default
                sensor_name = CONFIG.get("sensor_names", {}).get(sensor_id, f"Probe {i+1}")
                
                readings.append({
                    "id": sensor_id,
                    "name": sensor_name,
                    "temp": self._last_readings[i],
                    "status": self._get_status(self._last_readings[i], sensor_id)
                })
        else:
            # Real hardware reading
            for i in range(5):
                if i < len(self.sensors):
                    try:
                        temp = self.sensors[i].get_temperature()
                        
                        # Convert to F if configured
                        if CONFIG.get("temp_unit") == "F":
                            temp = (temp * 9/5) + 32

                        self._last_readings[i] = round(temp, 1)
                        
                        # Get custom name or default
                        sensor_name = CONFIG.get("sensor_names", {}).get(self.sensors[i].id, f"Probe {i+1}")

                        readings.append({
                            "id": self.sensors[i].id,
                            "name": sensor_name,
                            "temp": self._last_readings[i],
                            "status": self._get_status(self._last_readings[i], self.sensors[i].id)
                        })
                    except Exception as e:
                        print(f"Error reading sensor {i}: {e}")
                        readings.append({
                            "id": "error",
                            "name": f"Probe {i+1}",
                            "temp": 0.0,
                            "status": "error"
                        })
                else:
                # Missing sensor slot
                     readings.append({
                        "id": "missing",
                        "name": f"Probe {i+1}",
                        "temp": 0.0,
                        "status": "missing"
                    })
        
        return readings

    def _get_status(self, temp: float, sensor_id: str = None) -> str:
        # Pass sensor_id if we have it, otherwise only global applies (which config handles gracefully if id not found, but we should pass it)
        # However, mock sensors have IDs too.
        
        thresholds = CONFIG.get_thresholds(sensor_id) if sensor_id else CONFIG.get("temp_thresholds")["global"]
        
        if temp >= thresholds["critical"]:
            return "critical"
        elif temp >= thresholds["warning"]:
            return "warning"
        else:
            return "normal"

import math # Missing import added for mock logic
