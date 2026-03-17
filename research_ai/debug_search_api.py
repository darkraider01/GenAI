import requests
try:
    res = requests.post("http://localhost:8000/api/search", json={"query": "machine learning"})
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
except Exception as e:
    print(f"Error: {e}")
