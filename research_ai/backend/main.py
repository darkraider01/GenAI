from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sys
import os
import json

# Fix for tqdm OSError in background process
os.environ["TQDM_DISABLE"] = "1"
def safe_flush():
    try:
        sys.__stderr__.flush()
    except Exception:
        pass
if hasattr(sys.stderr, 'flush'):
    sys.stderr.flush = safe_flush

# Standardize path for backend/project imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(project_root, 'backend')

if project_root not in sys.path:
    sys.path.append(project_root)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from literature_review.review_generator import LiteratureReviewGenerator
from paper_reader.pdf_analyzer import PDFAnalyzer
from rag.retriever import ResearchRetriever
from trend_analysis.topic_model import analyze_trends
from gap_analysis.gap_detector import detect_gaps
from methodology.method_planner import MethodPlanner
from proposal.proposal_writer import ProposalWriter
from evaluation.novelty_score import NoveltyScorer
from agents.orchestrator import ResearchOrchestrator
from utils.llm_factory import get_llm
from responsible_ai.rai_engine import RAIAuditor
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

import time

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Research Intelligence API")

# Mount graphs directory for static access
graphs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "graphs")
os.makedirs(graphs_path, exist_ok=True)
app.mount("/graphs", StaticFiles(directory=graphs_path), name="graphs")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LitReviewRequest(BaseModel):
    topic: str

class GraphIdeaRequest(BaseModel):
    topic: str
    custom_data: str = None

class SearchRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    messages: list
    model: str = "Gemini Pro"

class MethodPlanRequest(BaseModel):
    topic: str
    
class ProposalRequest(BaseModel):
    topic: str
    methodology: str
    
class NoveltyRequest(BaseModel):
    proposal_text: str

class OrchestratorRequest(BaseModel):
    topic: str

class RAIAuditRequest(BaseModel):
    query: str
    response: str
    papers: list = []

class DownloadReportRequest(BaseModel):
    topic: str
    markdown: str

# Lazy-loaded engine modules
_review_gen = None
_pdf_analyzer = None
_retriever = None
_method_planner = None
_proposal_writer = None
_novelty_scorer = None
_orchestrator = None

def get_review_gen():
    global _review_gen
    if _review_gen is None: _review_gen = LiteratureReviewGenerator()
    return _review_gen

def get_pdf_analyzer():
    global _pdf_analyzer
    if _pdf_analyzer is None: _pdf_analyzer = PDFAnalyzer()
    return _pdf_analyzer

def get_retriever():
    global _retriever
    if _retriever is None: _retriever = ResearchRetriever()
    return _retriever

def get_method_planner():
    global _method_planner
    if _method_planner is None: _method_planner = MethodPlanner()
    return _method_planner

def get_proposal_writer():
    global _proposal_writer
    if _proposal_writer is None: _proposal_writer = ProposalWriter()
    return _proposal_writer

def get_novelty_scorer():
    global _novelty_scorer
    if _novelty_scorer is None: _novelty_scorer = NoveltyScorer()
    return _novelty_scorer

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None: _orchestrator = ResearchOrchestrator()
    return _orchestrator

@app.post("/api/literature-review")
async def generate_literature_review(req: LitReviewRequest):
    result = get_review_gen().generate(req.topic)
    return result

@app.post("/api/analyze-paper")
async def analyze_paper(file: UploadFile = File(...)):
    # Read streaming PDF bytes into memory
    file_bytes = await file.read()
    structured_data = get_pdf_analyzer().analyze(file_bytes)
    
    # PERSISTENCE: Save reader history
    from utils.history_manager import history_manager
    history_manager.add_reader_entry(file.filename, json.dumps(structured_data))
    
    return structured_data

@app.get("/api/reader-history")
async def get_reader_history():
    from utils.history_manager import history_manager
    return {"history": history_manager.get_history("reader_history")}

@app.post("/api/graph-ideas")
async def get_graph_ideas(req: GraphIdeaRequest):
    from agents.graph_agent import GraphAgent
    agent = GraphAgent()
    ideas = agent.generate_ideas(req.topic, req.custom_data)
    
    # PERSISTENCE: Save graph history (ideas phase)
    from utils.history_manager import history_manager
    history_manager.add_graph_entry(req.topic, ideas)
    
    return {"ideas": ideas}
