import sys
import os
import json

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__)))

from backend.rag.retriever import ResearchRetriever
from backend.trend_analysis.topic_model import analyze_trends
from backend.gap_analysis.gap_detector import detect_gaps
from backend.evaluation.novelty_score import NoveltyScorer

def run_trials():
    print("="*60)
    print("RUNNING RESEARCHNEX TRIALS")
    print("="*60)
    
    print("\n[1] Testing RAG Retriever...")
    try:
        retriever = ResearchRetriever()
        results = retriever.retrieve("agentic ai frameworks", top_k=2)
        print(f"-> Successfully retrieved {len(results)} papers.")
        for r in results:
            print(f"   - Title: {r.get('title', 'Unknown')}")
    except Exception as e:
        print(f"-> Error: {e}")

    print("\n[2] Testing Trend Analysis...")
    try:
        trends = analyze_trends()
        print(f"-> Successfully identified {len(trends)} emerging topics.")
        for t in trends[:2]: # Show top 2
            print(f"   - Topic {t.get('topic_id')} ({t.get('growth_rate')} growth): {t.get('keywords', [])[:3]}")
    except Exception as e:
        print(f"-> Error: {e}")

    print("\n[3] Testing Gap Detection...")
    try:
        gaps = detect_gaps()
        print(f"-> Successfully detected {len(gaps)} potential research gaps.")
        for g in gaps[:2]:
            print(f"   - Gap: {g.get('gap_description')}")
    except Exception as e:
        print(f"-> Error: {e}")
        
    print("\n[4] Testing Novelty Scorer...")
    try:
        scorer = NoveltyScorer()
        res = scorer.score_novelty("A completely novel mechanism for accelerating transformers using biological neural pathways.")
        print(f"-> Scored Proposal Novelty: {res['novelty_score']:.2f} (Max similarity: {res['max_similarity']:.2f})")
    except Exception as e:
        print(f"-> Error: {e}")

    print("\n" + "="*60)
    print("TRIALS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_trials()
