from typing import List, Dict
import numpy as np
from umap import UMAP
from hdbscan import HDBSCAN
from backend.utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
from backend.rag.retriever import ResearchRetriever

class LiteratureReviewGenerator:
    def __init__(self, llm=None):
        self.retriever = ResearchRetriever()
        self.llm = llm or get_llm(temperature=0.3)
        self.prompt = PromptTemplate(
            template="""You are an expert academic summarizing a clustered literature corpus.
            Generate a formal, structured Literature Review survey mapping the provided clusters of recent papers.
            
            Research Topic: {topic}
            
            Discovered Clusters (Themes) & Papers:
            {clusters_text}
            
            Write the formal Literature Review strictly using the following EXACT markdown sections:
            
            # Literature Review: {topic}
            
            ## 1. Introduction
            (1-2 paragraphs summarizing the overarching context).
            
            ## 2. Major Research Themes
            (For each cluster provided, create a subsection detailing its thematic focus and citing its key papers).
            
            ## 3. Methodological Approaches
            (Synthesize the prominent methods/architectures seen across these themes).
            
            ## 4. Current Limitations
            (Discuss weaknesses apparent in these approaches).
            
            ## 5. Open Research Challenges
            (Future outlook connecting the limitations into actionable next steps).
            """,
            input_variables=["topic", "clusters_text"]
        )

    def generate(self, topic: str) -> Dict:
        print(f"Retrieving top 30 papers for literature review on: {topic}")
        # Step 1: Retrive up to 30 papers
        papers = self.retriever.retrieve(topic, top_k=30)
        
        if not papers:
            return {"review": "Not enough papers found for this topic.", "clusters": [], "papers_used": []}
            
        # Step 2: Re-cluster to find specific local themes instead of global DB clusters
        from sentence_transformers import SentenceTransformer
        # Use simple miniLM for fast local clustering of the 30 abstracts
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        abstracts = [p.get("abstract", "") for p in papers]
        
        print("Generating local embeddings for 30 papers...")
        embeddings = embedder.encode(abstracts)
        
        print("Clustering via UMAP + HDBSCAN...")
        n_neighbors = min(15, len(embeddings) - 1) if len(embeddings) > 2 else 2
        umap_model = UMAP(n_neighbors=n_neighbors, n_components=min(5, len(embeddings)), min_dist=0.0, metric='cosine', random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=min(3, max(2, len(embeddings)//5)), metric='euclidean', cluster_selection_method='eom')
        
        try:
            reduced = umap_model.fit_transform(embeddings)
            clusters = hdbscan_model.fit_predict(reduced)
        except Exception as e:
            print("Clustering failed, using single cluster wildcard.", e)
            clusters = [0] * len(embeddings)
            
        groups = {}
        for idx, cluster_id in enumerate(clusters):
            c_str = f"Theme_{cluster_id}" if cluster_id != -1 else "Miscellaneous"
            if c_str not in groups:
                groups[c_str] = []
            groups[c_str].append(papers[idx])
            
        cluster_summaries = []
        cluster_data_for_ui = []
        
        for theme, group_papers in groups.items():
            abstract_snips = "\n".join([f"- {p['title']}: {p['abstract'][:200]}..." for p in group_papers])
            cluster_summaries.append(f"### {theme}\nPapers:\n{abstract_snips}\n")
            
            cluster_data_for_ui.append({
                "theme_name": theme,
                "paper_count": len(group_papers),
                "titles": [p['title'] for p in group_papers]
            })
            
        clusters_text = "\n\n".join(cluster_summaries)
        
        # Step 3: Generate Structured Lit Review
        print("Piping to LLM for survey synthesis...")
        chain = self.prompt | self.llm
        try:
            res = chain.invoke({"topic": topic, "clusters_text": clusters_text})
            review_md = res.content
        except Exception as e:
            print("LLM Errl", e)
            review_md = "Failed to generate review. Check LLM."
            
        papers_used = [{"title": p.get("title"), "year": p.get("year", "Unknown"), "authors": p.get("authors", [])} for p in papers]
        
        return {
            "review": review_md,
            "clusters": cluster_data_for_ui,
            "papers_used": papers_used
        }
