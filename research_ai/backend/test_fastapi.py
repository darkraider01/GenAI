import os, sys
sys.path.append(r'c:\Users\Hp\GenAI\research_ai\backend')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Starting test on /api/search")
response = client.post("/api/search", json={"query": "test query"})
print("Status code:", response.status_code)
if response.status_code == 200:
    results = response.json()
    print("Results length:", len(results))
else:
    print("Error:", response.text)

print("Starting test on /api/search-history")
his_response = client.get("/api/search-history")
print("Status code:", his_response.status_code)
if his_response.status_code == 200:
    history = his_response.json().get("history", [])
    print("History entries:", len(history))
else:
    print("Error:", his_response.text)
