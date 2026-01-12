
# ==========================================
# Rack Dashboard Integration
# ==========================================

# 1. REST Command to Control Brightness
rest_command:
  pidash_set_brightness:
    url: "http://localhost:8000/api/settings"
    method: post
    payload: '{"led_brightness": {{ brightness }}}'
    content_type:  'application/json; charset=utf-8'

# 2. Sensors (Temperatures + Status + Global Settings)
sensor:
  # The Settings Sensor (Tracks Brightness)
  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 5
    name: "Rack Dashboard Settings"
    unique_id: "rack_dashboard_settings_global"
    value_template: "{{ value_json['_global']['mode'] }}"
    json_attributes_path: "$.['_global']"
    json_attributes:
      - brightness

  # The Temperature Probes
  # REPLACE 'YOUR_BAY_A_ID' etc. with actual IDs from http://<PI_IP>:8000/api/ha
  
  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 10
    name: "Dashboard Bay A"
    unique_id: "rack_dashboard_sensor_bay_a"
    value_template: "{{ value_json['YOUR_BAY_A_ID']['temp'] }}"
    unit_of_measurement: "°F"
    device_class: temperature
    json_attributes_path: "$.['YOUR_BAY_A_ID']"
    json_attributes:
      - led_rgb
      - status

  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 10
    name: "Dashboard Bay B"
    unique_id: "rack_dashboard_sensor_bay_b"
    value_template: "{{ value_json['YOUR_BAY_B_ID']['temp'] }}"
    unit_of_measurement: "°F"
    device_class: temperature
    json_attributes_path: "$.['YOUR_BAY_B_ID']"
    json_attributes:
      - led_rgb
      - status

  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 10
    name: "Dashboard Bay C"
    unique_id: "rack_dashboard_sensor_bay_c"
    value_template: "{{ value_json['YOUR_BAY_C_ID']['temp'] }}"
    unit_of_measurement: "°F"
    device_class: temperature
    json_attributes_path: "$.['YOUR_BAY_C_ID']"
    json_attributes:
      - led_rgb
      - status

  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 10
    name: "Dashboard Ambient"
    unique_id: "rack_dashboard_sensor_ambient"
    value_template: "{{ value_json['YOUR_AMBIENT_ID']['temp'] }}"
    unit_of_measurement: "°F"
    device_class: temperature
    json_attributes_path: "$.['YOUR_AMBIENT_ID']"
    json_attributes:
      - led_rgb
      - status

  - platform: rest
    resource: http://localhost:8000/api/ha
    scan_interval: 10
    name: "Dashboard Exhaust"
    unique_id: "rack_dashboard_sensor_exhaust"
    value_template: "{{ value_json['YOUR_EXHAUST_ID']['temp'] }}"
    unit_of_measurement: "°F"
    device_class: temperature
    json_attributes_path: "$.['YOUR_EXHAUST_ID']"
    json_attributes:
      - led_rgb
      - status

# 3. Light Entity (Master Brightness Control)
# Modern "template" syntax (replaces legacy "light: platform: template")
template:
  - light:
      - name: "Rack LEDs"
        unique_id: "rack_dashboard_led_controller"
        
        # State: On if brightness > 0
        state: "{{ state_attr('sensor.rack_dashboard_settings', 'brightness') | int > 0 }}"
        
        # Brightness: 0-255
        level: "{{ state_attr('sensor.rack_dashboard_settings', 'brightness') | int }}"
        
        # Color: RGB List [r, g, b]
        rgb: "{{ state_attr('sensor.dashboard_bay_a', 'led_rgb') }}"

        turn_on:
          action: rest_command.pidash_set_brightness
          data:
            brightness: 255

        turn_off:
          action: rest_command.pidash_set_brightness
          data:
            brightness: 0

        set_level:
          action: rest_command.pidash_set_brightness
          data:
            brightness: "{{ brightness }}"
