"""
Test login endpoint directly
"""
import requests

# Test credentials
email = "admin@mirakle.local"
password = "admin123"

print("\n=== Testing Login Endpoint ===")
print(f"URL: http://127.0.0.1:5000/auth/login")
print(f"Email: {email}")
print(f"Password: {password}")

try:
    # Test POST request
    response = requests.post(
        "http://127.0.0.1:5000/auth/login",
        data={"email": email, "password": password},
        allow_redirects=False
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print(f"\n[SUCCESS] Login successful! Redirecting to: {response.headers.get('Location')}")
    elif response.status_code == 200:
        print(f"\n[SUCCESS] Login successful!")
        print(f"Response: {response.text[:200]}")
    else:
        print(f"\n[ERROR] Login failed!")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"\n[ERROR] Request failed: {e}")
