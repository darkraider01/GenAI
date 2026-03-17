import fitz  # PyMuPDF
import json
import re
from pydantic import BaseModel
from typing import List, Dict, Any
from utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate

class PDFAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.1)
        self.prompt = PromptTemplate(
            template="""You are the Lead Scientific Reviewer at a Top-Tier Research Institution.
            Your goal is to extract deep, authentic, and highly technical structured information from the provided raw text of a research paper PDF.
            
            Guidelines for extraction:
            - **Title & Authors**: Ensure maximum accuracy.
            - **Key Contributions**: Provide 4-6 bullet points. Each point should be a detailed 1-2 sentence explanation of a technical or theoretical advancement. Avoid vague summaries.
            - **Methodology Overview**: Provide a 2-3 paragraph technical deep-dive. Explain the core architecture, the specific mathematical or algorithmic approach used, the data flow, and any novel training/execution strategies. Be technical and precise. Use explicit `\\n\\n` sequence for paragraph breaks.
            - **Datasets & Metrics**: Extract specific names of datasets and the exact evaluation metrics used.
            - **Tech Stack**: Identify any programming languages, frameworks (PyTorch, TensorFlow), libraries, hardware (NVIDIA A100), or specific software used.
            - **Strengths & Limitations**: Be critical and nuanced.
            
            Format the output strictly as a JSON object matching this schema exactly without any markdown backticks. 
            
            **CRITICAL**: Do NOT include literal newlines or unescaped control characters inside JSON strings. 
            - WRONG: "methodology": "Line 1
            Line 2"
            - RIGHT: "methodology": "Line 1\\nLine 2"
            
            JSON Schema:
            {{
                "title": "Full Paper Title",
                "authors": ["Author 1", "Author 2"],
                "year": "YYYY",
                "contributions": ["Detailed Contribution 1...", "Detailed Contribution 2...", "Detailed Contribution 3...", "Detailed Contribution 4..."],
                "methodology": "Paragraph 1: Core Architecture... \\n\\nParagraph 2: Algorithmic Approach... \\n\\nParagraph 3: Implementation Details...",
                "datasets": ["Dataset 1", "Dataset 2"],
                "tech_stack": ["Library 1", "Framework 2", "Hardware 3"],
                "evaluation_metrics": ["Metric 1", "Metric 2"],
                "strengths": ["Nuanced Technical Strength 1", "Nuanced Technical Strength 2"],
                "limitations": ["Critical Limitation 1", "Critical Limitation 2"],
                "future_work": ["Specific Future Direction 1"]
            }}
            
            Raw Paper Text (first 15,000 chars):
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
                
            try:
                # First attempt with strict=False to handle some control characters
                parsed = json.loads(clean_json, strict=False)
            except json.JSONDecodeError:
                # If it still fails, it's likely literal newlines/tabs inside strings.
                # Use regex to find strings and escape literal newlines within them.
                def replace_newlines(match):
                    return match.group(0).replace('\n', '\\n').replace('\r', '\\r')
                
                # Regex for JSON strings: " (anything but " or \", or escaped chars) "
                # This is a heuristic but often works for LLM outputs
                fixed_json = re.sub(r'"(.*?)"', replace_newlines, clean_json, flags=re.DOTALL)
                parsed = json.loads(fixed_json, strict=False)
                
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
                "tech_stack": [],
                "evaluation_metrics": [],
                "strengths": [],
                "limitations": [],
                "future_work": []
            }
