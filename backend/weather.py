import requests
import time
from config import CONFIG
from system import SystemManager
from typing import Dict, Any

def log_debug(msg):
    # Print to stdout so it shows in logs/console immediately
    print(f"[WEATHER] {msg}")
    try:
        with open("backend_debug.log", "a") as f:
            f.write(f"[WEATHER] {time.ctime()}: {msg}\n")
    except: pass

class WeatherManager:
    def __init__(self):
        self.current_weather = None
        self.last_update = 0
        self.update_interval = 1800 # 30 minutes
        
        # Initialize location attributes to prevent runtime errors
        self.lat = None
        self.lon = None
        self.location_name = "Unknown"
        self._error_count = 0
        self._backoff_until = 0
        self._cached_weather = None
        self._last_weather_time = 0
        self._is_using_auto_fallback = False
        self._last_location_check = 0
        self._location_check_interval = 3600 # Re-check every hour if auto

    def reload_config(self):
        """Reset cached location to force re-evaluation from CONFIG (auto or manual)"""
        self.lat = None
        self.lon = None
        self.location_name = "Unknown"
        self.last_update = 0 # Force weather fetch
        log_debug("Configuration reloaded, location cache reset.")

    def get_weather(self) -> Dict[str, Any]:
        # Return cached if valid
        if time.time() - self.last_update < self.update_interval and self.current_weather:
            return self.current_weather
        
        # Rate Limit / Retry Backoff
        # If we failed recently, don't retry immediately to avoid banning
        # BUT: If we have NO data yet (startup), retry aggressively (every 5s)
        backoff_time = 60
        if not self.current_weather:
            backoff_time = 5
            
        if self._backoff_until > time.time():
             return {"temp": "--", "code": 0, "unit": "F", "location_name": "Offline"}

        # Determine location
        loc = CONFIG.get("location")
        auto_mode = loc.get("auto", True)
        config_lat = loc["latitude"]
        config_lon = loc["longitude"]
        config_name = loc["name"]

        # 1. If in Auto Mode, try to pick it up if we don't have it or if it's been an hour
        if auto_mode:
            # If we don't have a location, OR if we previously fell back, OR if it's been an hour, try re-detecting
            should_check = (not self.lat or self._is_using_auto_fallback or 
                           (time.time() - self._last_location_check > self._location_check_interval))
            
            if should_check:
                self._update_location_auto()

        # 2. If NOT in Auto Mode, always use Config values
        else:
            self.lat = config_lat
            self.lon = config_lon
            self.location_name = config_name
            self._is_using_auto_fallback = False

        # 3. FINAL FALLBACK: If Auto failed (still None), use Config but mark as fallback so we retry
        if not self.lat or not self.lon:
            log_debug(f"Auto-location failed. Falling back to config: {config_name}")
            self.lat = config_lat
            self.lon = config_lon
            self.location_name = config_name
            self._is_using_auto_fallback = True

        # Fetch Weather
        try:
            # 2. Fetch Weather
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
            
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status() # Raise error for 4xx/5xx
                data = r.json()
            except Exception as e:
                log_debug(f"API Request Failed: {e}")
                raise e

            current = data.get("current", {})
            self._cached_weather = {
                "temp": current.get("temperature_2m", "--"),
                "code": current.get("weather_code", 0),
                "unit": "F",
                "location_name": self.location_name
            }
            self.current_weather = self._cached_weather
            self._last_weather_time = time.time()
            self.last_update = time.time()
            log_debug(f"Weather updated for {self.location_name}: {self._cached_weather['temp']}F")
            return self._cached_weather

        except Exception as e:
            print(f"Weather Error: {e}")
            log_debug(f"Weather Error (General): {e}")
            self._error_count += 1
            
            # Short backoff if we have nothing to show
            delay = 5 if not self.current_weather else 60
            self._backoff_until = time.time() + delay
            
            return {"temp": "--", "code": 0, "unit": "F", "location_name": "Offline"}

    def _update_location_auto(self):
        try:
            # Check config first - if auto is False, don't ping IP API
            loc = CONFIG.get("location")
            if not loc.get("auto", True):
                return # Skip auto

            # Use ip-api to get lat/lon based on public IP
            r = requests.get("http://ip-api.com/json/", timeout=5)
            data = r.json()
            if data.get("status") == "success":
                self.lat = data.get("lat")
                self.lon = data.get("lon")
                self.location_name = data.get("city", "Unknown")
                timezone = data.get("timezone")
                self._is_using_auto_fallback = False
                self._last_location_check = time.time()
                log_debug(f"Location Found (Auto): {self.location_name} ({self.lat}, {self.lon}), Timezone: {timezone}")
                
                if timezone:
                    success, msg = SystemManager.set_timezone(timezone)
                    log_debug(f"System Timezone Sync: {msg}")
            else:
                 log_debug(f"Location API failed status: {data}")
        except Exception as e:
            print(f"Error auto-detecting location: {e}")
            log_debug(f"Location Detect Exception: {e}")
            # Ensure we don't leave partial state if possible, though lat/lon should stay None

