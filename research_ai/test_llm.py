import traceback
from backend.methodology.method_planner import MethodPlanner

print("--- TESTING METHOD PLANNER ---")
try:
    planner = MethodPlanner()
    # Let's bypass try/except inside the class to see the real error:
    response = planner.chain.invoke({
        "topic": "Testing",
        "context": "Fake context"
    })
    print("Method Planner Success:", response.content[:100])
except Exception as e:
    print("METHOD PLANNER ERROR:")
    traceback.print_exc()

print("\n--- TESTING ORCHESTRATOR ---")
try:
    from backend.agents.orchestrator import ResearchOrchestrator
    orchestrator = ResearchOrchestrator()
    print("Orchestrator Loaded Successfully!")
except Exception as e:
    print("ORCHESTRATOR ERROR:")
    traceback.print_exc()
