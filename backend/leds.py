import time
import threading
from config import CONFIG

# NeoPixel / Blinka Import
try:
    import board
    import neopixel
    HAS_LEDS = True
except Exception as e:
    HAS_LEDS = False
    print(f"NeoPixel/Blinka libraries not found: {e}. Using Mock LEDs.")

class LEDManager:
    def __init__(self):
        self.mock_mode = CONFIG.get("mock_mode")
        self.pixels = None
        self.led_count = 8 # User specified 8 LEDs
        self.led_pin = None
        if HAS_LEDS:
            self.led_pin = board.D18 # GPIO 18
        
        # self.current_brightness is float 0.0-1.0
        self.current_brightness = float(CONFIG.get("led_brightness", 255)) / 255.0

    @property
    def led_brightness(self):
        """Return brightness as 0-255 integer for backward compatibility"""
        return int(self.current_brightness * 255)

    @led_brightness.setter
    def led_brightness(self, value):
        """Set brightness from 0-255 integer"""
        self.current_brightness = max(0, min(255, int(value))) / 255.0
        if self.pixels:
            self.pixels.brightness = self.current_brightness

        
        self.current_colors = [(0,0,0)] * self.led_count
        self.running = True
        self.update_thread = None

        if not self.mock_mode and HAS_LEDS:
            self._init_real_leds()
        else:
            self.mock_mode = True
            
        # Start background effect loop (for pulsing/flashing)
        self.update_thread = threading.Thread(target=self._animate_loop, daemon=True)
        self.update_thread.start()

    def reload_config(self):
        new_mock = CONFIG.get("mock_mode")
        # Config stores 0-255, NeoPixel uses 0.0-1.0
        new_brightness_int = CONFIG.get("led_brightness", 255)
        new_brightness = float(new_brightness_int) / 255.0
        
        # Update Brightness if changed
        if self.pixels and abs(new_brightness - self.current_brightness) > 0.01:
            self.current_brightness = new_brightness
            try:
                self.pixels.brightness = self.current_brightness
            except Exception as e:
                print(f"Error setting brightness: {e}")

        if self.mock_mode and not new_mock:
             # Switching from Mock -> Real
             if not self.pixels and HAS_LEDS:
                print("Switching to Real LEDs (NeoPixel)...")
                self._init_real_leds()
        
        self.mock_mode = new_mock

    def _init_real_leds(self):
        try:
            # check for sudo/root? NeoPixel on Pi 5 usually needs root for GPIO mapping via Blinka/PlatformDetect
            # The service is now running as root, so this should work.
            
            # Auto-write false for smoother animations
            self.pixels = neopixel.NeoPixel(
                self.led_pin, 
                self.led_count, 
                brightness=self.current_brightness, 
                auto_write=False, 
                pixel_order=neopixel.GRB # WS2812 is usually GRB
            )
            print(f"[LEDS] NeoPixel Initialized on D18 with {self.led_count} LEDs.")
        except Exception as e:
            print(f"Error initializing NeoPixel LEDs: {e}. Switching to Mock Mode.")
            self.mock_mode = True

    def update_from_sensors(self, sensor_data):
        # sensor_data is list of dicts from SensorManager
        # Map each sensor status to a color
        
        # Reset all to off first? Or keep last state?
        # We will overwrite indices 0..N based on sensors
        
        for i, sensor in enumerate(sensor_data):
            if i >= self.led_count: break
            
            status = sensor['status']
            
            # Default RGB colors
            if status == "critical":
                self.current_colors[i] = (255, 0, 0) # Red
            elif status == "warning":
                self.current_colors[i] = (255, 140, 0) # Orange
            elif status == "normal":
                self.current_colors[i] = (0, 255, 0) # Green
            elif status == "searching":
                self.current_colors[i] = (0, 0, 255) # Blue
            elif status == "empty":
                self.current_colors[i] = (0, 0, 0) # Off
            else:
                self.current_colors[i] = (0, 50, 50) # Dim Cyan for unknown

        # If we have more LEDs than sensors, make the rest ...?
        # Let's make them dim white (or off) for now. Use config?
        # Leaving them 0,0,0 as initialized.

    def _animate_loop(self):
        # Handle flashing for critical status
        flash_state = True
        while self.running:
            if self.mock_mode:
                time.sleep(1)
                continue

            # Real LED driving
            if self.pixels:
                try:
                    for i in range(self.led_count):
                        if i < len(self.current_colors):
                            r, g, b = self.current_colors[i]
                            
                            # Flash effect for critical (Red)
                            if r == 255 and g == 0 and b == 0:
                                if not flash_state:
                                    r, g, b = 50, 0, 0 # Dim instead of full off
                            
                            self.pixels[i] = (r, g, b)
                    
                    self.pixels.show()
                except Exception as e:
                    print(f"LED Update Error: {e}")
            
            flash_state = not flash_state
            time.sleep(0.5)

    def cleanup(self):
        self.running = False
        if self.pixels:
            try:
                self.pixels.fill((0, 0, 0))
                self.pixels.show()
            except: pass

