"""
Test if the auth routes are properly registered
"""
from app import create_app

app = create_app()

print("=" * 80)
print("REGISTERED ROUTES")
print("=" * 80)
print()

# Get all routes
routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
        'path': str(rule)
    })

# Sort by path
routes.sort(key=lambda x: x['path'])

# Print routes
for route in routes:
    print(f"{route['path']:40} {route['methods']:20} → {route['endpoint']}")

print()
print("=" * 80)
print("\nLooking for /auth/login route...")
auth_login = [r for r in routes if '/auth/login' in r['path']]
if auth_login:
    print("✓ Found /auth/login route:")
    for r in auth_login:
        print(f"  {r['path']} - Methods: {r['methods']}")
else:
    print("✗ /auth/login route NOT FOUND!")
    print("  This is why you're getting 405 error")

print("=" * 80)
