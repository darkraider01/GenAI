import requests
import sys

print("Testing direct POST request to localhost:8000/api/literature-review")
try:
    res = requests.post(
        "http://127.0.0.1:8000/api/literature-review", 
        json={"topic": "AI-Powered Academic Research Assistant & Grant Proposal Generator"},
        timeout=120
    )
    print(f"Status Code: {res.status_code}")
    if res.status_code != 200:
        print(f"Error Text: {res.text}")
    else:
        print("Success! Keys:", res.json().keys())
except Exception as e:
    print(f"Request failed: {e}")