@app.post("/api/generate-graph")
async def generate_graph(req: dict):
    from agents.graph_agent import GraphAgent
    agent = GraphAgent()
    idea = req.get("idea")
    topic = req.get("topic")
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "graphs")
    filename = agent.generate_graph(idea, output_dir)
    
    image_url = f"/graphs/{filename}"
    
    from utils.history_manager import history_manager
    history_manager.add_graph_entry(topic, [idea], image_url)
    
    return {"image_url": image_url}

@app.post("/api/plot-csv")
async def plot_csv_directly(req: GraphIdeaRequest):
    from agents.graph_agent import GraphAgent
    if not req.custom_data:
        raise HTTPException(status_code=400, detail="No CSV data provided")
        
    agent = GraphAgent()
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db", "graphs")
    filename = agent.plot_csv_directly(req.custom_data, output_dir)
    
    if not filename:
        raise HTTPException(status_code=500, detail="Could not parse or plot CSV")
        
    image_url = f"/graphs/{filename}"
    return {"image_url": image_url}


@app.post("/api/search")
async def search_papers(req: SearchRequest):
    try:
        print(f"\n[DEBUG] RECEIVED SEARCH REQUEST: {req.query}")
        retriever = get_retriever()
        print(f"[DEBUG] RETRIEVER OBTAINED")
        results = retriever.retrieve(req.query)
        print(f"[DEBUG] SEARCH COMPLETED: {len(results)} results")
        
        # PERSISTENCE: Save search history
        from utils.history_manager import history_manager
        history_manager.add_explorer_entry(req.query, len(results))
        
        return results
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        try:
            with open('traceback_debug.txt', 'w', encoding='utf-8') as f:
                f.write(error_msg)
        except Exception:
            pass
        print(f"Search error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/search-history")
async def get_search_history():
    from utils.history_manager import history_manager
    return {"history": history_manager.get_history("explorer_history")}

_cached_trends = None
_cached_gaps = None

def get_cached_trends():
    global _cached_trends
    if _cached_trends is None:
        import time
        print("Computing Trends (Cache Miss)...")
        _cached_trends = analyze_trends()
    return _cached_trends

def get_cached_gaps():
    global _cached_gaps
    if _cached_gaps is None:
        print("Computing Gaps (Cache Miss)...")
        _cached_gaps = detect_gaps()
    return _cached_gaps

@app.get("/api/trends")
async def get_trends():
    trends = get_cached_trends()
    return trends

@app.get("/api/gaps")
async def get_gaps():
    # We remove caching to ensure variety on every click as requested by user
    print("Computing Gaps for variety...")
    gaps = detect_gaps()
    return gaps

@app.post("/api/method-plan")
async def generate_method_plan(req: MethodPlanRequest):
    result = get_method_planner().plan_methodology(req.topic)
    return result

@app.post("/api/generate-proposal")
async def generate_proposal(req: ProposalRequest):
    # Retrieve top 5 papers as context for the Proposal Writer (matching streamlit behavior)
    context_papers = get_retriever().retrieve(req.topic, top_k=5)
    markdown_out = get_proposal_writer().generate_proposal(req.topic, req.methodology, context_papers)
    return {"markdown": markdown_out}

@app.post("/api/novelty-score")
async def score_novelty(req: NoveltyRequest):
    res = get_novelty_scorer().score_novelty(req.proposal_text)
    return res

swarm_history = []

@app.post("/api/orchestrator")
async def run_orchestrator(req: OrchestratorRequest):
    try:
        orchestrator = ResearchOrchestrator()
        result_dict = orchestrator.run_pipeline(req.topic)
        
        # result_dict has 'report' and 'logs'
        res_text = result_dict.get('report', str(result_dict))
        logs = result_dict.get('logs', [])
        
        # PERSISTENCE: Save swarm history
        from utils.history_manager import history_manager
        history_manager.add_swarm_entry(req.topic, res_text)
        
        return {"result": res_text, "logs": logs}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/download-report")
