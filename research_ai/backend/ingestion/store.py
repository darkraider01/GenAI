import json
import os
import chromadb

def store_papers():
    input_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'chroma')
    
    input_path = os.path.abspath(input_path)
    db_path = os.path.abspath(db_path)
    
    os.makedirs(db_path, exist_ok=True)
    
    print(f"Loading embedded papers from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            embedded_data = json.load(f)
    except FileNotFoundError:
        print("Embedded papers not found. Run embed.py first.")
        return
        
    print(f"Initializing ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    collection_name = "research_papers"
    print(f"Getting or creating collection '{collection_name}'...")
    collection = client.get_or_create_collection(name=collection_name)
    
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for item in embedded_data:
        ids.append(item["id"])
        embeddings.append(item["embedding"])
        
        # ChromaDB metadata values must be strings, ints, floats or bools
        clean_metadata = {}
        for k, v in item["metadata"].items():
            if isinstance(v, (str, int, float, bool)):
                clean_metadata[k] = v
            elif v is None:
                clean_metadata[k] = ""
            else:
                clean_metadata[k] = str(v)
                
        metadatas.append(clean_metadata)
        documents.append(item["text"])
        
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end_idx = min(i + batch_size, len(ids))
        collection.upsert(
            ids=ids[i:end_idx],
            embeddings=embeddings[i:end_idx],
            metadatas=metadatas[i:end_idx],
            documents=documents[i:end_idx]
        )
        print(f"Inserted {end_idx}/{len(ids)} papers...")
        
    print("Successfully stored all papers in ChromaDB.")

if __name__ == "__main__":
    store_papers()
