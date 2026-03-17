import sys
import os
import traceback

# Add the backend to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

print("=" * 60)
print("STEP 1: Testing SentenceTransformer")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en")
    embedding = model.encode("federated learning", normalize_embeddings=True)
    print(f"  [OK] SentenceTransformer OK. Embedding shape: {embedding.shape}")
except Exception as e:
    print(f"  [FAIL] SentenceTransformer FAILED: {e}")
    traceback.print_exc()

print("=" * 60)
print("STEP 2: Testing ChromaDB Connection")
try:
    import chromadb
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'chroma')
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="research_papers")
    count = collection.count()
    print(f"  [OK] ChromaDB OK. Document count: {count}")
except Exception as e:
    print(f"  [FAIL] ChromaDB FAILED: {e}")
    traceback.print_exc()

print("=" * 60)
print("STEP 3: Testing ChromaDB Query")
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    model = SentenceTransformer("BAAI/bge-large-en")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'chroma')
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="research_papers")
    
    embedding = model.encode("federated learning", normalize_embeddings=True).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=5)
    print(f"  [OK] ChromaDB Query OK. Found {len(results['ids'][0])} results")
except Exception as e:
    print(f"  [FAIL] ChromaDB Query FAILED: {e}")
    traceback.print_exc()

print("=" * 60)
print("STEP 4: Testing ResearchRetriever.retrieve()")
try:
    from rag.retriever import ResearchRetriever
    r = ResearchRetriever()
    results = r.retrieve("federated learning", top_k=3)
    print(f"  [OK] ResearchRetriever OK. Returned {len(results)} papers.")
    if results:
        print(f"  First result title: {results[0].get('title', 'N/A')}")
except Exception as e:
    print(f"  [FAIL] ResearchRetriever FAILED: {e}")
    traceback.print_exc()

print("=" * 60)
print("STEP 5: Testing LLM (Groq)")
try:
    from dotenv import load_dotenv
    load_dotenv()
    from utils.llm_factory import get_llm
    llm = get_llm()
    response = llm.invoke("Say 'hello' in one word.")
    print(f"  [OK] LLM OK. Response: {response.content[:50]}")
except Exception as e:
    print(f"  [FAIL] LLM FAILED: {e}")
    traceback.print_exc()

print("=" * 60)
print("DEBUG COMPLETE")
