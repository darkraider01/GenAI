"""
Responsible AI — Unified RAI Auditor Engine
Combines Content Safety, Bias Detection, and Transparency into a single audit report.
"""
from typing import Dict, List

from .guardrails import check_input_safety, check_output_safety
from .bias_detector import detect_bias
from .transparency import generate_transparency_report


class RAIAuditor:
    """
    Industry-grade Responsible AI auditor that runs three parallel checks:
    1. Content Safety (Guardrails) — input + output
    2. Bias Detection — confirmation, recency, homogeneity, vague attribution
    3. Transparency & Attribution — source grounding, confidence scoring
    """

    def audit(self, query: str, response: str, papers: List[Dict] = None) -> Dict:
        """
        Run all RAI checks for a given query-response-papers triple.

        Args:
            query: The original user research query.
            response: The AI-generated response text.
            papers: Retrieved RAG papers (optional, enriches analysis).

        Returns:
            A unified RAIReport dict.
        """
        papers = papers or []

        # Run all three checks
        input_safety = check_input_safety(query)
        output_safety = check_output_safety(response)
        bias_report = detect_bias(response, papers)
        transparency = generate_transparency_report(response, papers)

        # Compute an overall RAI score (0–100, higher = more responsible)
        safety_score = 100 if input_safety["safe"] and output_safety["safe"] else (
            60 if input_safety["risk_level"] in ("LOW", "MEDIUM") or output_safety["risk_level"] in ("LOW", "MEDIUM")
            else 20
        )
        bias_penalty = int(bias_report["bias_score"] * 40)
        confidence_bonus = int(transparency["avg_confidence"] * 20)
        overall_score = max(0, min(100, safety_score - bias_penalty + confidence_bonus))

        # Overall RAI status
        if overall_score >= 80:
            rai_status = "COMPLIANT"
            rai_color = "green"
        elif overall_score >= 55:
            rai_status = "REVIEW_RECOMMENDED"
            rai_color = "yellow"
        else:
            rai_status = "NON_COMPLIANT"
            rai_color = "red"

        return {
            "rai_status": rai_status,
            "rai_color": rai_color,
            "overall_score": overall_score,
            "safety": {
                "input": input_safety,
                "output": output_safety,
                "combined_risk": max(
                    ["SAFE", "LOW", "MEDIUM", "HIGH"].index(input_safety["risk_level"]),
                    ["SAFE", "LOW", "MEDIUM", "HIGH"].index(output_safety["risk_level"])
                )
            },
            "bias": bias_report,
            "transparency": transparency,
        }
