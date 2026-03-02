import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from weather import WeatherManager
from config import CONFIG

class TestAutoLocationRobustness(unittest.TestCase):
    @patch('config.CONFIG.get')
    @patch('system.SystemManager.set_timezone')
    @patch('requests.get')
    def test_retry_on_fallback(self, mock_get, mock_set_tz, mock_config_get):
        mock_set_tz.return_value = (True, "Success")
        
        # Mock Config to return Las Vegas as fallback
        def side_effect(key, default=None):
            if key == "location":
                return {"auto": True, "latitude": 36.1699, "longitude": -115.1398, "name": "Las Vegas"}
            return default
        mock_config_get.side_effect = side_effect
        # 1. Setup: First call fails, should hit fallback
        mock_resp_fail = MagicMock()
        mock_resp_fail.json.return_value = {"status": "fail"}
        mock_get.return_value = mock_resp_fail
        
        mgr = WeatherManager()
        
        # Initial state
        self.assertFalse(mgr._is_using_auto_fallback)
        
        # Trigger weather fetch (which triggers location check)
        mgr.get_weather()
        
        self.assertTrue(mgr._is_using_auto_fallback)
        self.assertEqual(mgr.location_name, "Las Vegas") # Config default
        
        # 2. Second call: API now works, should re-detect because it's using fallback
        mock_resp_success = MagicMock()
        mock_resp_success.json.return_value = {
            "status": "success",
            "lat": 44.0582,
            "lon": -121.3153,
            "city": "Bend",
            "timezone": "America/Los_Angeles"
        }
        mock_get.return_value = mock_resp_success
        
        # Reset last_update to force a fresh fetch
        mgr.last_update = 0
        mgr.get_weather()
        
        self.assertFalse(mgr._is_using_auto_fallback)
        self.assertEqual(mgr.location_name, "Bend")
        self.assertEqual(mgr.lat, 44.0582)

    @patch('config.CONFIG.get')
    @patch('system.SystemManager.set_timezone')
    @patch('requests.get')
    def test_periodic_recheck(self, mock_get, mock_set_tz, mock_config_get):
        mock_set_tz.return_value = (True, "Success")
        mock_config_get.return_value = {"auto": True, "latitude": 0, "longitude": 0, "name": "Unknown"}
        # 1. Initial success
        mock_resp_1 = MagicMock()
        mock_resp_1.json.return_value = {
            "status": "success", "lat": 1, "lon": 1, "city": "City A", "timezone": "UTC"
        }
        mock_get.return_value = mock_resp_1
        
        mgr = WeatherManager()
        mgr.get_weather()
        self.assertEqual(mgr.location_name, "City A")
        
        # 2. Fast forward time by 2 hours
        with patch('time.time', return_value=time.time() + 7200):
            mock_resp_2 = MagicMock()
            mock_resp_2.json.return_value = {
                "status": "success", "lat": 2, "lon": 2, "city": "City B", "timezone": "UTC"
            }
            mock_get.return_value = mock_resp_2
            
            mgr.last_update = 0 # Force weather fetch
            mgr.get_weather()
            
            self.assertEqual(mgr.location_name, "City B")

if __name__ == '__main__':
    unittest.main()
