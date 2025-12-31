import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.main import app
    
    print("Checking registered routes:")
    required_routes = ["/api/status", "/api/settings", "/api/weather", "/api/ha"]
    found_routes = []
    
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"  - {route.path}")
            found_routes.append(route.path)
            
    missing = [r for r in required_routes if r not in found_routes]
    
    if missing:
        print(f"\n❌ CRITICAL: Missing endpoints: {missing}")
        sys.exit(1)
    else:
        print("\n✅ All critical endpoints verified.")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Failed to load backend: {e}")
    sys.exit(1)
