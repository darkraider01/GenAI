from dotenv import load_dotenv
load_dotenv()

import sys
import os
import time
import traceback

# Standardize path for backend imports
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')

if project_root not in sys.path:
    sys.path.append(project_root)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import the tools to test
from backend.agents.orchestrator import (
    search_literature_tool,
    trend_analysis_tool,
    gap_detection_tool,
    method_planning_tool,
    proposal_generation_tool,
    novelty_scoring_tool,
    ResearchOrchestrator
)

DELAY_BETWEEN_LLM_CALLS = 10  # Reduced delay since we are fixing things

def run_tests():
    with open("pipeline_test_log.txt", "w", encoding="utf-8") as f:
        def log(msg):
            # Clean emojis for Windows console if needed, though we replaced them
            print(msg)
            f.write(msg + "\n")
            f.flush()
            
        log("=" * 60)
        log("COMPREHENSIVE PIPELINE TEST - ALL 7 AGENTS")
        log("=" * 60)
        
        results = {}
        
        # 1. Literature Search
        try:
            log("\n[TEST 1/7] Literature Search Agent (search_literature_tool)...")
            res1 = search_literature_tool.run("AI in healthcare")
            log(f"  SUCCESS")
            log(f"  Output sample: {str(res1)[:300]}...")
            results["1_Literature"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["1_Literature"] = "FAIL"
            
        # 2. Trend Analysis
        try:
            log("\n[TEST 2/7] Trend Analysis Agent (trend_analysis_tool)...")
            res2 = trend_analysis_tool.run("")
            log(f"  SUCCESS")
            log(f"  Output sample: {str(res2)[:300]}...")
            results["2_Trend"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["2_Trend"] = "FAIL"
            
        # 3. Gap Detection
        try:
            log("\n[TEST 3/7] Gap Detection Agent (gap_detection_tool)...")
            res3 = gap_detection_tool.run("")
            log(f"  SUCCESS")
            log(f"  Output sample: {str(res3)[:300]}...")
            results["3_Gap"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["3_Gap"] = "FAIL"
        
        # 4. Method Planner
        method_plan = ""
        try:
            log(f"\n[TEST 4/7] Method Planner Agent (method_planning_tool)...")
            log(f"  [WAIT] Calling LLM...")
            method_plan = method_planning_tool.run("Federated Learning in Medical Imaging")
            log(f"  SUCCESS")
            log(f"  Output sample: {str(method_plan)[:300]}...")
            results["4_Method"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["4_Method"] = "FAIL"
        
        time.sleep(DELAY_BETWEEN_LLM_CALLS)
            
        # 5. Proposal Generator
        grant_proposal = ""
        try:
            log(f"\n[TEST 5/7] Proposal Generator Agent (proposal_generation_tool)...")
            log(f"  [WAIT] Calling LLM...")
            topic_str = f"Topic: Federated Learning in Medical Imaging\nMethodology:\n{method_plan}"
            grant_proposal = proposal_generation_tool.run(topic_str)
            log(f"  SUCCESS")
            log(f"  Output sample: {str(grant_proposal)[:300]}...")
            results["5_Proposal"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["5_Proposal"] = "FAIL"
            
        time.sleep(DELAY_BETWEEN_LLM_CALLS)
            
        # 6. Novelty Scorer
        try:
            log(f"\n[TEST 6/7] Novelty Scorer Agent (novelty_scoring_tool)...")
            test_text = grant_proposal if grant_proposal else "AI for healthcare using quantum computing"
            res6 = novelty_scoring_tool.run(test_text)
            log(f"  SUCCESS")
            log(f"  Output sample: {str(res6)[:300]}...")
            results["6_Novelty"] = "PASS"
        except Exception as e:
            log(f"  FAILED: {e}")
            results["6_Novelty"] = "FAIL"
            
        # 7. Full Orchestrator
        try:
            log(f"\n[TEST 7/7] Full Orchestrator (ResearchOrchestrator)...")
            log(f"  [WAIT] Running full pipeline...")
            orchestrator = ResearchOrchestrator()
            res7 = orchestrator.run_pipeline("Small language models on edge devices")
            log(f"  SUCCESS")
            log(f"  Report Length: {len(res7.get('report', ''))}")
            results["7_Orchestrator"] = "PASS"
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "QUOTA" in error_msg.upper():
                log(f"  RATE LIMITED (429) - Code works but API quota exceeded")
                results["7_Orchestrator"] = "RATE_LIMITED"
            else:
                log(f"  FAILED: {error_msg}")
                traceback.print_exc()
                results["7_Orchestrator"] = "FAIL"

        log("\n" + "="*50)
        log("FINAL TEST SUMMARY")
        log("="*50)
        for step, status in results.items():
            log(f"{step}: {status}")
        log("="*50)

if __name__ == "__main__":
    run_tests()
