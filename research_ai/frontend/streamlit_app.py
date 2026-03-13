import sys
import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
from pyvis.network import Network
import tempfile
import json
import streamlit.components.v1 as components

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.rag.retriever import ResearchRetriever
from backend.trend_analysis.topic_model import analyze_trends
from backend.gap_analysis.gap_detector import detect_gaps
from backend.methodology.method_planner import MethodPlanner
from backend.proposal.proposal_writer import ProposalWriter
from backend.evaluation.novelty_score import NoveltyScorer
from backend.agents.orchestrator import ResearchOrchestrator
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

st.set_page_config(page_title="Agentic Research Assistant", layout="wide")

if "agent_history" not in st.session_state:
    st.session_state.agent_history = {}
    
if "activity_log" not in st.session_state:
    st.session_state.activity_log = []

def log_activity(msg):
    st.session_state.activity_log.append(msg)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "1 Research Explorer", 
    "2 Trend Analytics", 
    "3 Gap Finder", 
    "4 Method Planner", 
    "5 Proposal Generator", 
    "6 Novelty Analyzer",
    "7 Agent Orchestrator",
    "Research Insight Panel",
    "Future Forecast Panel",
    "Citation Graph Viewer"
])

st.sidebar.divider()
st.sidebar.subheader("Agent Activity Log")
if not st.session_state.activity_log:
    st.sidebar.write("*No activity yet.*")
else:
    for log in reversed(st.session_state.activity_log[-10:]):
        st.sidebar.write(log)

def research_explorer():
    st.title("Research Explorer")
    query = st.text_input("Semantic Search:")
    if st.button("Search") and query:
        retriever = ResearchRetriever()
        results = retriever.retrieve(query)
        for r in results:
            st.subheader(r['title'])
            st.write(f"**Authors:** {r['authors']} | **Year:** {r['year']}")
            st.write(r['abstract'])
            st.divider()

def trend_analytics():
    st.title("Trend Analytics")
    
    if st.button("Analyze Trends"):
        with st.spinner("Running BERTopic and Growth Analysis..."):
            trends = analyze_trends()
        if trends:
            st.session_state.agent_history["trend_agent"] = trends
            n_papers = sum((t.get("papers_in_topic", 0) for t in trends))
            log_activity(f"Trend Agent -> clustered {n_papers} papers into {len(trends)} topics")
        else:
            st.warning("No trends found or database empty. Ensure ingestion is complete.")
            
    if "trend_agent" in st.session_state.agent_history:
        trends = st.session_state.agent_history["trend_agent"]
        st.subheader("Key Research Trends Identified:")
        
        # Display the rich insight reports natively
        for idx, t in enumerate(trends):
            if "insight_report" in t and t["insight_report"]:
                with st.expander(f"{idx+1}. {t.get('topic_name', 'Unnamed Topic')} ({t.get('trend_type', 'Unknown')})", expanded=(idx==0)):
                    st.markdown(t["insight_report"])
            else:
                st.write(f"**{idx+1}. {t.get('topic_name', 'Unnamed Topic')}**")
                st.write(f"- Trend Type: {t.get('trend_type', 'Unknown')}")
                st.write(f"- Growth Rate: {t['growth_rate']:.2f}")
                st.write(f"- Key Papers: {t['papers_in_topic']}")
        
        df = pd.DataFrame(trends)
        if 'trend_type' not in df.columns:
            df['trend_type'] = 'Unknown'
        if 'topic_name' not in df.columns:
            df['topic_name'] = 'Unnamed Topic'
            
        fig = px.bar(df, x='topic_id', y='growth_rate', color='trend_type', hover_data=['topic_name', 'papers_in_topic'], title='Topics Growth & Classification')
        st.plotly_chart(fig)

