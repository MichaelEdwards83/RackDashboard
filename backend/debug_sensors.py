import glob
import os
import sys
import time

# Add current directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("--- 1-Wire Sensor Diagnostic Tool (Integration Mode) ---")

# 1. Check OS Level
print("\n[1] Checking /sys/bus/w1/devices/...")
sys_paths = glob.glob("/sys/bus/w1/devices/28-*")
if not sys_paths:
    print("    FAIL: No devices found in filesystem.")
else:
    print(f"    SUCCESS: Found in OS: {[os.path.basename(p) for p in sys_paths]}")

# 2. Test SensorManager (The Real Code)
print("\n[2] Testing SensorManager Initialization...")
try:
    from sensors import SensorManager, NativeW1Sensor
    print("    Import Successful.")
    
    mgr = SensorManager()
    print(f"    Manager Initialized. Mock Mode: {mgr.mock_mode}")
    print(f"    Sensors Detected: {len(mgr.sensors)}")
    for s in mgr.sensors:
        print(f"      -> Sensor Obj: {s} (ID: {getattr(s, 'id', 'Unknown')})")
    
    print("\n[3] Testing Temperature Read (get_temperatures)...")
    readings = mgr.get_temperatures()
    print(f"    Readings Returned: {len(readings)}")
    for r in readings:
        print(f"      -> {r}")

except ImportError as e:
    print(f"    IMPORT ERROR: {e}")
except Exception as e:
    print(f"    CRITICAL RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Diagnostic Complete ---")
