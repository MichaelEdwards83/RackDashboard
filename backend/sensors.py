import random
import time
import os
import glob
from typing import List, Dict, Any
from config import CONFIG

# Try to import w1thermsensor, fail gracefully if not on Pi/installed
try:
    from w1thermsensor import W1ThermSensor, Sensor as W1SensorType
    HAS_W1 = True
except Exception:
    # Catches ImportError AND w1thermsensor.errors.KernelModuleLoadError
    HAS_W1 = False
    W1SensorType = type(None) # Dummy for isinstance checks

# Native fallback class
class NativeW1Sensor:
    def __init__(self, sensor_id):
        self.id = sensor_id
        # Standard path
        self.path = f"/sys/bus/w1/devices/{sensor_id}/w1_slave"

    def get_temperature(self):
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
            
            if not lines:
                raise Exception("Empty file")
                
            # Line 1 check YES
            if "YES" not in lines[0]:
                raise Exception("CRC check failed")
                
            # Line 2 get t=
            pos = lines[1].find("t=")
            if pos != -1:
                temp_string = lines[1][pos+2:]
                val = float(temp_string) / 1000.0
                # Log occasional success to prove we are reading
                # (Comment out if too spammy, but vital for debug now)
                # with open("backend_debug.log", "a") as logf:
                #     logf.write(f"NATIVE READ {self.id}: {val}\n")
                return val
            else:
                raise Exception("Temp not found")
        except Exception as e:
            raise Exception(f"Native Read Error: {e}")

import threading

