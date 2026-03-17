import os, sys
sys.path.append(r'c:\Users\Hp\GenAI\research_ai\backend')
try:
    from rag.retriever import ResearchRetriever
    print('Init')
    r = ResearchRetriever()
    print('Retrieving')
    results = r.retrieve('test query')
    print('Success:', len(results))
except Exception as e:
    import traceback
    traceback.print_exc()
