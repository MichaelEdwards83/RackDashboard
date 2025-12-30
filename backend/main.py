import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

from config import CONFIG
from sensors import SensorManager
from leds import LEDManager
from weather import WeatherManager
from system import SystemManager
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for development (allowing Vite frontend to talk to us)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Modules
sensors_mgr = SensorManager()
leds_mgr = LEDManager()
weather_mgr = WeatherManager()

class SettingsUpdate(BaseModel):
    ntp_server: str = None
    location_auto: bool = None
    threshold_warning: float = None
    threshold_critical: float = None
    sensor_id: str = None # If provided, thresholds apply to this sensor. If "global" or None, applies globally.
    sensor_name: str = None # Optional name update for sensor_id
    mock_mode: bool = None

# ... (startup event and background tasks unchanged) ...

@app.on_event("startup")
async def startup_event():
    # Start background polling loop
    asyncio.create_task(run_background_tasks())

async def run_background_tasks():
    while True:
        try:
            # 1. Read Sensors
            readings = sensors_mgr.get_temperatures()
            
            # 2. Update LEDs
            leds_mgr.update_from_sensors(readings)
            
            # 3. Opportunistic Weather Update (internal cache handles interval)
            # Run in thread to prevent blocking loop
            await asyncio.to_thread(weather_mgr.get_weather)
            
            # Sleep
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Background loop error: {e}")
            await asyncio.sleep(5)

@app.on_event("shutdown")
def shutdown_event():
    leds_mgr.cleanup()

@app.get("/api/status")
def get_status():
    readings = sensors_mgr.get_temperatures()
    # Format current time
    now = datetime.now()
    
    return {
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%A, %B %d"),
        "sensors": readings,
        "led_status": leds_mgr.current_colors if leds_mgr.mock_mode else "hardware_controlled"
    }

@app.get("/api/weather")
def get_weather():
    w = weather_mgr.get_weather()
    if not w:
        return {"status": "unavailable"}
    return w

@app.get("/api/ha")
def get_ha_data():
    """
    Simplified endpoint for Home Assistant.
    Returns a dictionary keyed by Sensor ID for stable parsing.
    Example: { "28-03...": { "temp": 72.1, "name": "Bay A" } }
    """
    readings = sensors_mgr.get_temperatures()
    data = {}
    for r in readings:
        # Use simple dictionary struct
        data[r["id"]] = {
            "temp": r["temp"],
            "name": r["name"],
            "status": r["status"]
        }
    return data

@app.get("/api/settings")
def get_settings():
    return CONFIG.get_all()

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate):
    try:
        current = CONFIG.get_all()
        # Log payload
        try:
            with open("backend_debug.log", "a") as f:
                f.write(f"SETTINGS REQUEST: {settings}\n")
        except: pass

        # Check structure update (migration fix if config.json was old)
        if "global" not in current["temp_thresholds"]:
             current["temp_thresholds"] = {
                 "global": current["temp_thresholds"],
                 "sensors": {}
             }

        # Update Thresholds
        target_scope = "global"
        if settings.sensor_id and settings.sensor_id != "global":
            target_scope = "sensors"
            
        if target_scope == "global":
            if settings.threshold_warning is not None:
                current["temp_thresholds"]["global"]["warning"] = settings.threshold_warning
            if settings.threshold_critical is not None:
                 current["temp_thresholds"]["global"]["critical"] = settings.threshold_critical
        else:
            # Per-sensor
            sid = settings.sensor_id
            if sid not in current["temp_thresholds"]["sensors"]:
                # Copy global as baseline if creating new
                 current["temp_thresholds"]["sensors"][sid] = \
                     current["temp_thresholds"]["global"].copy()
            
            if settings.threshold_warning is not None:
                current["temp_thresholds"]["sensors"][sid]["warning"] = settings.threshold_warning
            if settings.threshold_critical is not None:
                 current["temp_thresholds"]["sensors"][sid]["critical"] = settings.threshold_critical
            
            # Update Name
            if settings.sensor_name is not None:
                 if "sensor_names" not in current:
                     current["sensor_names"] = {}
                 current["sensor_names"][sid] = settings.sensor_name

        # Update Location
        if settings.location_auto is not None:
            current["location"]["auto"] = settings.location_auto
            
        # Update Mock Mode
        if settings.mock_mode is not None:
            current["mock_mode"] = settings.mock_mode
            
        CONFIG.save()
        return {"status": "ok", "config": current}
        
    except Exception as e:
        try:
            with open("backend_debug.log", "a") as f:
                f.write(f"SETTINGS ENDPOINT ERROR: {e}\n")
        except: pass
        raise HTTPException(status_code=500, detail=str(e))
    
    # Reload Managers
    sensors_mgr.reload_config()
    leds_mgr.reload_config()
    
    # Update NTP
    msg = "Settings updated"
    if settings.ntp_server:
        success, ntp_msg = SystemManager.set_ntp_server(settings.ntp_server)
        msg += f". {ntp_msg}"
        
    return {"message": msg, "config": CONFIG.get_all()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
