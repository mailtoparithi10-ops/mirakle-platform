import requests
import json

try:
    response = requests.get('http://127.0.0.1:5001/api/opportunities/')
    data = response.json()
    if data['success']:
        print(f"Count: {len(data['data']['items'])}")
        if len(data['data']['items']) > 0:
            print(json.dumps(data['data']['items'][0], indent=2))
    else:
        print("API failed")
except Exception as e:
    print(f"Error: {e}")
