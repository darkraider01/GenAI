import os
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

class ResearchRetriever:
    _shared_model = None

    def __init__(self, db_path=None, collection_name="research_papers", model_name="BAAI/bge-large-en"):
        # Set up paths relative to the project root
        # This file is in backend/rag/
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Robustly find the 27MB database if not specified
        if db_path is None:
            db_path = os.path.join(project_root, 'db', 'chroma')
            # Fallback check: if root/db/chroma doesn't exist but backend/db/chroma does, warn but use root/db/chroma
            # because that's where the 1000 docs are.
            if not os.path.exists(db_path):
                 print(f"Warning: Primary DB path {db_path} not found. Creating it.")
        
        self.db_path = os.path.abspath(db_path)
        self.collection_name = collection_name
        
        print(f"Retriever initialized with db_path: {self.db_path}")
        
        # Singleton model loading to prevent redundant memory usage and lag
        if ResearchRetriever._shared_model is None:
            print(f"Loading embedding model: {model_name}...")
            try:
                # Explicitly disable tqdm for this call in case main script didn't catch it
                os.environ["TQDM_DISABLE"] = "1"
                ResearchRetriever._shared_model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"Warning: Model loading error (likely tqdm stream): {e}. Retrying without tqdm...")
                # Second attempt if the first failed due to some weird hook
                ResearchRetriever._shared_model = SentenceTransformer(model_name)
        self.model = ResearchRetriever._shared_model
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            doc_count = self.collection.count()
            print(f"Connected to ChromaDB. Collection '{self.collection_name}' has {doc_count} documents.")
        except Exception as e:
            print(f"CRITICAL ERROR: Could not connect to ChromaDB at {self.db_path}: {e}")
            raise e
        
        # BM25 Keyword Indexing (Hybrid Search)
        self.bm25 = None
        self.corpus = []
        self.metadata = []
        self.ids = []
        self._build_bm25_index()

    def _build_bm25_index(self):
        """Builds the BM25 index from all documents in the ChromaDB collection."""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            if results and results['documents']:
                self.corpus = results['documents']
                self.metadata = results['metadatas']
                self.ids = results['ids'] # IDs are always returned
                
                print(f"Building BM25 keyword index for {len(self.corpus)} documents...")
                tokenized_corpus = [doc.lower().split() for doc in self.corpus]
                self.bm25 = BM25Okapi(tokenized_corpus)
            else:
                print("ChromaDB is empty. BM25 index not built.")
        except Exception as e:
            print(f"Error building BM25 index: {e}")

    def retrieve(self, query: str, top_k: int = 5):
        """
        Hybrid retrieval: Vector search (Semantic) + BM25 (Keyword)
        Uses Reciprocal Rank Fusion (RRF) to combine results.
        """
        try:
            total_docs = self.collection.count()
        except Exception as e:
            print(f"Error counting documents in collection: {e}")
            return []

        if total_docs == 0:
            print("Collection is empty. Returning 0 results.")
            return []
            
        # 1. Semantic Search
        query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()
        
        # Ensure n_results is at least 1 and no more than total_docs
        safe_n_results = max(1, min(top_k * 2, total_docs))
        
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=safe_n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Map IDs to rank and data for RFF
        vector_ranks = {}
        if vector_results['ids'] and len(vector_results['ids'][0]) > 0:
            for rank, doc_id in enumerate(vector_results['ids'][0]):
                vector_ranks[doc_id] = {
                    "rank": rank + 1,
                    "metadata": vector_results['metadatas'][0][rank] if vector_results['metadatas'] else {},
                    "document": vector_results['documents'][0][rank] if vector_results['documents'] else "",
                    "distance": vector_results['distances'][0][rank] if 'distances' in vector_results else 0
                }

        # 2. Keyword Search (BM25)
        bm25_ranks = {}
        if self.bm25 and self.corpus:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Get top scores
            top_n_indices = np.argsort(bm25_scores)[-safe_n_results:][::-1]
            for rank, idx in enumerate(top_n_indices):
                if bm25_scores[idx] > 0:
                    doc_id = self.ids[idx]
                    bm25_ranks[doc_id] = rank + 1

        # 3. Reciprocal Rank Fusion (RRF)
        k = 60
        fused_scores = {}
        all_doc_ids = set(vector_ranks.keys()).union(set(bm25_ranks.keys()))
        
        for doc_id in all_doc_ids:
            score = 0
            if doc_id in vector_ranks:
                score += 1.0 / (k + vector_ranks[doc_id]["rank"])
            if doc_id in bm25_ranks:
                score += 1.0 / (k + bm25_ranks[doc_id])
            fused_scores[doc_id] = score
            
        # Sort by fused score
        sorted_docs = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        retrieved_papers = []
        for doc_id, hybrid_score in sorted_docs:
            match_reason = []
            if doc_id in vector_ranks:
                match_reason.append("Semantic Match")
                metadata = vector_ranks[doc_id]["metadata"]
                doc_text = vector_ranks[doc_id]["document"]
                similarity = 1.0 - vector_ranks[doc_id]["distance"]
            else:
                match_reason.append("Keyword Match")
                # Find in metadata/corpus by ID
                try:
                    idx = self.ids.index(doc_id)
                    metadata = self.metadata[idx]
                    doc_text = self.corpus[idx]
                except ValueError:
                    metadata = {}
                    doc_text = ""
                similarity = 0.5 # Default middle score for keyword only
                
            if doc_id in bm25_ranks and "Keyword Match" not in match_reason:
                match_reason.append("Keyword Match")
                
            paper = {
                "id": doc_id,
                "title": metadata.get("title", "No Title"),
                "abstract": metadata.get("abstract", "") or doc_text[:500] + "...",
                "authors": metadata.get("authors", ""),
                "published_date": metadata.get("published_date", ""),
                "year": metadata.get("published_date", "")[:4] if metadata.get("published_date") else "",
                "pdf_url": metadata.get("pdf_url", ""),
                "similarity": round(float(similarity), 3),
                "match_reason": " + ".join(match_reason),
                "hybrid_score": round(float(hybrid_score), 4)
            }
            retrieved_papers.append(paper)
            
        return retrieved_papers

if __name__ == "__main__":
    retriever = ResearchRetriever()
    res = retriever.retrieve("federated learning", top_k=3)
    for r in res:
        print(f"[{r['match_reason']}] {r['title']} (Score: {r['hybrid_score']})")
