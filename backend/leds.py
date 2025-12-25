import time
import threading
from config import CONFIG

# rpi_ws281x import (mocked if not available)
try:
    from rpi_ws281x import PixelStrip, Color as WsColor
    HAS_LEDS = True
except ImportError:
    HAS_LEDS = False
    # Mock class for development
    class WsColor:
        def __new__(cls, r, g, b): return (r, g, b)

class LEDManager:
    def __init__(self):
        self.mock_mode = CONFIG.get("mock_mode")
        self.strip = None
        self.led_count = 5
        self.led_pin = 18 # GPIO 18 (PCM)
        self.led_freq_hz = 800000
        self.led_dma = 10
        self.led_brightness = 255
        self.led_invert = False
        self.led_channel = 0
        
        self.current_colors = [(0,0,0)] * self.led_count
        self.running = True
        self.update_thread = None

        if not self.mock_mode and HAS_LEDS:
            self._init_real_leds()
        else:
            if not HAS_LEDS and not self.mock_mode:
                print("rpi_ws281x not found, forcing Mock LEDs")
            self.mock_mode = True
            
        # Start background effect loop (for pulsing/flashing)
        self.update_thread = threading.Thread(target=self._animate_loop, daemon=True)
        self.update_thread.start()

    def _init_real_leds(self):
        try:
            self.strip = PixelStrip(self.led_count, self.led_pin, self.led_freq_hz, 
                                  self.led_dma, self.led_invert, self.led_brightness, 
                                  self.led_channel)
            self.strip.begin()
        except Exception as e:
            print(f"Error initializing LEDs: {e}. Switching to Mock Mode.")
            self.mock_mode = True

    def update_from_sensors(self, sensor_data):
        # sensor_data is list of dicts from SensorManager
        # Map each sensor status to a color
        temp_thresholds = CONFIG.get("temp_thresholds")
        
        for i, sensor in enumerate(sensor_data):
            if i >= self.led_count: break
            
            temp = sensor['temp']
            status = sensor['status']
            
            if status == "critical":
                # Red
                self.current_colors[i] = (255, 0, 0)
            elif status == "warning":
                # Yellow/Orange
                self.current_colors[i] = (255, 140, 0)
            elif status == "normal":
                # Green
                self.current_colors[i] = (0, 255, 0)
            else:
                # Off or Blue for error
                self.current_colors[i] = (0, 0, 255)

    def _animate_loop(self):
        # Handle flashing for critical status
        flash_state = True
        while self.running:
            if self.mock_mode:
                # Just print status occasionally to not spam
                # time.sleep(5)
                # print(f"[MOCK LEDs] {self.current_colors}")
                time.sleep(1)
                continue

            # Real LED driving
            if self.strip:
                for i in range(self.strip.numPixels()):
                    if i < len(self.current_colors):
                        r, g, b = self.current_colors[i]
                        
                        # Flash effect for critical (Red)
                        if r == 255 and g == 0 and b == 0:
                            if not flash_state:
                                r, g, b = 50, 0, 0 # Dim instead of full off for smoother look
                        
                        self.strip.setPixelColor(i, WsColor(r, g, b))
                
                self.strip.show()
            
            flash_state = not flash_state
            time.sleep(0.5)

    def cleanup(self):
        self.running = False
        if self.strip:
            # Clear leds
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, WsColor(0,0,0))
            self.strip.show()

