import os, sys
sys.path.append(r'c:\Users\Hp\GenAI\research_ai\backend')
from literature_review.review_generator import LiteratureReviewGenerator
import traceback

try:
    print("Testing review generation...")
    gen = LiteratureReviewGenerator()
    res = gen.generate("AI-Powered Academic Research Assistant & Grant Proposal Generator")
    print("KEYS:", res.keys())
    print("SUCCESS")
except Exception as e:
    print("EXCEPTION:")
    traceback.print_exc()
