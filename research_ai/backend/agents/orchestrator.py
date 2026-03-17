import os
import sys
import time
import json
from dotenv import load_dotenv

# Standardize path for backend imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

load_dotenv()

# Import our backend modules
from trend_analysis.topic_model import analyze_trends
from gap_analysis.gap_detector import detect_gaps
from methodology.method_planner import MethodPlanner
from proposal.proposal_writer import ProposalWriter
from evaluation.novelty_score import NoveltyScorer
from rag.retriever import ResearchRetriever
from utils.llm_factory import get_llm
from langchain_core.tools import Tool


def search_literature(query: str) -> str:
    """Search for deep technical details and prior art in the research domain."""
    retriever = ResearchRetriever()
    papers = retriever.retrieve(query, top_k=8)
    if not papers: return "No papers found."
    res = "### Direct Evidence & Prior Art\n\n"
    for p in papers:
        res += f"#### {p['title']} ({p['year']})\n"
        res += f"- **Key Info:** {p['abstract'][:500]}...\n"
        res += f"- **Access:** [{p.get('pdf_url', 'Source Paper Link')}]({p.get('pdf_url', '#')})\n\n"
    return res

def analyze_tech_trends() -> str:
    """Identify high-growth trajectories and technology stacks."""
    trends = analyze_trends()
    if not trends: return "No trends found."
    res = "### Market & Academic Trajectories\n\n"
    for t in trends[:5]:
        res += f"- **Topic Sector:** {', '.join(t['keywords'])}  \n  *Momentum:* High | *Growth Rate:* {t['growth_rate']}\n"
    return res

def detect_research_gaps(topic: str = None) -> str:
    """Identify precise white spaces and unexplored technical intersections."""
    gaps = detect_gaps(query_topic=topic)
    if not gaps: return "No gaps found."
    res = "### High-Potential Research Gaps\n\n"
    for g in gaps[:4]:
        res += f"- **Target Gap:** {g['gap_description']}\n  *Technical Foundation:* Unexplored Interdisciplinary Overlap\n"
    return res

# Tool Definitions for CrewAI / Testing
search_literature_tool = Tool(
    name="Search Literature",
    func=search_literature,
    description="Search for deep technical details and prior art in the research domain."
)

trend_analysis_tool = Tool(
    name="Trend Analysis",
    func=lambda x=None: analyze_tech_trends(),
    description="Identify high-growth trajectories and technology stacks."
)

gap_detection_tool = Tool(
    name="Gap Detection",
    func=detect_research_gaps,
    description="Identify precise white spaces and unexplored technical intersections."
)

method_planning_tool = Tool(
    name="Method Planning",
    func=lambda x: MethodPlanner().plan_methodology(x)['plan_markdown'],
    description="Design a rigorous scientific methodology for a given topic."
)

proposal_generation_tool = Tool(
    name="Proposal Generation",
    func=lambda x: ProposalWriter().generate_proposal(
        x.split("\n")[0].replace("Topic: ", ""), 
        "\n".join(x.split("\n")[1:]), 
        ResearchRetriever().retrieve(x.split("\n")[0].replace("Topic: ", ""), top_k=5)
    ),
    description="Generate an exhaustive, highly formal grant proposal."
)

novelty_scoring_tool = Tool(
    name="Novelty Scoring",
    func=lambda x: NoveltyScorer().score_novelty(x),
    description="Score the novelty of a research proposal against existing literature."
)

from utils.logger import pipeline_logger

