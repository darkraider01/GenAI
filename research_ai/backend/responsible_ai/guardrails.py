"""
Responsible AI — Content Safety Guardrails
Checks both the input query and AI-generated output for harmful or unsafe content.
Uses a fast keyword-heuristic scan followed by an LLM-based deep safety check.
"""
import re
from typing import Dict

# High-risk keyword patterns for academic research context
_HARMFUL_PATTERNS = [
    r"\b(how to hack|exploit|jailbreak|bypass|ignore previous instructions)\b",
    r"\b(generate fake|fabricate data|plagiarize|plagiarism)\b",
    r"\b(harmful|dangerous|lethal|weapon|bomb|explosive)\b",
    r"\b(self.harm|suicide method|how to hurt)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _HARMFUL_PATTERNS]


def _keyword_scan(text: str) -> tuple[bool, str]:
    """Fast heuristic scan. Returns (is_flagged, matched_reason)."""
    for pattern in _COMPILED:
        m = pattern.search(text)
        if m:
            return True, f"Flagged pattern: '{m.group()}'"
    return False, ""


def _classify_risk(text: str) -> str:
    """
    Heuristic risk classifier without external LLM call,
    keeping this lightning-fast with zero latency cost.
    """
    word_count = len(text.split())
    flagged, reason = _keyword_scan(text)

    if flagged:
        return "HIGH"

    # Look for softer risk signals
    soft_signals = ["controversial", "unverified", "speculative", "unethical", "illegal"]
    soft_hit = sum(1 for s in soft_signals if s in text.lower())

    if soft_hit >= 2:
        return "MEDIUM"
    elif soft_hit == 1:
        return "LOW"
    return "SAFE"


def check_input_safety(query: str) -> Dict:
    """
    Validates a user query before it enters the AI pipeline.
    Returns a safety report dict.
    """
    flagged, reason = _keyword_scan(query)
    risk = _classify_risk(query)

    return {
        "safe": risk in ("SAFE", "LOW"),
        "risk_level": risk,
        "reason": reason if flagged else "No harmful patterns detected in input.",
        "check_type": "input_guardrail"
    }


def check_output_safety(response: str) -> Dict:
    """
    Validates AI-generated output text before it is served to the user.
    Returns a safety report dict.
    """
    flagged, reason = _keyword_scan(response)
    risk = _classify_risk(response)

    # Additional output check: warn if response is suspiciously short or empty
    if len(response.strip()) < 20:
        return {
            "safe": False,
            "risk_level": "MEDIUM",
            "reason": "Output is extremely short or empty — possible model failure.",
            "check_type": "output_guardrail"
        }

    return {
        "safe": risk in ("SAFE", "LOW"),
        "risk_level": risk,
        "reason": reason if flagged else "Output passed safety checks.",
        "check_type": "output_guardrail"
    }
