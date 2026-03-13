import os
import chromadb
from sentence_transformers import SentenceTransformer

class ResearchRetriever:
    def __init__(self, db_path=None, model_name="BAAI/bge-large-en"):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'chroma')
        self.db_path = os.path.abspath(db_path)
        
        self.model = SentenceTransformer(model_name)
        
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_collection(name="research_papers")

    def retrieve(self, query: str, top_k: int = 10):
        query_embedding = self.model.encode(query, normalize_embeddings=True).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved_papers = []
        if results['metadatas'] and len(results['metadatas']) > 0:
            for i in range(len(results['metadatas'][0])):
                metadata = results['metadatas'][0][i]
                doc_text = results['documents'][0][i] if results['documents'] else ""
                
                paper = {
                    "title": metadata.get("title", ""),
                    "abstract": metadata.get("abstract", ""),
                    "authors": metadata.get("authors", ""),
                    "year": metadata.get("published_date", "")[:4] if metadata.get("published_date") else "",
                    "text": doc_text,
                    "distance": results['distances'][0][i] if 'distances' in results else None
                }
                retrieved_papers.append(paper)
                
        return retrieved_papers

if __name__ == "__main__":
    retriever = ResearchRetriever()
    res = retriever.retrieve("federated learning in healthcare", top_k=3)
    for r in res:
        print(r['title'], r['distance'])
