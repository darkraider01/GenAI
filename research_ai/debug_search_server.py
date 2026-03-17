import sys
import os
sys.path.append(os.path.abspath('backend'))
from backend.main import search_papers, SearchRequest
import asyncio

async def test():
    req = SearchRequest(query="Transformers in NLP")
    try:
        res = await search_papers(req)
        print(f"Success! Found {len(res)} results.")
        import json
        with open("test_output.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print("Wrote results to test_output.json")
    except Exception as e:
        import traceback
        print("Caught Exception:", repr(e))
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
