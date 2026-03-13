import fitz  # PyMuPDF
import json
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

class PDFAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.1)
        self.prompt = PromptTemplate(
            template="""You are an expert AI scientific paper analyzer.
            Extract the requested structured information from the provided raw text of a research paper PDF.
            Extract only facts grounded in the text.
            
            Format the output strictly as a JSON object matching this schema exactly without any markdown backticks:
            {{
                "title": "Full Paper Title",
                "authors": ["Author 1", "Author 2"],
                "year": "YYYY",
                "contributions": ["Contribution 1", "Contribution 2"],
                "methodology": "Summary of the core methodology...",
                "datasets": ["Dataset 1", "Dataset 2"],
                "evaluation_metrics": ["Metric 1", "Metric 2"],
                "strengths": ["Strength 1"],
                "limitations": ["Limitation 1"],
                "future_work": ["Future Direction 1"]
            }}
            
            Raw Paper Text (first 10,000 chars):
            {paper_text}
            """,
            input_variables=["paper_text"]
        )

    def analyze(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Parses a PDF from bytes, extracts text, and asks the LLM to structure it.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            full_text = ""
            for i in range(min(5, doc.page_count)):  # Analyze up to first 5 pages for extreme speed and context window
                full_text += doc[i].get_text()
                
            doc.close()
            
            # Truncate to avoid context blowing up
            truncated_text = full_text[:15000]
            
            chain = self.prompt | self.llm
            res = chain.invoke({"paper_text": truncated_text})
            
            # Clean JSON
            clean_json = res.content.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
                
            parsed = json.loads(clean_json.strip())
            return parsed
            
        except Exception as e:
            print(f"Error analyzing PDF: {e}")
            return {
                "title": "Error Parsing PDF",
                "authors": [],
                "year": "Unknown",
                "contributions": [],
                "methodology": str(e),
                "datasets": [],
                "evaluation_metrics": [],
                "strengths": [],
                "limitations": [],
                "future_work": []
            }
