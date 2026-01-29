#!/usr/bin/env python3
"""
Test script to verify startup dashboard API endpoints
"""

import requests
import json

def test_api_endpoint(url, description):
    """Test an API endpoint and print results"""
    print(f"\n🔍 Testing {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success: {description}")
                if 'data' in data and 'items' in data['data']:
                    print(f"   Items count: {len(data['data']['items'])}")
                elif 'referrals' in data:
                    print(f"   Referrals count: {len(data['referrals'])}")
                else:
                    print(f"   Response keys: {list(data.keys())}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"❌ Failed: {description}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

def main():
    base_url = "http://localhost:5001"
    
    # Test the main API endpoints used by startup dashboard
    test_api_endpoint(f"{base_url}/api/opportunities/", "Opportunities API")
    
    print("\n" + "="*60)
    print("🎯 SUMMARY")
    print("="*60)
    print("The startup dashboard should be working if:")
    print("1. ✅ Opportunities API returns 200 with data.items array")
    print("2. ✅ Each item has sectors field (array or string)")
    print("3. ✅ JavaScript can parse the sectors correctly")
    print("\nIf you're still seeing 'failed to load program', check:")
    print("- Browser console for JavaScript errors")
    print("- Network tab for failed API calls")
    print("- Authentication status (login required)")

if __name__ == "__main__":
    main()