def gap_finder():
    st.title("Gap Finder")
    if st.button("Detect Research Gaps"):
        with st.spinner("Analyzing semantic + citation gaps..."):
            gaps = detect_gaps()
        if gaps:
            st.session_state.agent_history["gap_agent"] = gaps
            log_activity(f"Gap Agent -> analyzed numerous topic relationships")
            log_activity(f"Gap Agent -> detected {len(gaps)} potential research gaps")
        else:
            st.warning("No gaps found. Ensure citation graph & embeddings exist.")
            
    if "gap_agent" in st.session_state.agent_history:
        gaps = st.session_state.agent_history["gap_agent"]
        st.subheader("Top Research Opportunities")
        
        # Group by type
        grouped_gaps = {}
        for g in gaps:
            gtype = g.get('gap_type', 'Cross-Domain Gap')
            if gtype not in grouped_gaps:
                grouped_gaps[gtype] = []
            grouped_gaps[gtype].append(g)
            
        for gtype, items in grouped_gaps.items():
            st.markdown(f"### {gtype}s")
            for idx, g in enumerate(items):
                st.info(f"**Opportunity Score:** {g.get('gap_score', 0.0):.2f}")
                if 'gap_description' in g:
                    st.markdown(g['gap_description'])
                st.divider()

def method_planner():
    st.title("Methodology Planner")
    topic = st.text_input("Enter Research Gap Topic:")
    if st.button("Generate Methodology") and topic:
        with st.spinner("Designing methodology via LLM..."):
            planner = MethodPlanner()
            result = planner.plan_methodology(topic)
            st.session_state.agent_history["method_agent"] = result
            log_activity("Method Agent -> generated experiment plan")
            
    if "method_agent" in st.session_state.agent_history:
        st.markdown(st.session_state.agent_history["method_agent"]['plan_markdown'])

def proposal_generator():
    st.title("Grant Proposal Generator")
    topic = st.text_input("Topic:")
    methodology = st.text_area("Methodology Plan:")
    if st.button("Generate Proposal") and topic and methodology:
        with st.spinner("Synthesizing grant proposal..."):
            writer = ProposalWriter()
            retriever = ResearchRetriever()
            papers = retriever.retrieve(topic, top_k=5)
            md = writer.generate_proposal(topic, methodology, papers)
            st.session_state.agent_history["proposal_agent"] = md
            log_activity("Proposal Agent -> generated IEEE-style research proposal")
            
    if "proposal_agent" in st.session_state.agent_history:
        md = st.session_state.agent_history["proposal_agent"]
        st.markdown(md)
        
        # Export to PDF
        try:
            writer = ProposalWriter()
            pdf_path = writer.export_pdf(md, os.path.join(tempfile.gettempdir(), "proposal.pdf"))
            with open(pdf_path, "rb") as pdf_file:
                st.download_button("Download PDF", data=pdf_file, file_name="Grant_Proposal.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")

def research_insight_panel():
    st.title("Research Insight Panel")
    st.markdown("Synthesize a cohesive landscape summary using both Trend and Gap data.")
    
    if st.button("Generate Landscape Summary"):
        trends = st.session_state.agent_history.get("trend_agent", [])
        gaps = st.session_state.agent_history.get("gap_agent", [])
        
        if not trends or not gaps:
            st.warning("Please run Trend Analytics and Gap Finder first.")
            return
            
        with st.spinner("Synthesizing research landscape..."):
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
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
            chain = prompt | llm
            res = chain.invoke({"trends": trend_str, "gaps": gap_str})
            
            st.session_state.agent_history["insight_panel"] = res.content
            
    if "insight_panel" in st.session_state.agent_history:
        st.markdown(st.session_state.agent_history["insight_panel"])

def future_forecast_panel():
    st.title("Future Research Forecast")
    st.markdown("Predict High Impact Fields over the next 3 years based on current topic momentum.")
    
    if st.button("Generate Forecast (3-Year Horizon)"):
        trends = st.session_state.agent_history.get("trend_agent", [])
        
        if not trends:
            st.warning("Please run Trend Analytics first to establish baseline momentum.")
            return
            
        with st.spinner("Calculating future trajectories..."):
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
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
            chain = prompt | llm
            res = chain.invoke({"trends": trend_str})
            
            st.session_state.agent_history["future_forecast"] = res.content
            
    if "future_forecast" in st.session_state.agent_history:
        st.markdown(st.session_state.agent_history["future_forecast"])

