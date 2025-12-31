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
      
      # Sensor 2
      - name: "Dashboard Bay B"
        value_template: "{{ value_json['28-8a2b1c4d5e6f']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature

      # Sensor 3
      - name: "Dashboard Bay C"
        value_template: "{{ value_json['28-7d3e4f5g6h7i']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature

      # Sensor 4
      - name: "Dashboard Ambient"
        value_template: "{{ value_json['28-1a2b3c4d5e6f']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature

      - name: "Dashboard Exhaust"
        value_template: "{{ value_json['28-9z8y7x6w5v4u']['temp'] }}"
        unit_of_measurement: "°F"
        device_class: temperature

## Step 3: Brightness Control (Optional)
To control the LED brightness from Home Assistant, add this to your `configuration.yaml`:

```yaml
rest_command:
  pidash_set_brightness:
    url: "http://localhost:8000/api/settings"
    method: post
    payload: '{"led_brightness": {{ brightness }}}'
    content_type:  'application/json; charset=utf-8'
```
*Usage:* Call this service with `brightness` (0-255). Example:
```yaml
service: rest_command.pidash_set_brightness
data:
  brightness: 128
```

## Step 4: Restart Home Assistant
After saving the file, restart Home Assistant to apply the changes. Your new sensors will appear as `sensor.dashboard_bay_a`, etc.
