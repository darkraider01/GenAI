import json
import re
import os

def clean_text(text):
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove references section
    text = re.split(r'\breferences\b|\bbibliography\b', text, maxsplit=1)[0]
    
    # Remove latex equations
    text = re.sub(r'\$.*?\$', '', text)  # inline math
    text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', text, flags=re.DOTALL) # display math
    
    # Remove special characters (keep alphanumeric, space, basic punctuation)
    text = re.sub(r'[^a-z0-9\s.,?!-]', ' ', text)
    
    # Extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_papers():
    input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw_papers', 'arxiv_papers.json')
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'clean_papers.json')
    
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Loading raw papers from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            papers = json.load(f)
    except FileNotFoundError:
        print("Raw papers not found. Run fetch_arxiv.py first.")
        return
        
    cleaned_papers = []
    
    for p in papers:
        c_p = p.copy()
        c_title = clean_text(p.get("title", ""))
        c_abstract = clean_text(p.get("abstract", ""))
        c_p["document_text"] = f"{c_title} {c_abstract}".strip()
        cleaned_papers.append(c_p)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_papers, f, indent=4, ensure_ascii=False)
        
    print(f"Processed {len(cleaned_papers)} papers and saved to {output_path}")

    # S3 upload (additive — does not affect local pipeline)
    try:
        from utils.storage_manager import storage
        storage.upload_file(output_path, "processed/clean_papers.json")
    except Exception:
        pass  # S3 is optional; local file is the source of truth

if __name__ == "__main__":
    preprocess_papers()