def novelty_analyzer():
    st.title("Novelty Analyzer")
    proposal_text = st.text_area("Paste Proposal Text Here:")
    if st.button("Analyze Novelty") and proposal_text:
        with st.spinner("Scoring against vector database..."):
            scorer = NoveltyScorer()
            res = scorer.score_novelty(proposal_text)
            st.metric("Novelty Score", f"{res['novelty_score']:.2f}")
            st.metric("Max Similarity", f"{res['max_similarity']:.2f}")
            if res.get('closest_paper'):
                st.subheader("Closest Existing Paper:")
                st.json(res['closest_paper'])
            else:
                st.warning("Database may be empty.")

def citation_graph_viewer():
    st.title("Citation Graph Viewer")
    graph_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db', 'graphs', 'citation_graph.gpickle'))
    if os.path.exists(graph_path):
        if st.button("Render Graph"):
            with st.spinner("Rendering PyVis network..."):
                import pickle
                with open(graph_path, 'rb') as f:
                    G = pickle.load(f)
                
                # Fetch recent gaps to highlight
                gap_kw = set()
                if "gap_agent" in st.session_state.agent_history:
                    gaps = st.session_state.agent_history["gap_agent"]
                    for g in gaps:
                        gap_kw.update([k.strip() for k in g.get("t1_keywords", "").split(",")])
                        gap_kw.update([k.strip() for k in g.get("t2_keywords", "").split(",")])
                        
                # Subgraph for performance if too large
                if len(G.nodes) > 300:
                    import random
                    nodes = random.sample(list(G.nodes), 300)
                    G = G.subgraph(nodes).copy()
                
                for node, data in G.nodes(data=True):
                    # Color highlighting heuristic based on title matching gaps
                    title = data.get("title", "").lower()
                    highlight = any(k.lower() in title for k in gap_kw if len(k) > 3)
                    
                    if highlight:
                        data["color"] = "#ff4b4b"  # Streamlit red
                        data["size"] = 20
                    else:
                        data["color"] = "#97c2fc"
                        data["size"] = 10
                     
                net = Network(notebook=False, height="750px", width="100%", bgcolor="#222222", font_color="white")
                net.from_nx(G)
                 
                html_path = os.path.join(tempfile.gettempdir(), "graph.html")
                net.save_graph(html_path)
                 
                with open(html_path, 'r', encoding='utf-8') as f:
                    source_code = f.read() 
                components.html(source_code, height=800)
    else:
        st.warning("Citation graph not found. Run ingestion Phase 3 first.")

def agent_orchestrator():
    st.title("Autonomous Agent Orchestrator")
    st.write("Launch the full CrewAI agent team (Researcher, Trend Analyst, Gap Detector, Method Designer, Proposal Writer, and Scorer) to autonomously synthesize a proposal.")
    topic = st.text_input("Enter a broad research domain (e.g., 'Agentic Frameworks'):")
    if st.button("Launch Agent Crew") and topic:
        with st.spinner("Agents are collaborating to build your proposal... this may take a few minutes."):
            orchestrator = ResearchOrchestrator()
            try:
                result = orchestrator.run_pipeline(topic)
                st.success("Agents have completed their tasks!")
                st.markdown("### Final Output")
                st.write(result)
            except Exception as e:
                st.error(f"Agent execution failed: {e}")

if page == "1 Research Explorer": research_explorer()
elif page == "2 Trend Analytics": trend_analytics()
elif page == "3 Gap Finder": gap_finder()
elif page == "4 Method Planner": method_planner()
elif page == "5 Proposal Generator": proposal_generator()
elif page == "6 Novelty Analyzer": novelty_analyzer()
elif page == "7 Agent Orchestrator": agent_orchestrator()
elif page == "Citation Graph Viewer": citation_graph_viewer()
elif page == "Research Insight Panel": research_insight_panel()
elif page == "Future Forecast Panel": future_forecast_panel()
