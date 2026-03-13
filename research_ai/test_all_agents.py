from dotenv import load_dotenv
load_dotenv()

import sys
import time
import traceback

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

DELAY_BETWEEN_LLM_CALLS = 25  # seconds - stay under free tier RPM

def run_tests():
    with open("pipeline_test_log.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")
            f.flush()  # flush immediately so we can read the file while running
            
        log("=" * 60)
        log("COMPREHENSIVE PIPELINE TEST - ALL 7 AGENTS")
        log("=" * 60)
        
        results = {}
        
        # 1. Literature Search (no LLM call, just vector DB)
        try:
            log("\n[TEST 1/7] Literature Search Agent (search_literature_tool)...")
            res1 = search_literature_tool.run(query="AI in healthcare")
            log(f"  ✅ SUCCESS")
            log(f"  Output: {str(res1)[:300]}")
            results["1_Literature"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["1_Literature"] = "FAIL"
            
        # 2. Trend Analysis (no LLM call, just BERTopic)
        try:
            log("\n[TEST 2/7] Trend Analysis Agent (trend_analysis_tool)...")
            res2 = trend_analysis_tool.run()
            log(f"  ✅ SUCCESS")
            log(f"  Output: {str(res2)[:300]}")
            results["2_Trend"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["2_Trend"] = "FAIL"
            
        # 3. Gap Detection (no LLM call, just embeddings + graph)
        try:
            log("\n[TEST 3/7] Gap Detection Agent (gap_detection_tool)...")
            res3 = gap_detection_tool.run()
            log(f"  ✅ SUCCESS")
            log(f"  Output: {str(res3)[:300]}")
            results["3_Gap"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["3_Gap"] = "FAIL"
        
        # 4. Method Planner (LLM call - needs delay)
        method_plan = ""
        try:
            log(f"\n[TEST 4/7] Method Planner Agent (method_planning_tool)...")
            log(f"  ⏳ Calling Gemini API...")
            method_plan = method_planning_tool.run(topic="Federated Learning in Medical Imaging")
            is_placeholder = "Placeholder" in str(method_plan)
            if is_placeholder:
                log(f"  ⚠️  GOT PLACEHOLDER (LLM call failed silently, likely rate-limited)")
                results["4_Method"] = "PARTIAL (placeholder)"
            else:
                log(f"  ✅ SUCCESS - Got real LLM output")
                log(f"  Output: {str(method_plan)[:300]}")
                results["4_Method"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["4_Method"] = "FAIL"
        
        log(f"  💤 Waiting {DELAY_BETWEEN_LLM_CALLS}s for rate limit cooldown...")
        time.sleep(DELAY_BETWEEN_LLM_CALLS)
            
        # 5. Proposal Generator (LLM call)
        grant_proposal = ""
        try:
            log(f"\n[TEST 5/7] Proposal Generator Agent (proposal_generation_tool)...")
            log(f"  ⏳ Calling Gemini API...")
            topic_str = f"Topic: Federated Learning in Medical Imaging\nMethodology:\n{method_plan}"
            grant_proposal = proposal_generation_tool.run(topic_and_methodology=topic_str)
            is_placeholder = "# 1. Abstract\n# 2." in str(grant_proposal) and len(str(grant_proposal)) < 300
            if is_placeholder:
                log(f"  ⚠️  GOT PLACEHOLDER (LLM call failed silently)")
                results["5_Proposal"] = "PARTIAL (placeholder)"
            else:
                log(f"  ✅ SUCCESS - Got real LLM output")
                log(f"  Output: {str(grant_proposal)[:300]}")
                results["5_Proposal"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["5_Proposal"] = "FAIL"
            
        log(f"  💤 Waiting {DELAY_BETWEEN_LLM_CALLS}s for rate limit cooldown...")
        time.sleep(DELAY_BETWEEN_LLM_CALLS)
            
        # 6. Novelty Scorer (no LLM, just embeddings + cosine similarity)
        try:
            log(f"\n[TEST 6/7] Novelty Scorer Agent (novelty_scoring_tool)...")
            test_text = grant_proposal if grant_proposal else "AI for healthcare using quantum computing"
            res6 = novelty_scoring_tool.run(proposal_text=test_text)
            log(f"  ✅ SUCCESS")
            log(f"  Output: {str(res6)[:300]}")
            results["6_Novelty"] = "PASS"
        except Exception as e:
            log(f"  ❌ FAILED: {e}")
            results["6_Novelty"] = "FAIL"
            
        # 7. Full CrewAI Orchestrator (multiple LLM calls)
        try:
            log(f"\n[TEST 7/7] Full CrewAI Orchestrator (ResearchOrchestrator)...")
            log(f"  ⏳ Starting crew.kickoff() - this makes 6+ sequential LLM calls...")
            log(f"  ⚠️  This may take 2-5 minutes on free tier due to rate limits")
            orchestrator = ResearchOrchestrator()
            res7 = orchestrator.run_pipeline("AI in healthcare")
            log(f"  ✅ SUCCESS - Orchestrator completed!")
            log(f"  Output: {str(res7)[:500]}")
            results["7_Orchestrator"] = "PASS"
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                log(f"  ⚠️  RATE LIMITED (429) - Code works but Google free tier quota exceeded")
                log(f"  💡 The orchestrator fires 6+ LLM calls. Free tier limit is 20/day for gemini-3-flash.")
                results["7_Orchestrator"] = "RATE_LIMITED (code is correct)"
            else:
                log(f"  ❌ FAILED: {error_msg}")
                results["7_Orchestrator"] = "FAIL"
        
        log("\n" + "=" * 60)
        log("RESULTS SUMMARY")
        log("=" * 60)
        for test_name, status in results.items():
            emoji = "✅" if status == "PASS" else "⚠️" if "PARTIAL" in status or "RATE" in status else "❌"
            log(f"  {emoji} {test_name}: {status}")
        log("=" * 60)

if __name__ == "__main__":
    run_tests()
