"""
Responsible AI — Transparency & Attribution
Provides source attribution tracking and confidence scoring for AI-generated responses.
"""
from typing import Dict, List


def _estimate_grounding_confidence(response: str, papers: List[Dict]) -> float:
    """
    Estimate how well-grounded the response is in the retrieved papers.
    Uses lightweight keyword overlap between response and paper abstracts.
    """
    if not papers:
        return 0.3  # No papers = low confidence (LLM hallucination risk)
    
    response_words = set(response.lower().split())
    # Remove stopwords
    stopwords = {"the", "a", "an", "is", "in", "of", "and", "to", "that", "for",
                "it", "with", "as", "at", "by", "from", "this", "are", "was", "were"}
    response_words -= stopwords

    overlap_scores = []
    for paper in papers:
        abstract = paper.get("abstract", "") + " " + paper.get("title", "")
        paper_words = set(abstract.lower().split()) - stopwords
        if not paper_words:
            continue
        overlap = len(response_words & paper_words) / max(len(paper_words), 1)
        overlap_scores.append(min(overlap * 5, 1.0))  # Scale up for readability

    if not overlap_scores:
        return 0.35
    return round(min(sum(overlap_scores) / len(overlap_scores), 1.0), 2)


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "HIGH"
    elif score >= 0.45:
        return "MEDIUM"
    else:
        return "LOW"


def generate_transparency_report(response: str, papers: List[Dict]) -> Dict:
    """
    Generates a transparency and attribution report for an AI response.
    
    Args:
        response: The LLM-generated text.
        papers: List of papers retrieved by the RAG pipeline.
    
    Returns:
        A dict with attribution metadata, confidence score, and explanation.
    """
    sources_cited = len(papers)
    confidence = _estimate_grounding_confidence(response, papers)
    label = _confidence_label(confidence)

    # Build attribution summary
    attributions = []
    for i, p in enumerate(papers[:5]):
        title = p.get("title", f"Paper {i+1}")
        year = p.get("year", "N/A")
        authors = p.get("authors", "Unknown Authors")
        sim = p.get("similarity", None)
        entry = {
            "title": title,
            "authors": authors[:80] + "..." if len(authors) > 80 else authors,
            "year": year,
            "relevance_score": round(sim, 3) if sim is not None else "N/A"
        }
        attributions.append(entry)

    attribution_summary = (
        f"Response grounded in {sources_cited} retrieved papers via semantic RAG retrieval. "
        f"Confidence: {label} ({int(confidence * 100)}%). "
        + ("Strong grounding in literature detected." if label == "HIGH" 
           else "Moderate grounding — some claims may reflect LLM training data." if label == "MEDIUM"
           else "Weak grounding — treat response with caution; verify claims independently.")
    )

    return {
        "sources_cited": sources_cited,
        "avg_confidence": confidence,
        "confidence_label": label,
        "confidence_percent": int(confidence * 100),
        "attribution_summary": attribution_summary,
        "top_sources": attributions
    }
