import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from backend.agents.graph_agent import GraphAgent
from dotenv import load_dotenv

load_dotenv()

def test_graph_agent():
    print("Initializing GraphAgent...")
    agent = GraphAgent()
    topic = "AI-Powered Academic Research Assistant & Grant Proposal Generator"
    
    print(f"Generating ideas for topic: {topic}")
    ideas = agent.generate_ideas(topic)
    
    if not ideas:
        print("Failed to generate ideas.")
        return
    
    print(f"Generated {len(ideas)} ideas.")
    for i, idea in enumerate(ideas):
        print(f"Idea {i+1}: {idea.get('title')}")
        
    output_dir = "db/test_graphs"
    print(f"Generating graph for the first idea...")
    filename = agent.generate_graph(ideas[0], output_dir)
    
    path = os.path.join(output_dir, filename)
    if os.path.exists(path):
        print(f"SUCCESS: Graph saved to {path}")
    else:
        print(f"FAILED: Graph not found at {path}")

if __name__ == "__main__":
    test_graph_agent()
