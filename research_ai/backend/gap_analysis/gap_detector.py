import os
import sys
import pickle
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Standardize path for backend imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from trend_analysis.topic_model import analyze_trends, clean_text
from utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

def detect_gaps(similarity_threshold=0.75, max_cross_citations=2, query_topic=None):
    # This function assumes we have embeddings and a citation graph
    graph_out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'graphs')
    graph_path = os.path.join(graph_out_dir, 'citation_graph.gpickle')
    embeddings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
    
    try:
        if os.path.exists(graph_path):
            with open(graph_path, 'rb') as f:
                G = pickle.load(f)
        else:
            print(f"Citation graph not found at {graph_path}. Proceeding with semantic-only analysis.")
            G = None
            
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            papers_data = json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}. Ensure ingestion is complete.")
        return []
        
    print(f"Running Gap Analysis (Topic: {query_topic or 'Global Discovery'})...")
    from umap import UMAP
    from hdbscan import HDBSCAN
    from bertopic import BERTopic
    
    # Filter by topic if provided
    if query_topic:
        llm_temp = get_llm(temperature=0)
        topic_embedding = None
        try:
            # We use the first paper's embedding model or a generic one if we can extract it
            # Actually, standard ResearchRetriever can get embeddings if we had it, 
            # but let's just use cosine on existing embeddings vs a keyword matching or simple similarity
            # For simplicity, if query_topic is provided, we filter top 300 relevant papers
            from sklearn.feature_extraction.text import TfidfVectorizer
            corpus = [clean_text(d["text"]) for d in papers_data]
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(corpus)
            query_vec = vectorizer.transform([clean_text(query_topic)])
            from sklearn.metrics.pairwise import linear_kernel
            cosine_similarities = linear_kernel(query_vec, tfidf_matrix).flatten()
            related_indices = cosine_similarities.argsort()[:-300:-1] # Top 300
            papers_data = [papers_data[i] for i in related_indices if cosine_similarities[i] > 0]
            
            if len(papers_data) < 20:
                print("Too few papers found for topic-specific gap detection. Falling back to global with topic emphasis.")
                # We'll just continue with original data but maybe weight the gap score later
        except Exception as e:
            print(f"Topic filtering failed: {e}. Continuing with Global.")

    documents = [clean_text(d["text"]) for d in papers_data]
    embeddings = np.array([d["embedding"] for d in papers_data])
    ids = [d["id"] for d in papers_data]
    
    # Add randomness to UMAP to ensure different clusters on repeats
    import random
    rand_state = random.randint(1, 1000)
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.1, metric='cosine', random_state=rand_state)
    hdbscan_model = HDBSCAN(min_cluster_size=10, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, calculate_probabilities=False)
    
    try:
        topics, _ = topic_model.fit_transform(documents, embeddings)
    except Exception as e:
        print(f"Clustering failed: {e}")
        return []
    
    from trend_analysis.topic_model import analyze_trends
    trends_list = analyze_trends() 
    topic_momentum = {t['topic_id']: t['growth_rate'] for t in trends_list}
    
    topic_papers = {}
    for i, t in enumerate(topics):
        if t == -1: continue
        if t not in topic_papers:
            topic_papers[t] = []
        topic_papers[t].append(i)
        
    centroids = {}
    for t, indices in topic_papers.items():
        cluster_embeddings = embeddings[indices]
        centroid = np.mean(cluster_embeddings, axis=0)
        centroids[t] = centroid
        
    topic_ids = list(centroids.keys())
    
    if len(topic_ids) < 2:
        return []
        
    centroid_matrix = np.array([centroids[t] for t in topic_ids])
    sim_matrix = cosine_similarity(centroid_matrix)
    
    # Calculate cross citations if graph exists
    all_cross_citations = []
    if G:
        for i in range(len(topic_ids)):
            for j in range(i + 1, len(topic_ids)):
                t1, t2 = topic_ids[i], topic_ids[j]
                pids1 = set([ids[idx] for idx in topic_papers[t1]])
                pids2 = set([ids[idx] for idx in topic_papers[t2]])
                
                c = 0
                for node in pids1:
                    if node in G:
                        neighbors = set(G.successors(node)) | set(G.predecessors(node))
                        c += len(neighbors.intersection(pids2))
                for node in pids2:
                    if node in G:
                        neighbors = set(G.successors(node)) | set(G.predecessors(node))
                        c += len(neighbors.intersection(pids1))
                all_cross_citations.append(c // 2)
    
    max_cites = max(all_cross_citations) if all_cross_citations and max(all_cross_citations) > 0 else 1
    
    gaps = []
    for i in range(len(topic_ids)):
        for j in range(i + 1, len(topic_ids)):
            sim = sim_matrix[i, j]
            if sim >= similarity_threshold:
                t1, t2 = topic_ids[i], topic_ids[j]
                kw1 = ", ".join([w for w, _ in topic_model.get_topic(t1)][:5])
                kw2 = ", ".join([w for w, _ in topic_model.get_topic(t2)][:5])
                
                cross_citations = 0
                if G:
                    pids1 = set([ids[idx] for idx in topic_papers[t1]])
                    pids2 = set([ids[idx] for idx in topic_papers[t2]])
                    for node in pids1:
                        if node in G:
                            cross_citations += len(set(G.successors(node)).intersection(pids2))
                    for node in pids2:
                        if node in G:
                            cross_citations += len(set(G.successors(node)).intersection(pids1))
                    cross_citations = cross_citations // 2
                
                normalized_cites = cross_citations / max_cites if G else 0
                jitter = random.uniform(0, 0.4) # Increased jitter for variety
                gap_score = float(sim) + (float(topic_momentum.get(t1, 0)) * 0.1) + (float(topic_momentum.get(t2, 0)) * 0.1) - normalized_cites + jitter
                
                gaps.append({
                    "t1": t1,
                    "t2": t2,
                    "t1_keywords": kw1,
                    "t2_keywords": kw2,
                    "similarity": float(sim),
                    "cross_citations": cross_citations,
                    "gap_score": gap_score,
                    "inferred_type": "Cross-Domain Gap"
                })
                    
    # Sort by gap_score descending and pick top 30, then shuffle and pick 6
    gaps = sorted(gaps, key=lambda x: x["gap_score"], reverse=True)[:30]
    random.shuffle(gaps)
    gaps = gaps[:6]
    
    # Enrich gaps with LLM Topic generation
    llm = get_llm(temperature=0.7) # Higher temperature for variety in descriptions
    topic_context = f" within the domain of '{query_topic}'" if query_topic else ""
    prompt = PromptTemplate(
        template="""You are the Chief Research Strategist at a leading AI Research Lab.
        Your goal is to identify a high-value 'Research Niche'{topic_context}—a specific gap where two trending fields overlap but haven't been fully explored.
        
        Field 1 Keywords: {kw1}
        Field 2 Keywords: {kw2}
        Current Momentum Classification: {inferred_type}
        
        Output EXACTLY in this markdown format:
        **Research Niche:** (A bold, professional 3-7 word name for the niche)
        **Primary Connection:** (1 sentence explaining the semantic link between {kw1} and {kw2})
        
        **The Research Gap:**
        (Explain what is missing from current literature that sits in this overlap)
        
        **Recommended Research Ideas:**
        - **Project Alpha:** (A specific, actionable research project title and 1-sentence description)
        - **Project Beta:** (Another specific research project title and 1-sentence description)
        
        **Impact Potential:**
        (Why this is a hot topic for publication or funding)
        """,
        input_variables=["kw1", "kw2", "inferred_type", "topic_context"]
    )
    chain = prompt | llm
    
    enriched_gaps = []
    for g in gaps:
        try:
            response = chain.invoke({
                "kw1": g["t1_keywords"], 
                "kw2": g["t2_keywords"],
                "inferred_type": g["inferred_type"],
                "topic_context": topic_context
            })
            gap_description = response.content.strip()
        except Exception as e:
            gap_description = f"**Research Niche:** {g['inferred_type']} in {g['t1_keywords']} vs {g['t2_keywords']}\n**Current Momentum Classification:** {g['inferred_type']}\n\n**The Research Gap:** High similarity yet low interaction."
            
        # Extract supporting papers for this gap
        t1, t2 = g["t1"], g["t2"]
        t1_pids = [ids[idx] for idx in topic_papers[t1]][:3]
        t2_pids = [ids[idx] for idx in topic_papers[t2]][:3]
        
        supporting_papers = []
        for pid in (t1_pids + t2_pids):
            # Find the paper in the original data by id
            for p in papers_data:
                if p["id"] == pid:
                    paper = {
                        "title": p.get("metadata", {}).get("title", "Unknown"),
                        "authors": p.get("metadata", {}).get("authors", "Unknown"),
                        "pdf_url": p.get("metadata", {}).get("pdf_url", "")
                    }
                    if paper not in supporting_papers:
                        supporting_papers.append(paper)
                    break

        enriched_gaps.append({
            "gap_description": gap_description,
            "gap_type": g["inferred_type"],
            "similarity": float(g["similarity"]),
            "cross_citations": g["cross_citations"],
            "gap_score": g["gap_score"],
            "t1_keywords": g["t1_keywords"],
            "t2_keywords": g["t2_keywords"],
            "t1_density": len(topic_papers[t1]),
            "t2_density": len(topic_papers[t2]),
            "supporting_papers": supporting_papers[:5] # Max 5 supporting papers
        })

    print(f"Found {len(enriched_gaps)} potential research gaps.")
    return enriched_gaps

    print(f"Found {len(enriched_gaps)} potential research gaps.")
    return enriched_gaps

if __name__ == "__main__":
    potential_gaps = detect_gaps()
    for g in potential_gaps[:5]:
        print(f"Gap: {g['gap_description']} | Sim: {g['similarity']:.2f} | Cross-Cites: {g['cross_citations']}")
