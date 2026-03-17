import os
import json
from langchain_core.prompts import PromptTemplate
from utils.llm_factory import get_llm
from rag.retriever import ResearchRetriever

class MethodPlanner:
    def __init__(self, retriever=None, llm=None):
        self.retriever = retriever or ResearchRetriever()
        
        self.llm = llm or get_llm(temperature=0.2)
        
        prompt_template = """
        Identify the core scientific principles from the relevant papers and adapt them to solve the new research gap.
        
        New Research Topic: {topic}

        Relevant Papers Context:
        {context}

        Analyze the context to explicitly outline a scientific experiment including hardware constraints, datasets, state-of-the-art baselines, structural architectures, and ablation studies.
        
        Output MUST be structured EXACTLY in the following Markdown format:

        # Experimental Design

        ### Dataset Selection
        - (List suggested datasets based on literature)

        ### Baseline Models
        - (List specific baseline models to compare against)

        ### Proposed Architecture
        - (Describe the high-level architecture inspired by the context)

        ### Evaluation Metrics
        - (List rigorous evaluation metrics)

        ### Ablation Studies
        - (Suggest 1-2 ablation studies to prove component efficacy)

        ### Experimental Setup & Compute
        - (Suggest the required computational hardware and framework, e.g., PyTorch, 4xA100 GPUs)
        
        ### System Reasoning & Primary Sources
        - (Explain *why* this specific methodology was chosen based on the context).
        
        ### Primary Sources (Access Papers)
        - (CRITICAL: List the top 2-3 most influential papers provided as clickable Markdown links. Format: `[[Title]](URL)`).
        - (Example: `[[Attention Is All You Need]](https://arxiv.org/pdf/1706.03762v7)`)
        """
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["topic", "context"]
        )
        self.chain = self.prompt | self.llm
        
    def plan_methodology(self, topic: str):
        print(f"Retrieving context for topic: {topic}")
        papers = self.retriever.retrieve(topic, top_k=5)
        
        context_parts = []
        for i, p in enumerate(papers):
            title = p.get('title', 'Unknown Title')
            pdf_link = p.get('pdf_url', '')
            link_str = f" [Paper PDF URL: {pdf_link}]" if pdf_link else ""
            context_parts.append(f"Source {i+1}:\nTitle: {title}{link_str}\nAbstract: {p.get('abstract', '')}")
            
        context_str = "\n\n".join(context_parts)
        
        # In case no papers found or db is empty, context string might be empty
        if not context_str.strip():
            context_str = "No specific context available. Please rely on general knowledge."
            
        print("Generating methodology plan via LLM...")
        try:
            response = self.chain.invoke({
                "topic": topic,
                "context": context_str
            })
            content = response.content
            if isinstance(content, list):
                content = content[0].get("text", str(content))
            
            return {
                "topic": topic,
                "plan_markdown": content,
                "context_papers": papers
            }
        except Exception as e:
            print(f"LLM Error: {e}")
            plan = "### Suggested Dataset\n- Placeholder\n### Baseline Models\n- Placeholder\n### Evaluation Metrics\n- Placeholder\n### Experimental Steps\n1. Placeholder"
            return {
                "topic": topic,
                "plan_markdown": plan,
                "source_papers": papers
            }

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    planner = MethodPlanner()
    result = planner.plan_methodology("Federated Learning + Medical Imaging -> Potential research topic")
    print(result["plan_markdown"])
