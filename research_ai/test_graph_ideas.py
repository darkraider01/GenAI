import requests
import json
url = "http://localhost:8000/api/graph-ideas"
payload = {"topic": "AI-Powered Academic Research Assistant & Grant Proposal Generator", "custom_data": ""}
try:
    response = requests.post(url, json=payload)
    print("Ideas Status:", response.status_code)
    ideas = response.json().get("ideas", [])
    if ideas:
        graph_url = "http://localhost:8000/api/generate-graph"
        graph_payload = {"idea": ideas[0], "topic": payload["topic"]}
        resp2 = requests.post(graph_url, json=graph_payload)
        print("Graph Status:", resp2.status_code)
        print("Graph Text:", resp2.text)
except Exception as e:
    print("Error:", str(e))
