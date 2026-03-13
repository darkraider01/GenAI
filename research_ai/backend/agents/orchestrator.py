import os
import time
from crewai import Agent, Task, Crew, Process
from crewai import LLM
from crewai.tools import tool

# Import our backend modules
from backend.trend_analysis.topic_model import analyze_trends
from backend.gap_analysis.gap_detector import detect_gaps
from backend.methodology.method_planner import MethodPlanner
from backend.proposal.proposal_writer import ProposalWriter
from backend.evaluation.novelty_score import NoveltyScorer
from backend.rag.retriever import ResearchRetriever

import os

# Primary key: used by agents 1-3 (Literature, Trend, Gap)
# llama-3.1-8b-instant: 131,072 TPM on Groq free tier (vs 12K for 70b model)
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.2,
    max_retries=5,
    api_key=os.getenv("GROQ_API_KEY", "")
)

# Secondary key: used by agents 4-6 (Method, Grant, Evaluation)
_key2 = os.getenv("GROQ_API_KEY_2", "") or os.getenv("GROQ_API_KEY", "")
llm2 = LLM(
    model="groq/llama-3.1-8b-instant",
    temperature=0.2,
    max_retries=5,
    api_key=_key2
)

@tool
def search_literature_tool(query: str) -> str:
    """Search the vector database for relevant research papers."""
    retriever = ResearchRetriever()
    papers = retriever.retrieve(query, top_k=5)
    if not papers: return "No papers found."
    res = "Relevant Papers:\n"
    for p in papers:
        res += f"- {p['title']} ({p['year']}): {p['abstract'][:200]}...\n"
    return res

@tool
def trend_analysis_tool(dummy: str = "") -> str:
    """Run trend analysis to discover emerging research topics."""
    trends = analyze_trends()
    if not trends: return "No trends found."
    res = "Emerging Topics:\n"
    for t in trends[:3]:
        res += f"- Topic {t['topic_id']} (Growth: {t['growth_rate']}): {', '.join(t['keywords'])}\n"
    return res

@tool
def gap_detection_tool(dummy: str = "") -> str:
    """Analyze semantic similarity and citation graphs to detect research gaps."""
    gaps = detect_gaps()
    if not gaps: return "No gaps found."
    res = "Potential Gaps:\n"
    for g in gaps[:3]:
        res += f"- {g['gap_description']} (Sim: {g['similarity']:.2f}, Cross-Cites: {g['cross_citations']})\n"
    return res

@tool
def method_planning_tool(topic: str) -> str:
    """Generate a structured methodology plan for a given research topic."""
    planner = MethodPlanner()
    result = planner.plan_methodology(topic)
    return result['plan_markdown']

@tool
def proposal_generation_tool(topic_and_methodology: str) -> str:
    """Generate a grant proposal. Input must contain the topic and methodology."""
    writer = ProposalWriter()
    planner = MethodPlanner() # We reuse retriever part implicitly
    # Let's just pass the whole string to writer since topic_and_methodology has everything
    # The writer expects topic, methodology_plan, source_papers. We handle it in the tool easily:
    papers = ResearchRetriever().retrieve(topic_and_methodology[:100], top_k=5)
    md = writer.generate_proposal("Extracted Topic", topic_and_methodology, papers)
    return md

@tool
def novelty_scoring_tool(proposal_text: str) -> str:
    """Score the novelty of a proposal text against existing literature."""
    scorer = NoveltyScorer()
    res = scorer.score_novelty(proposal_text)
    return f"Novelty Score: {res['novelty_score']:.2f}\nClosest Paper Sim: {res['max_similarity']:.2f}\nClosest Paper: {res.get('closest_paper', {}).get('title', 'Unknown')}"

class ResearchOrchestrator:
    def __init__(self):
        # Define Agents
        self.literature_agent = Agent(
            role='Literature Researcher',
            goal='Search and summarize relevant academic literature.',
            backstory='An expert librarian and researcher.',
            verbose=True,
            allow_delegation=False,
            tools=[search_literature_tool],
            llm=llm
        )
        
        self.trend_agent = Agent(
            role='Trend Analyst',
            goal='Identify emerging topics in the research landscape.',
            backstory='A data scientist specializing in scientometrics and topic modeling.',
            verbose=True,
            allow_delegation=False,
            tools=[trend_analysis_tool],
            llm=llm
        )
        
        self.gap_agent = Agent(
            role='Gap Detector',
            goal='Find high-value research gaps using semantic overlaps and citation disconnects.',
            backstory='An analytical strategist who finds unexplored intersections of ideas.',
            verbose=True,
            allow_delegation=False,
            tools=[gap_detection_tool],
            llm=llm
        )
        
        self.method_agent = Agent(
            role='Methodology Designer',
            goal='Design rigorous experimental methodologies for new research topics.',
            backstory='A senior principal investigator with deep expertise in experimental design.',
            verbose=True,
            allow_delegation=False,
            tools=[method_planning_tool],
            llm=llm2  # Uses second API key
        )
        
        self.grant_agent = Agent(
            role='Grant Proposal Writer',
            goal='Synthesize research gaps and methodologies into compelling grant proposals.',
            backstory='A highly successful academic who has won millions in grant funding.',
            verbose=True,
            allow_delegation=False,
            tools=[proposal_generation_tool],
            llm=llm2  # Uses second API key
        )
        
        self.evaluation_agent = Agent(
            role='Evaluation & Novelty Scorer',
            goal='Evaluate the novelty of a proposed grant and score it against existing literature.',
            backstory='A strict reviewer for top-tier academic journals.',
            verbose=True,
            allow_delegation=False,
            tools=[novelty_scoring_tool],
            llm=llm2  # Uses second API key
        )
        
    def run_pipeline(self, user_topic: str):
        # Define Tasks
        t1 = Task(
            description=f'Search literature for the domain: {user_topic}',
            expected_output='A summary of the current literature landscape for the given topic.',
            agent=self.literature_agent
        )
        
        t2 = Task(
            description='Analyze the database to find emerging trends / topics with high growth rates.',
            expected_output='A list of emerging topics with growth rates.',
            agent=self.trend_agent
        )
        
        t3 = Task(
            description='Use the trend analysis and citation graph to detect an actionable research gap.',
            expected_output='A specific research gap connecting two distinct topics.',
            agent=self.gap_agent
        )
        
        t4 = Task(
            description='Based on the detected research gap, generate a detailed methodology plan including datasets, baselines, and metrics.',
            expected_output='A methodology plan in markdown format.',
            agent=self.method_agent
        )
        
        t5 = Task(
            description='Write a full 8-section grant proposal using the research gap and methodology plan.',
            expected_output='A full grant proposal in markdown format.',
            agent=self.grant_agent
        )
        
        t6 = Task(
            description='Evaluate the generated grant proposal for novelty against the database.',
            expected_output='A final report appending the novelty score to the grant proposal.',
            agent=self.evaluation_agent
        )
        
        crew = Crew(
            agents=[self.literature_agent, self.trend_agent, self.gap_agent, self.method_agent, self.grant_agent, self.evaluation_agent],
            tasks=[t1, t2, t3, t4, t5, t6],
            process=Process.sequential,
            verbose=True,
            max_rpm=3  # Limit to 3 LLM calls/min to respect Groq free-tier TPM (12,000)
        )
        
        res = crew.kickoff()
        return res

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    orchestrator = ResearchOrchestrator()
    result = orchestrator.run_pipeline("AI for healthcare")
    print(result)
