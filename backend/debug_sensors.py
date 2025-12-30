import glob
import os
import sys

print("--- 1-Wire Sensor Diagnostic Tool ---")

# 1. Check OS Level
print("\n[1] Checking /sys/bus/w1/devices/...")
sys_paths = glob.glob("/sys/bus/w1/devices/28-*")
if not sys_paths:
    print("    FAIL: No devices found in filesystem (ls /sys/bus/w1/devices/).")
    print("    Check wiring and config.txt (dtoverlay=w1-gpio).")
else:
    print(f"    SUCCESS: Found {len(sys_paths)} devices in OS:")
    for p in sys_paths:
        print(f"      -> {p}")

# 2. Check Library
print("\n[2] Checking w1thermsensor Library...")
try:
    from w1thermsensor import W1ThermSensor, Sensor
    print("    Library imported successfully.")
    
    available = W1ThermSensor.get_available_sensors()
    print(f"    Library.get_available_sensors() found: {len(available)}")
    
    for s in available:
        try:
            t = s.get_temperature()
            print(f"      -> ID: {s.id} | Temp: {t}°C")
        except Exception as e:
             print(f"      -> ID: {s.id} | Error reading: {e}")

except ImportError:
    print("    ERROR: w1thermsensor module not installed.")
except Exception as e:
    print(f"    CRITICAL LIBRARY ERROR: {e}")

# 3. Manual Fallback Test
print("\n[3] Testing Manual Fallback Logic...")
manual_sensors = []
if sys_paths:
    for path in sys_paths:
        try:
            sid = os.path.basename(path)
            # Try to force instantiate
            # Note: W1ThermSensor constructor might differ by version, trying standard
            # W1ThermSensor(sensor_type, sensor_id)
            s = W1ThermSensor(Sensor.DS18B20, sid)
            reading = s.get_temperature()
            print(f"    Manual Init {sid}: Success ({reading}°C)")
            manual_sensors.append(s)
        except Exception as e:
            print(f"    Manual Init {sid}: Failed ({e})")
else:
    print("    Skipping (No OS devices)")

print("\n--- Diagnostic Complete ---")
