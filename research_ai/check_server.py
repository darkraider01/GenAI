import requests
import sys

def check_server():
    urls = [
        "http://localhost:8000/docs",
        "http://127.0.0.1:8000/docs",
        "http://localhost:8000/api/search-history"
    ]
    
    for url in urls:
        print(f"Checking {url}...")
        try:
            res = requests.get(url, timeout=5)
            print(f"Response from {url}: {res.status_code}")
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")

if __name__ == "__main__":
    check_server()
