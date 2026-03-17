import requests
import os

def test_report_download():
    print("Testing Report Download API...")
    
    url = "http://localhost:8000/api/download-report"
    payload = {
        "topic": "Test Research Topic",
        "markdown": "# Test Report\nThis is a sample report content for testing PDF generation."
    }
    
    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        
        # Verify response headers
        print(f"Headers: {response.headers}")
        assert response.headers["content-type"] == "application/pdf"
        assert "Master_Report_Test_Research_Topic.pdf" in response.headers["content-disposition"]
        
        # Verify content is not empty and looks like a PDF
        content = response.content
        assert len(content) > 0
        assert content.startswith(b"%PDF")
        
        print("Test PASSED: PDF report generated and downloaded successfully.")
        
    except Exception as e:
        print(f"Test FAILED: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        raise

if __name__ == "__main__":
    test_report_download()
