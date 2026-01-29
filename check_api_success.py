import requests

try:
    response = requests.get('http://127.0.0.1:5001/api/opportunities/')
    data = response.json()
    print(f"Keys: {list(data.keys())}")
    if 'success' in data:
        print(f"Success value: {data['success']}")
except Exception as e:
    print(f"Error: {e}")
