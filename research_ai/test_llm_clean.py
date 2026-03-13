import traceback
import sys
from backend.methodology.method_planner import MethodPlanner

from dotenv import load_dotenv

load_dotenv()

with open("crash_log.txt", "w") as f:
    try:
        planner = MethodPlanner()
        response = planner.chain.invoke({"topic": "Testing", "context": "Fake context"})
        f.write("SUCCESS\n")
    except Exception as e:
        f.write("CRASH_REASON: " + repr(e) + "\n\n")
        traceback.print_exc(file=f)