class SensorManager:
    def __init__(self):
        self.mock_mode = CONFIG.get("mock_mode")
        self.sensors = []
        self._last_readings = [0.0] * 5
        self._cached_readings = []
        self._cache_lock = threading.Lock()
        self.running = True
        
        # Check if we are physically capable of 1-wire
        sys_w1 = glob.glob("/sys/bus/w1/devices/28-*")
        
        if not HAS_W1 and not sys_w1 and not self.mock_mode:
            print("w1thermsensor not found AND no OS devices found. Forcing Mock Mode")
            self.mock_mode = True

        if not self.mock_mode:
            self._init_real_sensors()

        # Start Poll Loop
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()

    def reload_config(self):
        new_mock = CONFIG.get("mock_mode")
        if self.mock_mode and not new_mock:
            print("Switching to Real Sensors...")
            self._init_real_sensors()
        self.mock_mode = new_mock

    def _init_real_sensors(self):
        try:
            found_sensors = []
            try:
                found_sensors = W1ThermSensor.get_available_sensors()
            except Exception as e:
                print(f"Library scan failed: {e}. Trying manual fallback.")
            
            if not found_sensors:
                manual_paths = glob.glob("/sys/bus/w1/devices/28-*")
                if manual_paths:
                    print(f"Manual scan found {len(manual_paths)} sensors: {manual_paths}")
                    for path in manual_paths:
                        try:
                            sensor_id = os.path.basename(path)
                            found_sensors.append(NativeW1Sensor(sensor_id))
                        except Exception as e2:
                            print(f"Failed to load manual sensor {path}: {e2}")

            self.sensors = found_sensors[:5]
            if len(self.sensors) < 5:
                print(f"Warning: Only found {len(self.sensors)} sensors.")
        except Exception as e:
            print(f"Error initializing 1-wire sensors: {e}. Switching to Mock Mode.")
            self.mock_mode = True

    def _log_error(self, msg):
        try:
            with open("backend_debug.log", "a") as f:
                f.write(f"{time.ctime()}: {msg}\n")
        except: pass

    def get_temperatures(self) -> List[Dict[str, Any]]:
        with self._cache_lock:
            # Return copy of cache to prevent threading issues
            return list(self._cached_readings)

    def _poll_loop(self):
        while self.running:
            readings = []
            t_start = time.time()

            if self.mock_mode:
                # Mock Logic
                bases = [22.0, 24.5, 28.0, 19.5, 31.0]
                for i in range(5):
                    variation = math.sin(t_start * 0.1 + i) * 0.5 + random.uniform(-0.1, 0.1)
                    temp = bases[i] + variation
                    if CONFIG.get("temp_unit") == "F":
                        temp = (temp * 9/5) + 32
                    
                    sensor_id = f"mock-{i+1}"
                    readings.append({
                        "id": sensor_id,
                        "name": CONFIG.get("sensor_names", {}).get(sensor_id, f"Probe {i+1}"),
                        "temp": round(temp, 1),
                        "status": self._get_status(round(temp, 1), sensor_id)
                    })
            else:
                # Real Logic
                try:
                    # 1. Hardware Scan (Only every 30s to save IO, or if empty)
                    # For stability, let's keep the list static unless we specifically rescan
                    # But if we have 0 sensors, we should keep looking.
                    if not self.sensors:
                         self._init_real_sensors()

                    # 2. Prepare Slots
                    order = CONFIG.get("sensor_order") or []
                    available_map = {s.id: s for s in self.sensors}
                    final_slots = [None] * 5

                    for i, locked_id in enumerate(order):
                        if i >= 5: break
                        if locked_id in available_map:
                            final_slots[i] = available_map.pop(locked_id)
                        else:
                            final_slots[i] = "missing"

                    remaining_sensors = list(available_map.values())
                    for i in range(5):
                        if final_slots[i] is None:
                            if remaining_sensors:
                                final_slots[i] = remaining_sensors.pop(0)
                            else:
                                final_slots[i] = "empty"

                    # 3. Read Data
                    new_order = []
                    
                    for i, item in enumerate(final_slots):
                        if isinstance(item, (W1SensorType, NativeW1Sensor)):
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
                                self._log_error(f"Sensor Read Error ({item.id}): {e}")
                                readings.append({
                                    "id": item.id,
                                    "name": CONFIG.get("sensor_names", {}).get(item.id, f"Probe {i+1}"),
                                    "temp": 0.0,
                                    "status": "error"
                                })
                                new_order.append(item.id)

                        elif item == "missing":
                             miss_id = order[i]
                             readings.append({
                                "id": miss_id,
                                "name": CONFIG.get("sensor_names", {}).get(miss_id, f"Probe {i+1}"),
                                "temp": 0.0,
                                "status": "searching"
                            })
                             new_order.append(miss_id)
                        else:
                             readings.append({
                                "id": f"empty-{i}",
                                "name": "Empty Slot",
                                "temp": 0.0,
                                "status": "empty"
                            })

                    # 4. Auto-save Config Logic (Simplified)
                    # Only if we found significantly more unique real sensors
                    current_config = CONFIG.get("sensor_order") or []
                    real_sensors_found = [x for x in new_order if not x.startswith("empty-")]
                    if len(real_sensors_found) > len(current_config):
                         CONFIG.set("sensor_order", real_sensors_found)
                         print(f"Auto-Locked new sensor order: {real_sensors_found}")

                except Exception as e:
                    self._log_error(f"Poll Loop Error: {e}")
                    # Provide fallback or keep old readings?
                    # For now, just continue, preserving old cache if loop fails
                    pass

            # Update Cache
            if readings:
                with self._cache_lock:
                     self._cached_readings = readings

            # Sleep Remainder
            elapsed = time.time() - t_start
            sleep_time = max(1.0, 5.0 - elapsed) # Min 1s sleep, target 5s interval
            time.sleep(sleep_time)

    def _get_status(self, temp: float, sensor_id: str = None) -> str:
        thresholds = CONFIG.get_thresholds(sensor_id) if sensor_id else CONFIG.get("temp_thresholds")["global"]
        if temp >= thresholds["critical"]:
            return "critical"
        elif temp >= thresholds["warning"]:
            return "warning"
        else:
            return "normal"

import math # Ensure math is available
