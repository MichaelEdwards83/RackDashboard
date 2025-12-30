import random
import time
import os
from typing import List, Dict, Any
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
        self._last_readings_time = 0
        
        # Check if we are physically capable of 1-wire
        # (Very basic check, better to rely on config or import)
        if not HAS_W1 and not self.mock_mode:
            print("w1thermsensor not found, forcing Mock Mode")
            self.mock_mode = True

        if not self.mock_mode:
            self._init_real_sensors()

    def reload_config(self):
        new_mock = CONFIG.get("mock_mode")
        if self.mock_mode and not new_mock:
            # Switching from Mock -> Real
            print("Switching to Real Sensors...")
            self._init_real_sensors()
        
        self.mock_mode = new_mock

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
        
        # Continuous Scan Logic (Every 5 seconds)
        current_time = time.time()
        if not self.mock_mode and (current_time - self._last_readings_time > 5):
             try:
                 available = W1ThermSensor.get_available_sensors()
                 # Debug logging
                 if len(available) != len(self.sensors):
                     print(f"[DEBUG SCAN] Scan found {len(available)} sensors: {[s.id for s in available]}")
                 
                 self.sensors = available
                 self._last_readings_time = current_time
             except Exception as e:
                 print(f"[DEBUG SCAN] Scan Error: {e}")
                 pass # Ignore scan errors, keep old list
        
        if self.mock_mode:
            # ... (Mock logic - largely unchanged, but let's ensure it returns consistent order if we wanted)
            # Keeping existing mock logic simple for now, but wrapped in same structure would be ideal.
            # For brevity, let's keep the existing mock block implementation but note we are returning early.
            
            # [PASTED MOCK LOGIC - REUSING EXISTING CODE BLOCK]
            # Generate realistic fluctuating data
            bases = [22.0, 24.5, 28.0, 19.5, 31.0]
            
            for i in range(5):
                # Sine wave fluctuation + random noise
                variation = math.sin(current_time * 0.1 + i) * 0.5 + random.uniform(-0.1, 0.1)
                temp = bases[i] + variation
                
                # Convert to F if configured
                if CONFIG.get("temp_unit") == "F":
                    temp = (temp * 9/5) + 32
                    
                self._last_readings[i] = round(temp, 1)
                sensor_id = f"mock-{i+1}"
                
                sensor_name = CONFIG.get("sensor_names", {}).get(sensor_id, f"Probe {i+1}")
                
                readings.append({
                    "id": sensor_id,
                    "name": sensor_name,
                    "temp": self._last_readings[i],
                    "status": self._get_status(self._last_readings[i], sensor_id)
                })
            return readings

        else:
            # Real Hardware with Auto-Lock Ordering
            # 1. Get Configured Order
            order = CONFIG.get("sensor_order") or []
            
            # 2. Map Available Sensors by ID for quick lookup
            available_map = {s.id: s for s in self.sensors}
            
            # 3. Build Result List (Max 5 slots)
            final_slots = [None] * 5
            
            # 3a. Fill Locked Slots
            for i, locked_id in enumerate(order):
                if i >= 5: break
                if locked_id in available_map:
                    final_slots[i] = available_map.pop(locked_id)
                else:
                    # Sensor is locked to this slot but missing
                    final_slots[i] = "missing" # Placeholder marker

            # 3b. Fill Remaining Slots with New/Unassigned Sensors
            remaining_sensors = list(available_map.values())
            
            for i in range(5):
                if final_slots[i] is None:
                    if remaining_sensors:
                        final_slots[i] = remaining_sensors.pop(0)
                    else:
                        final_slots[i] = "empty"

            # 4. Process Readings and Update Config if Order Changed
            new_order = []
            order_changed = False
            
            for i, item in enumerate(final_slots):
                if isinstance(item, W1SensorType): # It's a real sensor object
                    # Read Temp
                    try:
                        temp = item.get_temperature()
                        if CONFIG.get("temp_unit") == "F":
                            temp = (temp * 9/5) + 32
                        temp = round(temp, 1)
                        status = self._get_status(temp, item.id)
                        
                        readings.append({
                            "id": item.id,
                            "name": CONFIG.get("sensor_names", {}).get(item.id, f"Probe {i+1}"),
                            "temp": temp,
                            "status": status
                        })
                        new_order.append(item.id)
                        
                    except Exception as e:
                        readings.append({
                            "id": item.id,
                            "name": CONFIG.get("sensor_names", {}).get(item.id, f"Probe {i+1}"),
                            "temp": 0.0,
                            "status": "error" # Reading error
                        })
                        new_order.append(item.id) # Keep it in order

                elif item == "missing":
                     # Was locked, but not found
                     miss_id = order[i]
                     readings.append({
                        "id": miss_id,
                        "name": CONFIG.get("sensor_names", {}).get(miss_id, f"Probe {i+1}"),
                        "temp": 0.0,
                        "status": "searching" # Specific status for UI
                    })
                     new_order.append(miss_id) # Keep locked ID
                     
                else: # "empty"
                     readings.append({
                        "id": f"empty-{i}",
                        "name": "Empty Slot",
                        "temp": 0.0,
                        "status": "empty"
                    })
                     # Don't add to order yet? Or placeholder? 
                     # If we don't add to order, this slot stays "floating". 
                     # Better to leave it out of 'new_order' so it can be filled later.
            
            # 5. Save Order if it grew (Smart Auto-Lock)
            # If we found new sensors that weren't in the original order, we should append them?
            # The 'new_order' list constructed above maintains the locked ones + new ones found in open slots.
            # We should only update config if it's different/longer.
            # Actually, to be robust: only Append. Never re-shuffle.
            
            current_config_order = CONFIG.get("sensor_order") or []
            if len(new_order) > len(current_config_order):
                # We found new stuff!
                # But wait, 'new_order' essentially IS the layout. 
                # Let's save it if it's "better" (more IDs) than before.
                
                # Careful: detection race condition could result in partial list saving.
                # Only save if we have MORE items, or if the original was empty.
                clean_order = [x for x in new_order if not x.startswith("empty-")]
                
                if len(clean_order) > len(current_config_order):
                    CONFIG.set("sensor_order", clean_order)
                    print(f"Auto-Locked new sensor order: {clean_order}")

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
