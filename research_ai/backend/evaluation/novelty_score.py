import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class NoveltyScorer:
    def __init__(self, model_name="BAAI/bge-large-en"):
        self.model = SentenceTransformer(model_name)
        
        embeddings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
        self.embeddings_path = os.path.abspath(embeddings_path)
        
        self.papers_data = []
        try:
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                self.papers_data = json.load(f)
        except FileNotFoundError:
            print("Embeddings not found. Ensure ingestion pipeline is run.")
            
        if self.papers_data:
            self.paper_embeddings = np.array([d["embedding"] for d in self.papers_data])
        else:
            self.paper_embeddings = np.array([])
            
    def score_novelty(self, proposal_text: str):
        if len(self.papers_data) == 0:
            return {"novelty_score": 1.0, "closest_paper": None, "max_similarity": 0.0}
            
        print("Embedding proposal text...")
        if isinstance(proposal_text, list) and len(proposal_text) > 0 and isinstance(proposal_text[0], dict):
            proposal_text = proposal_text[0].get("text", str(proposal_text))
        proposal_text = str(proposal_text)
        proposal_embedding = self.model.encode(proposal_text, normalize_embeddings=True)
        
        print("Computing similarities against paper database...")
        sims = cosine_similarity([proposal_embedding], self.paper_embeddings)[0]
        
        max_idx = np.argmax(sims)
        max_similarity = float(sims[max_idx])
        novelty_score = 1.0 - max_similarity
        
        closest_paper = self.papers_data[max_idx]["metadata"].copy()
        closest_paper["id"] = self.papers_data[max_idx]["id"]
        
        return {
            "novelty_score": novelty_score,
            "max_similarity": max_similarity,
            "closest_paper": closest_paper
        }

if __name__ == "__main__":
    scorer = NoveltyScorer()
    res = scorer.score_novelty("This is a brand new approach to AI in healthcare using quantum computing to accelerate convergence.")
    print(res)
