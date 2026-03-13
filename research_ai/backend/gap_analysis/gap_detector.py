import os
import pickle
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.trend_analysis.topic_model import analyze_trends, clean_text
from backend.utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

def detect_gaps(similarity_threshold=0.75, max_cross_citations=2):
    # This function assumes we have embeddings and a citation graph
    graph_out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'db', 'graphs')
    graph_path = os.path.join(graph_out_dir, 'citation_graph.gpickle')
    embeddings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
    
    try:
        with open(graph_path, 'rb') as f:
            G = pickle.load(f)
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            papers_data = json.load(f)
    except FileNotFoundError:
        print("Data files not found. Ensure ingestion and citation graph are built.")
        return []
        
    print("Running Trend Analysis to get topics...")
    # NOTE: In a real orchestrated environment, we'd pass the topic model state
    # rather than recomputing it. For demonstration we'll recompute basic clusters.
    from umap import UMAP
    from hdbscan import HDBSCAN
    from bertopic import BERTopic
    
    documents = [clean_text(d["text"]) for d in papers_data]
    embeddings = np.array([d["embedding"] for d in papers_data])
    ids = [d["id"] for d in papers_data]
    
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, calculate_probabilities=False)
    
    topics, _ = topic_model.fit_transform(documents, embeddings)
    print("Matching topics against embedded papers...")
    # Calculate topic momentum from topic_info
    # For demonstration, we'll re-run analyze_trends to get topic_info with growth_rate
    # In a real system, this would be passed or retrieved.
    from backend.trend_analysis.topic_model import analyze_trends
    trends_list = analyze_trends() 
    topic_momentum = {t['topic_id']: t['growth_rate'] for t in trends_list}
    
    # Group papers by topic
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
        print("Not enough topics to find gaps.")
        return []
        
    centroid_matrix = np.array([centroids[t] for t in topic_ids])
    sim_matrix = cosine_similarity(centroid_matrix)
    
    # Pre-calculate max citations for normalization
    all_cross_citations = []
    for i in range(len(topic_ids)):
        for j in range(i + 1, len(topic_ids)):
            t1 = topic_ids[i]
            t2 = topic_ids[j]
            idx1 = topic_papers[t1]
            idx2 = topic_papers[t2]
            pids1 = set([ids[idx] for idx in idx1])
            pids2 = set([ids[idx] for idx in idx2])
            
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
                t1 = topic_ids[i]
                t2 = topic_ids[j]
                
                # Check cross citations
                idx1 = topic_papers[t1]
                idx2 = topic_papers[t2]
                
                pids1 = set([ids[idx] for idx in idx1])
                pids2 = set([ids[idx] for idx in idx2])
                
                cross_citations = 0
                for node in pids1:
                    if node in G:
                        neighbors = set(G.successors(node)) | set(G.predecessors(node))
                        cross_citations += len(neighbors.intersection(pids2))
                        
                for node in pids2:
                    if node in G:
                        neighbors = set(G.successors(node)) | set(G.predecessors(node))
                        cross_citations += len(neighbors.intersection(pids1))
                        
                # We double counted undirected edges equivalent
                cross_citations = cross_citations // 2
                
                # Gap Score calculation (Similarity + Momentum - Citations)
                m1 = topic_momentum.get(t1, 0)
                m2 = topic_momentum.get(t2, 0)
                normalized_cites = cross_citations / max_cites
                gap_score = float(sim) + (float(m1) * 0.1) + (float(m2) * 0.1) - normalized_cites
                
                # Heuristics for typing the gap
                kw1 = ", ".join([w for w, _ in topic_model.get_topic(t1)][:5])
                kw2 = ", ".join([w for w, _ in topic_model.get_topic(t2)][:5])
                combined_kw = kw1 + " " + kw2
                
                inferred_type = "Cross-Domain Gap"
                if "dataset" in combined_kw or "benchmark" in combined_kw:
                    inferred_type = "Dataset/Benchmark Gap"
                elif any(m in combined_kw for m in ["cnn", "transformer", "gnn", "diffusion", "method", "model"]):
                    inferred_type = "Methodological Gap"
                
                # Store data to enrich later
                gaps.append({
                    "t1_keywords": kw1,
                    "t2_keywords": kw2,
                    "similarity": float(sim),
                    "cross_citations": cross_citations,
                    "gap_score": gap_score,
                    "inferred_type": inferred_type
                })
                    
    # Sort by gap_score descending
    gaps = sorted(gaps, key=lambda x: x["gap_score"], reverse=True)[:10]  # Top 10 gaps
    
    # Enrich gaps with LLM Topic generation
    llm = get_llm(temperature=0.2)
    prompt = PromptTemplate(
        template="""You are the Lead Scientific Director allocating research funding.
        Identify the multidimensional research gap between these two topic clusters.
        
        Topic 1 Keywords: {kw1}
        Topic 2 Keywords: {kw2}
        System Classification: {inferred_type}
        
        Output EXACTLY in this markdown format:
        **Gap Name:** (Give it a bold 3-5 word name)
        **Gap Type:** {inferred_type}
        
        **Observation:**
        (Briefly explain why these two fields are currently disconnected in the literature)
        
        **Opportunity:**
        (Briefly assert the high-impact research opportunity unifying them)
        """,
        input_variables=["kw1", "kw2", "inferred_type"]
    )
    chain = prompt | llm
    
    enriched_gaps = []
    for g in gaps:
        try:
            response = chain.invoke({
                "kw1": g["t1_keywords"], 
                "kw2": g["t2_keywords"],
                "inferred_type": g["inferred_type"]
            })
            gap_description = response.content.strip()
        except Exception as e:
            gap_description = f"**Gap Name:** {g['inferred_type']} in {g['t1_keywords']} vs {g['t2_keywords']}\n**Gap Type:** {g['inferred_type']}\n\n**Observation:** High similarity ({g['similarity']:.2f}) but low cross citations ({g['cross_citations']}).\n\n**Opportunity:** Combine the approaches."
            
        enriched_gaps.append({
            "gap_description": gap_description,
            "gap_type": g["inferred_type"],
            "similarity": float(g["similarity"]),
            "cross_citations": g["cross_citations"],
            "gap_score": g["gap_score"]
        })

    print(f"Found {len(enriched_gaps)} potential research gaps.")
    return enriched_gaps

if __name__ == "__main__":
    potential_gaps = detect_gaps()
    for g in potential_gaps[:5]:
        print(f"Gap: {g['gap_description']} | Sim: {g['similarity']:.2f} | Cross-Cites: {g['cross_citations']}")