async def download_report(req: DownloadReportRequest):
    try:
        from proposal.proposal_writer import ProposalWriter
        writer = ProposalWriter()
        
        # Create a sanitized filename
        import re
        safe_topic = re.sub(r'[^\w\s-]', '', req.topic).strip().replace(' ', '_')
        if not safe_topic:
            safe_topic = "Research_Report"
        
        filename = f"Master_Report_{safe_topic}.pdf"
        output_dir = os.path.join(project_root, "db", "reports")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        
        writer.export_pdf(req.markdown, file_path)
        
        return FileResponse(
            path=file_path, 
            filename=filename, 
            media_type='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orchestrator_logs")
async def get_orchestrator_logs():
    from utils.logger import pipeline_logger
    return {"logs": pipeline_logger.get_logs()}

@app.get("/api/orchestrator_history")
async def get_orchestrator_history():
    from utils.history_manager import history_manager
    history = history_manager.get_history("swarm_history")
    return {"history": history}
    
@app.get("/api/insights")
async def get_insights():
    # Cache trends and gaps to simulate the panel.
    trends = get_cached_trends()
    gaps = get_cached_gaps()
    
    if not trends or not gaps:
        return {"report": "Database requires trends and gaps."}
        
    # VARIETY: Shuffle or randomly sample for fresh content
    import random
    random_trends = random.sample(trends, min(5, len(trends)))
    random_gaps = random.sample(gaps, min(3, len(gaps)))
    
    trend_str = "\n".join([f"- {t.get('topic_name')} ({t.get('trend_type')})" for t in random_trends])
    gap_str = "\n".join([f"- {g.get('gap_description').splitlines()[0] if 'gap_description' in g else ''} (Score: {g.get('gap_score')})" for g in random_gaps])
    
    prompt = PromptTemplate(
        template="""You are a Senior Academic Intelligence Director.
        Based on these Trends and Research Gaps found in our corpus, generate a high-level Landscape Summary.
        
        Trends:
        {trends}
        
        Gaps:
        {gaps}
        
        Format EXACTLY as:
        ### Research Landscape Summary
        **Emerging Fields:**
        - (list items)
        
        **High Impact Research Gaps:**
        - (list items)
        
        **Recommended Research Direction:**
        (Provide 1 highly specific, promising paragraph combining an emerging field and a strong gap).
        """,
        input_variables=["trends", "gaps"]
    )
    # Higher temperature for more variety
    llm = get_llm(temperature=0.7)
    chain = prompt | llm
    res = chain.invoke({"trends": trend_str, "gaps": gap_str})
    
    return {"report": res.content}

@app.get("/api/forecast")
async def get_forecast():
    trends = get_cached_trends()
    if not trends:
        return {"forecast": "Please run analytics to establish baselines."}
        
    trend_strings = []
    for t in trends[:5]:
        papers = t.get('representative_papers', [])
        paper_str = ""
        if papers:
            paper_str = " Sources: " + ", ".join([f"[{p['title']}]({p['url']})" for p in papers])
        
        trend_strings.append(f"- {t.get('topic_name')} (Momentum: {t.get('growth_rate'):.2f}, Shift: {t.get('insight_report', '')[:100]}...){paper_str}")
        
    trend_str = "\n".join(trend_strings)
    
    prompt = PromptTemplate(
        template="""You are a visionary Chief Scientist.
        Based on the highest momentum topics extracted from the literature, forecast the top 3 dominant research fields for the next 3 years.
        
        Current Momentum Baselines with Sources:
        {trends}
        
        Format EXACTLY as:
        ### Predicted High Impact Fields (Next 3 Years)
        
        **1. [Field Name]**
        (Detailed paragraph predicting the trajectory and ultimate application of this field).
        *Sources:* Include the provided source links formatted as markdown links.
        
        **2. [Field Name]**
        (Detailed paragraph predicting the trajectory).
        *Sources:* Include the provided source links.
        
        **3. [Field Name]**
        (Detailed paragraph predicting the trajectory).
        *Sources:* Include the provided source links.
        """,
        input_variables=["trends"]
    )
    llm = get_llm(temperature=0.7)
    chain = prompt | llm
    res = chain.invoke({"trends": trend_str})
    
    return {"forecast": res.content}

@app.post("/api/assistant/chat")
async def assistant_chat(req: ChatRequest):
    from agents.assistant_agent import AssistantAgent
    agent = AssistantAgent()
    return await agent.stream_chat(req.messages, req.model)

# ── Responsible AI ────────────────────────────────────────────────────────────
_rai_auditor = None

def get_rai_auditor():
    global _rai_auditor
    if _rai_auditor is None:
        _rai_auditor = RAIAuditor()
    return _rai_auditor

@app.post("/api/rai-audit")
async def run_rai_audit(req: RAIAuditRequest):
    try:
        report = get_rai_auditor().audit(
            query=req.query,
            response=req.response,
            papers=req.papers
        )
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Make sure this is running using exactly port 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
