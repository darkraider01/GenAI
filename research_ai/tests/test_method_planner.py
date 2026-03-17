import sys
import os
from dotenv import load_dotenv

# Ensure backend modules can be imported
base_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, 'backend'))

from backend.methodology.method_planner import MethodPlanner

def test_paper_access_feature():
    load_dotenv()
    planner = MethodPlanner()
    topic = "Multimodal Learning for Cancer Detection"
    
    print(f"Testing methodology generation for topic: {topic}")
    result = planner.plan_methodology(topic)
    
    plan = result['plan_markdown']
    print("\n--- Generated Plan ---")
    print(plan)
    print("--- End of Plan ---\n")
    
    if "Primary Sources (Access Papers)" in plan:
        print("SUCCESS: Found 'Primary Sources (Access Papers)' section.")
    else:
        print("FAILED: 'Primary Sources (Access Papers)' section not found.")
        
    if "]](" in plan and ")" in plan:
        print("SUCCESS: Found potential markdown links.")
    else:
        print("FAILED: Markdown links not found in the output.")

if __name__ == "__main__":
    test_paper_access_feature()
