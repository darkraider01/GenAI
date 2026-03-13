from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.literature_review.review_generator import LiteratureReviewGenerator
from backend.paper_reader.pdf_analyzer import PDFAnalyzer
from backend.citation_graph.graph_builder import CitationGraphBuilder
from backend.rag.retriever import ResearchRetriever
from backend.trend_analysis.topic_model import analyze_trends
from backend.gap_analysis.gap_detector import detect_gaps
from backend.methodology.method_planner import MethodPlanner
from backend.proposal.proposal_writer import ProposalWriter
from backend.evaluation.novelty_score import NoveltyScorer
from backend.agents.orchestrator import ResearchOrchestrator
from backend.utils.llm_factory import get_llm
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

import time

app = FastAPI(title="Research Intelligence API")

# Setup CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since we're running locally we don't need strict origins yet
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LitReviewRequest(BaseModel):
    topic: str

class SearchRequest(BaseModel):
    query: str

class MethodPlanRequest(BaseModel):
    topic: str
    
class ProposalRequest(BaseModel):
    topic: str
    methodology: str
    
class NoveltyRequest(BaseModel):
    proposal_text: str

class OrchestratorRequest(BaseModel):
    topic: str

# Instantiate the engine modules on generic scope to cache their model weights implicitly
review_gen = LiteratureReviewGenerator()
pdf_analyzer = PDFAnalyzer()
graph_builder = CitationGraphBuilder()
retriever = ResearchRetriever()
method_planner = MethodPlanner()
proposal_writer = ProposalWriter()
novelty_scorer = NoveltyScorer()
orchestrator = ResearchOrchestrator()

@app.post("/api/literature-review")
async def generate_literature_review(req: LitReviewRequest):
    result = review_gen.generate(req.topic)
    return result

@app.post("/api/analyze-paper")
async def analyze_paper(file: UploadFile = File(...)):
    # Read streaming PDF bytes into memory
    file_bytes = await file.read()
    structured_data = pdf_analyzer.analyze(file_bytes)
    return structured_data

@app.get("/api/citation-graph")
async def get_citation_graph():
    graph_data = graph_builder.build_frontend_graph()
    return graph_data

@app.post("/api/search")
async def search_papers(req: SearchRequest):
    results = retriever.retrieve(req.query)
    return results

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
    gaps = get_cached_gaps()
    return gaps

@app.post("/api/method-plan")
async def generate_method_plan(req: MethodPlanRequest):
    result = method_planner.plan_methodology(req.topic)
    return result

@app.post("/api/generate-proposal")
async def generate_proposal(req: ProposalRequest):
    # Retrieve top 5 papers as context for the Proposal Writer (matching streamlit behavior)
    context_papers = retriever.retrieve(req.topic, top_k=5)
    markdown_out = proposal_writer.generate_proposal(req.topic, req.methodology, context_papers)
    return {"markdown": markdown_out}

@app.post("/api/novelty-score")
async def score_novelty(req: NoveltyRequest):
    res = novelty_scorer.score_novelty(req.proposal_text)
    return res

swarm_history = []

@app.post("/api/orchestrator")
async def run_orchestrator(req: OrchestratorRequest):
    try:
        orchestrator = ResearchOrchestrator()
        result = orchestrator.run_pipeline(req.topic)
        
        run_record = {
            "id": len(swarm_history) + 1,
            "topic": req.topic,
            "result": result.raw if hasattr(result, 'raw') else str(result),
            "timestamp": time.time()
        }
        swarm_history.insert(0, run_record)
        
        return {"result": run_record["result"]}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orchestrator_history")
async def get_orchestrator_history():
    return {"history": swarm_history}
    
@app.get("/api/insights")
async def get_insights():
    # Cache trends and gaps to simulate the panel.
    trends = get_cached_trends()
    gaps = get_cached_gaps()
    
    if not trends or not gaps:
        return {"report": "Database requires trends and gaps."}
        
    trend_str = "\n".join([f"- {t.get('topic_name')} ({t.get('trend_type')})" for t in trends[:5]])
    gap_str = "\n".join([f"- {g.get('gap_description').splitlines()[0] if 'gap_description' in g else ''} (Score: {g.get('gap_score')})" for g in gaps[:3]])
    
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
    llm = get_llm(temperature=0.2)
    chain = prompt | llm
    res = chain.invoke({"trends": trend_str, "gaps": gap_str})
    
    return {"report": res.content}

@app.get("/api/forecast")
async def get_forecast():
    trends = get_cached_trends()
    if not trends:
        return {"forecast": "Please run analytics to establish baselines."}
        
    trend_str = "\n".join([f"- {t.get('topic_name')} (Momentum: {t.get('growth_rate'):.2f}, Shift: {t.get('insight_report', '')[:100]}...)" for t in trends[:5]])
    
    prompt = PromptTemplate(
        template="""You are a visionary Chief Scientist.
        Based on the highest momentum topics extracted from the literature, forecast the top 3 dominant research fields for the next 3 years.
        
        Current Momentum Baselines:
        {trends}
        
        Format EXACTLY as:
        ### Predicted High Impact Fields (Next 3 Years)
        
        **1. [Field Name]**
        (Detailed paragraph predicting the trajectory and ultimate application of this field).
        
        **2. [Field Name]**
        (Detailed paragraph predicting the trajectory).
        
        **3. [Field Name]**
        (Detailed paragraph predicting the trajectory).
        """,
        input_variables=["trends"]
    )
    llm = get_llm(temperature=0.7)
    chain = prompt | llm
    res = chain.invoke({"trends": trend_str})
    
    return {"forecast": res.content}

if __name__ == "__main__":
    import uvicorn
    # Make sure this is running using exactly port 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
