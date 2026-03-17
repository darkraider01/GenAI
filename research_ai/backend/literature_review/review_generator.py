from typing import List, Dict
import numpy as np
from umap import UMAP
from hdbscan import HDBSCAN
from utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
from rag.retriever import ResearchRetriever

class LiteratureReviewGenerator:
    def __init__(self, llm=None):
        self.retriever = ResearchRetriever()
        self.llm = llm or get_llm(temperature=0.3)
        self.prompt = PromptTemplate(
            template="""You are a senior research scientist and academic editor. 
            Generate a high-quality, formal, and deeply structured Literature Review that standardizes the provided thematic clusters into a cohesive narrative suitable for a university-level research report.

            Research Topic: {topic}
            
            Discovered Clusters (Themes) & Papers:
            {clusters_text}
            
            Instructions:
            1. Use a formal academic tone throughout.
            2. Integrate the papers into the narrative using in-text citations in the format: [Title, Year].
            3. Ensure each section is substantial and provides synthesis beyond mere listing.
            4. Focus on how the themes relate to one another and the overall topic.
            
            Write the formal Literature Review strictly using the following EXACT markdown sections:
            
            # Literature Review: {topic}
            
            ## 1. Executive Summary
            (A concise high-level overview of the current state of research in this domain).

            ## 2. Tech Stacks used by current papers
            (Identify and discuss the technical stacks, programming languages, frameworks, and specific model architectures utilized in the referenced research).
            
            ## 3. Thematic Analysis of Research
            (For each cluster provided, create a robust subsection. Synthesize the core contributions of the papers within the theme and discuss their collective impact).
            
            ## 4. Methodological Synthesis
            (Analyze and compare the methodologies, architectures, or frameworks used across the various themes).
            
            ## 5. Current Research Gaps and Limitations
            (Critically discuss the weaknesses, missing links, or unresolved issues in the current literature).
            
            ## 6. Conclusion & Future Directions
            (A final summary connecting the findings to actionable future research paths).
            
            ## 7. System Reasoning & Sources
            (Provide a short paragraph explaining *why* the system synthesized this review based on the retrieved themes, and explicitly list the top 3-5 guiding papers with their primary contributions).
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
            # SLIGHTLY REDUCED CONTEXT for reliability: 800 characters per abstract
            abstract_snips = "\n".join([f"- {p['title']} ({p.get('year', 'N/A')}): {p['abstract'][:800]}..." for p in group_papers])
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
            import traceback
            print(f"LLM Error: {traceback.format_exc()}")
            review_md = "Failed to generate review. Check LLM connection and logs."
            
        papers_used = [{"title": p.get("title"), "year": p.get("year", "Unknown"), "authors": p.get("authors", [])} for p in papers]
        
        return {
            "review": review_md,
            "clusters": cluster_data_for_ui,
            "papers_used": papers_used
        }
