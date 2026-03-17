"""
Responsible AI — Bias Detector
Analyzes AI-generated research content for common academic biases.
"""
import re
from typing import Dict, List


def _count_date_recency(text: str) -> float:
    """Detect recency bias: what fraction of year-mentions are in the last 3 years."""
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if not years:
        return 0.0
    recent = [y for y in years if int(y) >= 2021]
    return round(len(recent) / len(years), 2)


def _detect_one_sided_language(text: str) -> bool:
    """Confirmation bias: check for absolute language with no counter-argument."""
    absolutes = ["always", "never", "clearly proves", "undeniably", "all studies show",
                 "only approach", "the definitive", "without exception"]
    counters = ["however", "on the other hand", "alternatively", "in contrast",
                "debate", "limitation", "criticism", "counter"]
    abs_hit = sum(1 for a in absolutes if a in text.lower())
    counter_hit = sum(1 for c in counters if c in text.lower())
    return abs_hit >= 2 and counter_hit == 0


def detect_bias(response: str, papers: List[Dict] = None) -> Dict:
    """
    Runs a multi-dimensional bias analysis on an AI-generated research response.
    
    Args:
        response: The LLM-generated text to analyze.
        papers: Optional list of retrieved papers (for citation homogeneity check).
    
    Returns:
        A dict with bias flags, a bias score 0.0-1.0, and recommendations.
    """
    bias_flags = []
    papers = papers or []

    # 1. Recency Bias
    recency_ratio = _count_date_recency(response)
    if recency_ratio > 0.8:
        bias_flags.append({
            "type": "Recency Bias",
            "severity": "MEDIUM",
            "detail": f"{int(recency_ratio*100)}% of cited years are post-2021. Consider including foundational works."
        })

    # 2. Confirmation Bias
    if _detect_one_sided_language(response):
        bias_flags.append({
            "type": "Confirmation Bias",
            "severity": "MEDIUM",
            "detail": "Absolute language detected with no counter-arguments. Consider presenting opposing views."
        })

    # 3. Citation Homogeneity (if papers provided)
    if papers:
        total = len(papers)
        authors_text = " ".join([p.get("authors", "") for p in papers]).lower()
        # Very basic: check if any single token appears too often as author indicator
        if total > 0:
            # Check if majority of papers are from the same first-author initial heuristic
            first_authors = [p.get("authors", "").split(",")[0].strip() for p in papers if p.get("authors")]
            if first_authors and len(set(first_authors)) < max(1, total // 2):
                bias_flags.append({
                    "type": "Citation Homogeneity",
                    "severity": "LOW",
                    "detail": "Retrieved papers appear to share similar authorship. Consider broadening the search."
                })

    # 4. Vague evidence bias
    vague_phrases = ["some studies suggest", "it is generally believed", "many researchers think", "experts say"]
    vague_count = sum(1 for v in vague_phrases if v in response.lower())
    if vague_count >= 2:
        bias_flags.append({
            "type": "Vague Attribution",
            "severity": "LOW",
            "detail": "Multiple vague attributions detected. Prefer citing specific papers for academic rigor."
        })

    # Score: 0 = unbiased, 1 = heavily biased
    severity_weights = {"HIGH": 0.4, "MEDIUM": 0.25, "LOW": 0.1}
    bias_score = min(1.0, sum(severity_weights.get(f["severity"], 0.1) for f in bias_flags))

    recommendation = (
        "No significant bias detected. Output meets academic standards." if not bias_flags
        else "Consider revising to address the flagged biases before publication or sharing."
    )

    return {
        "bias_flags": bias_flags,
        "bias_score": round(bias_score, 2),
        "bias_count": len(bias_flags),
        "recommendation": recommendation
    }