class ResearchOrchestrator:
    def __init__(self):
        # We use key 1 for early stages and key 2 for synthesis to balance TPM
        self.llm1 = get_llm(model="llama-3.3-70b-versatile", temperature=0.3)
        self.llm2 = get_llm(model="llama-3.3-70b-versatile", temperature=0.5)
        # Manually set key 2 if available
        if os.getenv("GROQ_API_KEY_2"):
            from langchain_groq import ChatGroq
            self.llm2 = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY_2"),
                temperature=0.5
            )

    def run_pipeline(self, user_topic: str):
        print(f"Starting Swarm for: {user_topic}")
        # Clear previous logs if any
        pipeline_logger.logs = []
        
        # 1. Literature Discovery
        s1 = pipeline_logger.start_step("Literature Discovery", f"Searching for deep technical details on {user_topic}")
        lit_context = search_literature(user_topic)
        pipeline_logger.complete_step(s1)
        
        # 2. Trend Analysis
        s2 = pipeline_logger.start_step("Trend Analysis", "Mapping academic momentum and trajectory")
        trend_context = analyze_tech_trends()
        pipeline_logger.complete_step(s2)
        
        # 3. Gap Detection
        s3 = pipeline_logger.start_step("Gap Identification", "Finding unexplored intersections via clustering")
        gap_context = detect_research_gaps(user_topic)
        pipeline_logger.complete_step(s3)
        
        # 4. Methodology Design (LLM Call 1)
        s4 = pipeline_logger.start_step("Methodology Design", "Structuring scientific experiments and baselines")
        planner = MethodPlanner()
        method_plan = planner.plan_methodology(user_topic)['plan_markdown']
        pipeline_logger.complete_step(s4)
        
        # 5. Proposal Writing (LLM Call 2)
        s5 = pipeline_logger.start_step("Proposal Synthesis", "Drafting technical grant proposal")
        writer = ProposalWriter()
        retriever = ResearchRetriever()
        context_papers = retriever.retrieve(user_topic, top_k=5)
        proposal_md = writer.generate_proposal(user_topic, method_plan, context_papers)
        pipeline_logger.complete_step(s5)
        
        # Final Synthesis
        s6 = pipeline_logger.start_step("Novelty Validation & Final Report", "Checking structural novelty and generating master document")
        scorer = NoveltyScorer()
        novelty_data = scorer.score_novelty(proposal_md)
        
        # Fixed: Identifying tech stack from trend context if available
        tech_stack = "Python, PyTorch, Transformers, ChromaDB, Groq LLM" # Default robust stack
        if "High-growth" in trend_context or "trajectories" in trend_context.lower():
             # Try to extract keywords if they look like tech
             tech_keywords = ["React", "FastAPI", "TensorFlow", "Scikit-Learn", "Keras", "LangChain"]
             detected = [tk for tk in tech_keywords if tk.lower() in trend_context.lower()]
             if detected:
                 tech_stack = ", ".join(detected)
             
        plagiarism_score = novelty_data.get('plagiarism_score', 0.0)
        
        novelty_str = (
            f"**Mathematical Novelty Score:** {novelty_data['novelty_score']:.2f}\n"
            f"**Plagiarism Probability:** {plagiarism_score}%\n"
            f"**Max Semantic Overlap:** {novelty_data['max_similarity']:.2f}\n"
            f"**Closest Competitor:** {novelty_data.get('closest_paper', {}).get('title', 'Unknown')}\n"
        )
        
        synthesis_prompt = f"""
        You are the Chief Research Officer at a world-class AI Laboratory.
        Synthesize the following research data into a MASTER RESEARCH REPORT.
        The report must be extremely professional, technical, and structured for a PhD-level audience.
        
        USER TOPIC: {user_topic}
        
        DATA SECTIONS TO INCLUDE:
        {lit_context}
        {trend_context}
        {gap_context}
        
        PROPOSED METHODOLOGY:
        {method_plan}
        
        TECH STACK REQUIREMENTS:
        {tech_stack}
        
        GRANT PROPOSAL CONTENT:
        {proposal_md}
        
        NOVELTY & PLAGIARISM VALIDATION:
        {novelty_str}
        
        YOUR TASK: 
        Create a single, cohesive Master Research Report in Markdown.
        Structure it exactly as:
        # Ultimate Master Research Report: [Topic]
        
        ## 1. Executive Summary
        (Write a 2-paragraph professional summary of the entire findings below)
        
        ## 2. Theoretical Foundation & Prior Art
        (Include and expand on the Literature findings)
        
        ## 3. Technology Trajectory & Momentum
        (Include the Trends findings)
        
        ## 4. The Innovation Gap
        (Detail the identified research gap)
        
        ## 5. Technical Methodology Design
        (Present the methodology plan)
        
        ## 6. Strategic Grant Proposal
        (The full grant proposal content)
        
        ## 7. Novelty & Structural Validation
        (The novelty score and competitor analysis)
        
        Ensure the formatting is flawless and the transition between sections is logical.
        """
        
        final_res = self.llm2.invoke(synthesis_prompt)
        pipeline_logger.complete_step(s6)
        
        # Return structured dict
        return {
            "report": final_res.content,
            "logs": pipeline_logger.get_logs()
        }

if __name__ == "__main__":
    orchestrator = ResearchOrchestrator()
    result = orchestrator.run_pipeline("AI in healthcare")
    print(result)
