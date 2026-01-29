import requests
import json

try:
    response = requests.get('http://127.0.0.1:5001/api/opportunities/')
    data = response.json()
    if data['success']:
        item = data['data']['items'][0]
        print(f"Sectors Type: {type(item.get('sectors'))}")
        print(f"Sectors value: {item.get('sectors')}")
    else:
        print("API failed")
except Exception as e:
    print(f"Error: {e}")
