import requests
import time
from config import CONFIG
from typing import Dict, Any

def log_debug(msg):
    try:
        with open("backend_debug.log", "a") as f:
            f.write(f"[WEATHER] {time.ctime()}: {msg}\n")
    except: pass

class WeatherManager:
    def __init__(self):
        self.current_weather = None
        self.last_update = 0
        self.update_interval = 1800 # 30 minutes

    def get_weather(self) -> Dict[str, Any]:
        # Return cached if valid
        if time.time() - self.last_update < self.update_interval and self.current_weather:
            return self.current_weather
        
        # Rate Limit / Retry Backoff
        # If we failed recently, don't retry immediately to avoid banning
        if time.time() - self.last_update < 60 and not self.current_weather:
             return {"temp": "--", "code": 0, "unit": "F", "location_name": "Offline"}

        # Determine location
        loc = CONFIG.get("location")
        lat = loc["latitude"]
        lon = loc["longitude"]

        if loc["auto"]:
             # Only try auto-loc if we haven't successfully done it recently/ever
             # But here we try every time if 'auto' is set? That's bad.
             # Let's simple check: if we have 0.0,0.0 OR it's been a long time (e.g. on boot)
             self._update_location_auto()
             # Refresh from config (in case it updated)
        # Fetch Weather
        try:
            # 1. Update Location if needed
            if not self.lat or not self.lon:
                self._update_location_auto()
            
            # 2. Fetch Weather
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch"
            
            try:
                r = requests.get(url, timeout=10)
                data = r.json()
                pass # success
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
            self._last_weather_time = time.time()
            return self._cached_weather

        except Exception as e:
            print(f"Weather Error: {e}")
            log_debug(f"Weather Error (General): {e}")
            self._error_count += 1
            self._backoff_until = time.time() + 60 # Backoff 60s
            return {"temp": "--", "code": 0, "unit": "F", "location_name": "Offline"}

    def _update_location_auto(self):
        try:
            # Use ip-api to get lat/lon based on public IP
            r = requests.get("http://ip-api.com/json/", timeout=5)
            data = r.json()
            if data.get("status") == "success":
                self.lat = data.get("lat")
                self.lon = data.get("lon")
                self.location_name = data.get("city", "Unknown")
                log_debug(f"Location Found: {self.location_name} ({self.lat}, {self.lon})")
            else:
                 log_debug(f"Location API failed status: {data}")
        except Exception as e:
            print(f"Error auto-detecting location: {e}")
            log_debug(f"Location Detect Exception: {e}")
            # Fallback to defaults (optional)
