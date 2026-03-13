import json
import os
from sentence_transformers import SentenceTransformer

def embed_papers():
    input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'clean_papers.json')
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
    
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Loading cleaned papers from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
    except FileNotFoundError:
        print("Cleaned papers not found. Run preprocess.py first.")
        return
        
    # BAAI/bge-large-en
    model_name = "BAAI/bge-large-en"
    print(f"Loading model {model_name}...")
    model = SentenceTransformer(model_name)
    
    print("Embedding document texts...")
    embedded_data = []
    texts = [p["document_text"] for p in papers]
    
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    for i, p in enumerate(papers):
        embedded_data.append({
            "id": p["paper_id"],
            "embedding": embeddings[i].tolist(),
            "metadata": {
                "title": p.get("title", ""),
                "abstract": p.get("abstract", ""),
                "authors": ",".join(p.get("authors", [])),
                "categories": ",".join(p.get("categories", [])),
                "published_date": p.get("published_date", ""),
                "pdf_url": p.get("pdf_url", "")
            },
            "text": p["document_text"]
        })
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(embedded_data, f, indent=4, ensure_ascii=False)
        
    print(f"Embedded {len(embedded_data)} papers and saved to {output_path}")

if __name__ == "__main__":
    embed_papers()
