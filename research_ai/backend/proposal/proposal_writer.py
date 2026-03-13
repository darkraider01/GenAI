import os
import re
from langchain_core.prompts import PromptTemplate
from backend.utils.llm_factory import get_llm
from fpdf import FPDF

class ProposalWriter:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.3)
        
        prompt_template = """
        You are an elite academic grant proposal writer for high-tier peer-reviewed conferences (e.g., IEEE, CVPR, NeurIPS).
        Based on the provided Research Topic, Methodology Plan, and Context Papers, generate an exhaustive, highly formal grant proposal.
        
        CRITICAL STYLE RULES:
        - Absolute adherence to formal academic writing tone. Never use conversational language (e.g., "This project tries to"). 
        - Instead, use rigorous phrasing (e.g., "This research aims to develop a principled architecture for...").
        - Always cite explicitly from the Context Papers using bracketed numbers, e.g., [1], [2].
        - Acknowledge potential limitations within your methodology.

        Research Topic: {topic}

        Methodology Plan:
        {methodology}

        Context Papers (Use these for your citations):
        {context}

        The proposal MUST contain the following 11 sections exactly as formatted below (use markdown):

        # 1. Abstract
        # 2. Introduction
        # 3. Related Work
        # 4. Research Gap
        # 5. Proposed Methodology
        # 6. Experimental Design
        # 7. Expected Contributions
        # 8. Timeline
        # 9. Budget Justification
        # 10. Broader Impact
        # 11. References
        (Synthesize explicitly the Context Papers provided into formal APA/IEEE references here matching the inline [1] [2] markers).

        Ground your writing firmly in the provided Context Papers. Prioritize scientific rigor.
        """
        
        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["topic", "methodology", "context"]
        )
        self.chain = self.prompt | self.llm
        
    def generate_proposal(self, topic: str, methodology_plan: str, source_papers: list):
        context_parts = []
        for i, p in enumerate(source_papers):
            context_parts.append(f"[Paper {i+1}]: {p.get('title', '')} - {p.get('abstract', '')}")
            
        context_str = "\n\n".join(context_parts)
        if not context_str.strip():
             context_str = "No specific context available. Please rely on general knowledge."
             
        try:
            response = self.chain.invoke({
                "topic": topic,
                "methodology": methodology_plan,
                "context": context_str
            })
            content = response.content
            if isinstance(content, list):
                content = content[0].get("text", str(content))
            proposal_markdown = content
        except Exception as e:
            print("LLM Error: Ensure GEMINI_API_KEY is set correctly.", e)
            proposal_markdown = "# 1. Abstract\n# 2. Introduction\n# 3. Related Work\n# 4. Research Gap\n# 5. Proposed Methodology\n# 6. Experimental Design\n# 7. Expected Contributions\n# 8. Timeline\n# 9. Budget Justification\n# 10. Broader Impact\n# 11. References"
            
        return proposal_markdown
        
    def export_pdf(self, markdown_text: str, output_path: str):
        # A simple text-to-PDF export using FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=11)
        
        # Super basic string cleaning for PDF
        text = markdown_text.encode('latin-1', 'replace').decode('latin-1')
        
        for line in text.split('\n'):
            pdf.multi_cell(0, 5, txt=line)
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf.output(output_path)
        return output_path

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    writer = ProposalWriter()
    plan = "### Dataset\n- ImageNet\n### Baseline\n- ResNet\n### Metrics\n- Accuracy\n### Steps\n1. Train"
    md = writer.generate_proposal("Medical AI", plan, [])
    print(md)
    writer.export_pdf(md, "test_proposal.pdf")
