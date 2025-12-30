import requests
import time
from config import CONFIG
from typing import Dict, Any

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
             loc = CONFIG.get("location")
             lat = loc["latitude"]
             lon = loc["longitude"]

        # Fetch Weather
        try:
            unit_param = ""
            if CONFIG.get("temp_unit") == "F":
                unit_param = "&temperature_unit=fahrenheit"
            
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=auto{unit_param}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})
                
                self.current_weather = {
                    "temp": current.get("temperature_2m"),
                    "code": current.get("weather_code"),
                    "unit": data.get("current_units", {}).get("temperature_2m", "°C"),
                    "timezone": data.get("timezone"),
                    "location_name": loc.get("name", "Unknown")
                }
                self.last_update = time.time()
                return self.current_weather
        except Exception as e:
            print(f"Error fetching weather: {e}")
            self.last_update = time.time() # Mark attempted so we trigger backoff
        
        # Return Error State if no valid cache
        if not self.current_weather:
            return {"temp": "--", "code": 0, "unit": "F", "location_name": "Offline"}
            
        return self.current_weather

    def _update_location_auto(self):
        try:
            # use ip-api.com for free location by IP
            resp = requests.get("http://ip-api.com/json/", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data["status"] == "success":
                    new_loc = {
                        "auto": True,
                        "latitude": data["lat"],
                        "longitude": data["lon"],
                        "name": data["city"]
                    }
                    CONFIG.set("location", new_loc)
                    print(f"Auto-detected location: {data['city']}")
        except Exception as e:
            print(f"Error auto-detecting location: {e}")
