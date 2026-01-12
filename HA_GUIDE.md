# Home Assistant Integration Guide

This guide explains how to pull your Raspberry Pi temperature data into Home Assistant (HA).

## Prerequisites
- This Dashboard running on your Pi.
- Home Assistant (running on the same Pi or another device on the network).

## Step 1: Verification
Ensure the new API endpoint is working. Open this URL in your browser:
`http://<YOUR_PI_IP>:8000/api/ha`

You should see JSON output like:
```json
{
  "28-3c01f096d29c": { "temp": 72.5, "name": "Bay A", "status": "normal" },
  "28-8a2b1c4d5e6f": { "temp": 68.2, "name": "Ambient", "status": "normal" }
}
```

## Step 2: Configure Home Assistant
Add the following to your `configuration.yaml` file in Home Assistant.

> [!IMPORTANT]
> Replace `http://localhost:8000` with your actual Pi IP if HA is on a different machine.
> Replace the `28-xxxx` IDs with **YOUR** actual Sensor IDs found in Step 1.

```yaml
rest:
  - resource: http://localhost:8000/api/ha
    scan_interval: 10
    sensor:
      # Sensor 1
      - name: "Dashboard Bay A"
        value_template: "{{ value_json['28-3c01f096d29c']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature
        json_attributes_path: "$.['28-3c01f096d29c']"
        json_attributes:
          - led_rgb
          - status
      
      # Sensor 2
      - name: "Dashboard Bay B"
        value_template: "{{ value_json['28-8a2b1c4d5e6f']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature
        json_attributes_path: "$.['28-8a2b1c4d5e6f']"
        json_attributes:
          - led_rgb
          - status

      # Sensor 3
      - name: "Dashboard Bay C"
        value_template: "{{ value_json['28-7d3e4f5g6h7i']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature
        json_attributes_path: "$.['28-7d3e4f5g6h7i']"
        json_attributes:
          - led_rgb
          - status

      # Sensor 4
      - name: "Dashboard Ambient"
        value_template: "{{ value_json['28-1a2b3c4d5e6f']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature
        json_attributes_path: "$.['28-1a2b3c4d5e6f']"
        json_attributes:
          - led_rgb
          - status

      - name: "Dashboard Exhaust"
        value_template: "{{ value_json['28-9z8y7x6w5v4u']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature
        json_attributes_path: "$.['28-9z8y7x6w5v4u']"
        json_attributes:
          - led_rgb
          - status

### 1. Define the REST Command
Add this to `configuration.yaml` (or ensure it's there):
```yaml
rest_command:
  pidash_set_brightness:
    url: "http://localhost:8000/api/settings"
    method: post
    payload: '{"led_brightness": {{ brightness }}}'
    content_type:  'application/json; charset=utf-8'
```

### 2. Define the Status Sensor
We need a sensor to track the current brightness and settings from the dashboard. Add this to your `sensor:` section (or `configuration.yaml`):
```yaml
  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 5
    name: "Rack Dashboard Settings"
    value_template: "{{ value_json['_global']['mode'] }}" 
    json_attributes_path: "$.['_global']"
    json_attributes:
      - brightness
```

### 3. Create a Light Entity
This creates a proper "Light" in Home Assistant that tracks the text color and controls brightness. Add this to your `light:` section (or `configuration.yaml`):

```yaml
light:
  - platform: template
    lights:
      rack_leds:
        friendly_name: "Rack LEDs"
        # On if brightness > 0
        value_template: "{{ state_attr('sensor.rack_dashboard_settings', 'brightness') | int > 0 }}"
        
        # Read brightness from API
        level_template: "{{ state_attr('sensor.rack_dashboard_settings', 'brightness') | int }}"
        
        # Read color from Bay A (as a proxy for the rack status)
        color_template: >
          {{ state_attr('sensor.dashboard_bay_a', 'led_rgb') }}

        # Turn On = Max Brightness
        turn_on:
          service: rest_command.pidash_set_brightness
          data:
            brightness: 255

        # Turn Off = 0 Brightness
        turn_off:
          service: rest_command.pidash_set_brightness
          data:
            brightness: 0

        # Set Brightness
        set_level:
          service: rest_command.pidash_set_brightness
          data:
            brightness: "{{ brightness }}"
```

## Step 4: Restart Home Assistant
After saving the file, restart Home Assistant to apply the changes. Your new sensors will appear as `sensor.dashboard_bay_a`, etc.
