import os
import sys
import json
import pandas as pd
import numpy as np
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Standardize path for backend imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

DOMAIN_STOPWORDS = {
    "paper", "method", "result", "approach", "study", 
    "propose", "proposed", "dataset", "model", "analysis"
}

METHOD_KEYWORDS = [
    "transformer", "cnn", "diffusion", "reinforcement", "contrastive", 
    "federated", "graph", "gan", "lstm", "gnn", "llm", "prompt", "agent"
]

def clean_text(text):
    text = text.lower()
    tokens = text.split()
    tokens = [t for t in tokens if t not in ENGLISH_STOP_WORDS and t not in DOMAIN_STOPWORDS]
    tokens = [t for t in tokens if len(t) > 3]
    return " ".join(tokens)

def analyze_trends():
    embeddings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'embeddings', 'embedded_papers.json')
    embeddings_path = os.path.abspath(embeddings_path)
    
    try:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Embeddings not found. Run ingestion pipeline first.")
        return []
        
    if not data:
        return []

    documents = [clean_text(d["text"]) for d in data]
    embeddings = np.array([d["embedding"] for d in data])
    
    # Extract years
    years = []
    for d in data:
        pub_date = d["metadata"].get("published_date", "")
        # Very basic parse for year assuming ISO format YYYY-MM-DD
        year = pub_date[:4] if pub_date else "2024" 
        try:
            years.append(int(year))
        except ValueError:
            years.append(2024)
            
    # UMAP dimensionality reduction
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    
    # HDBSCAN clustering
    hdbscan_model = HDBSCAN(min_cluster_size=15, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
    
    # BERTopic
    topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, calculate_probabilities=False)
    
    print("Fitting BERTopic model with embeddings...")
    topics, probs = topic_model.fit_transform(documents, embeddings)
    
    topic_info = topic_model.get_topic_info()
    
    # Calculate advanced metrics per topic
    df = pd.DataFrame({
        "topic": topics,
        "year": years,
        "embedding": list(embeddings),
        "document": documents
    })
    
    freq = df.groupby(['topic', 'year']).size().unstack(fill_value=0)
    
    advanced_metrics = {}
    for topic in freq.index:
        if topic == -1: # Outlier topic
            continue
            
        topic_years = sorted(freq.columns)
        counts = [int(freq.loc[topic, y]) for y in topic_years]
        
        # 1. Growth Rate (Slope)
        if len(topic_years) >= 2:
            slope = np.polyfit(topic_years, counts, 1)[0]
            growth = slope
        elif len(topic_years) == 1:
            growth = counts[0]
        else:
            growth = 0
            
        topic_df = df[df['topic'] == topic].sort_values(by='year')
        
        # 2. Citation Velocity Equivalent (Using count velocity as proxy if missing citations)
        # We will assume a random distribution of citations since it wasn't extracted, 
        # or calculate based on count momentum:
        if len(topic_years) >= 2:
            citation_velocity = (counts[-1] - counts[-2]) * 5.0 # mock multiplying for scale
        else:
            citation_velocity = 0
            
        # 3. Novelty Emergence
        embedding_shift = 0.0
        if len(topic_df) >= 2:
            mid = len(topic_df) // 2
            first_half = np.mean(topic_df.iloc[:mid]['embedding'].tolist(), axis=0)
            second_half = np.mean(topic_df.iloc[mid:]['embedding'].tolist(), axis=0)
            # cosine distance
            embedding_shift = 1.0 - (np.dot(first_half, second_half) / (np.linalg.norm(first_half) * np.linalg.norm(second_half) + 1e-10))
            
        # 4. Trend Classification
        trend_type = "Stable Research Area"
        if growth > 1.5 and citation_velocity > 10 and embedding_shift > 0.1:
            trend_type = "Breakthrough Topic"
        elif growth > 0.5 and citation_velocity > 0:
            trend_type = "Emerging Trend"
        elif growth < -0.5:
            trend_type = "Declining Topic"
        # 5. Method Detection
        # Track frequency of METHOD_KEYWORDS over the years 
        topic_methods = {yr: {m: 0 for m in METHOD_KEYWORDS} for yr in topic_years}
        for _, row in topic_df.iterrows():
            text = str(row['document']).lower()
            yr = row['year']
            for m in METHOD_KEYWORDS:
                if m in text:
                    topic_methods[yr][m] += 1
                    
        # Find shifting methods (most frequent in the last year compared to first)
        methodological_shift = "No clear shift detected."
        if len(topic_years) >= 2:
            first_yr, last_yr = topic_years[0], topic_years[-1]
            first_counts = topic_methods[first_yr]
            last_counts = topic_methods[last_yr]
            rising_methods = [m for m in METHOD_KEYWORDS if last_counts[m] > first_counts[m]]
            falling_methods = [m for m in METHOD_KEYWORDS if first_counts[m] > 0 and last_counts[m] <= first_counts[m]]
            
            if rising_methods:
                methodological_shift = f"Shift towards {', '.join(rising_methods[:3])}"
                if falling_methods:
                    methodological_shift += f" away from {', '.join(falling_methods[:2])}"
            
        # 6. Evolution Timeline (New)
        # We track how keywords evolve for this topic over time
        evolution_timeline = []
        if len(topic_years) >= 2:
            for yr in topic_years:
                yr_docs = topic_df[topic_df['year'] == yr]['document'].tolist()
                # Simple keyword extraction for this year
                from sklearn.feature_extraction.text import CountVectorizer
                cv = CountVectorizer(stop_words='english', max_features=5)
                try:
                    cv.fit(yr_docs)
                    yr_keywords = list(cv.vocabulary_.keys())
                    evolution_timeline.append(f"{yr}: {', '.join(yr_keywords)}")
                except:
                    pass
        
        advanced_metrics[topic] = {
            "growth_rate": float(growth),
            "citation_velocity": float(citation_velocity),
            "novelty_shift": float(embedding_shift),
            "methodological_shift": methodological_shift,
            "evolution_timeline": " | ".join(evolution_timeline),
            "trend_type": trend_type
        }
        
    topic_info["growth_rate"] = topic_info["Topic"].apply(lambda x: advanced_metrics.get(x, {}).get("growth_rate", 0))    
    topic_info["trend_type"] = topic_info["Topic"].apply(lambda x: advanced_metrics.get(x, {}).get("trend_type", "Unknown"))
    topic_info["methodological_shift"] = topic_info["Topic"].apply(lambda x: advanced_metrics.get(x, {}).get("methodological_shift", ""))
    topic_info["evolution_timeline"] = topic_info["Topic"].apply(lambda x: advanced_metrics.get(x, {}).get("evolution_timeline", ""))

    
    emerging_topics = topic_info[topic_info["Topic"] != -1].sort_values(by="growth_rate", ascending=False)
    
    llm = get_llm(temperature=0.2)
    prompt = PromptTemplate(
        template="""You are an expert AI Research Analyst formulating a Temporal Evolution Report.
        Given the following data about a topic cluster, produce an exact structured Research Landscape Analysis.
        
        Topic Core Keywords: {keywords}
        Trend Classification: {trend_type}
        Methodological Shift: {shift}
        Topic Growth Metric: {growth}
        Evolution Timeline: {evolution}
        
        Output format exactly as:
        
        ### Research Landscape Analysis
        
        **Topic:** (Generate a concise 3-5 word name for this research area based on the keywords)
        
        **Trend Classification:** {trend_type}
        
        **Research Evolution:**
        (Describe the progression from the timeline: {evolution})
        
        **Key Methodological Shift:** 
        (Explain the shift contextually: {shift})
        
        **Growth Momentum:**
        (Mention the growth metric: {growth} slope acceleration)
        
        **Dominant Research Themes:**
        - (bullet exactly 3 dominant sub-themes inferred from the keywords)
        """,
        input_variables=["keywords", "trend_type", "shift", "growth", "evolution"]
    )
    chain = prompt | llm

    results = []
    for _, row in emerging_topics.iterrows():
        t_id = row["Topic"]
        keyword_list = [word for word, _ in topic_model.get_topic(t_id)]
        
        try:
            kw_str = ", ".join(keyword_list)
            response = chain.invoke({
                "keywords": kw_str, 
                "trend_type": row.get("trend_type", "Unknown"), 
                "shift": row.get("methodological_shift", "Unknown"), 
                "growth": f"{row['growth_rate']:.2f}",
                "evolution": row.get("evolution_timeline", "Initial exploration phase.")
            })
            insight_report = response.content.strip()
            
            # Try to extract just the Topic Name from the report for easy UI mapping
            topic_name_line = [line for line in insight_report.split('\n') if '**Topic:**' in line]
            topic_name = topic_name_line[0].replace('**Topic:**', '').strip() if topic_name_line else ", ".join(keyword_list[:3])
            
        except Exception as e:
            print("Failed to generate insight report:", e)
            topic_name = ", ".join(keyword_list[:3])
            insight_report = f"Topic: {topic_name}"
            
        # 7. Collect Representative Papers (New)
        # We take the top papers that contributed most to this topic cluster
        # For simplicity, we'll take top papers based on their inclusion in this topic
        topic_paper_indices = [i for i, t in enumerate(topics) if t == t_id]
        topic_papers = []
        for idx in topic_paper_indices[:5]: # Take top 5 for selection
            p = data[idx]
            if p["metadata"].get("pdf_url"):
                topic_papers.append({
                    "title": p["metadata"].get("title", "Unknown"),
                    "url": p["metadata"].get("pdf_url")
                })
        
        results.append({
            "topic_id": t_id,
            "topic_name": topic_name,
            "trend_type": row.get("trend_type", "Unknown"),
            "insight_report": insight_report,
            "keywords": keyword_list,
            "papers_in_topic": int(row["Count"]),
            "growth_rate": float(row["growth_rate"]),
            "representative_papers": topic_papers[:3] # Keep top 3
        })
        
    print(f"Discovered {len(results)} emerging topics.")
    return results

if __name__ == "__main__":
    trends = analyze_trends()
    if trends:
        for t in trends[:5]:
            print(f"Topic {t['topic_id']} | Growth: {t['growth_rate']} | Keywords: {', '.join(t['keywords'])}")
