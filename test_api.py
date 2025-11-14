import requests
import json

try:
    response = requests.get('http://localhost:8000/api/events/?limit=1')
    print(f"Status Code: {response.status_code}")
    print("\nResponse JSON:")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
