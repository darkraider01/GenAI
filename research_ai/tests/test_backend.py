import pytest
import os
import sys

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.evaluation.novelty_score import NoveltyScorer

def test_novelty_scorer_initialization():
    scorer = NoveltyScorer()
    assert scorer is not None
    assert hasattr(scorer, 'paper_embeddings')
    assert hasattr(scorer, 'papers_data')

def test_novelty_score_output_format():
    scorer = NoveltyScorer()
    test_text = "A brand new quantum computing approach to agentic AI."
    result = scorer.score_novelty(test_text)
    
    assert "novelty_score" in result
    assert "max_similarity" in result
    assert "closest_paper" in result
    
    # Check bounds
    assert 0.0 <= result["novelty_score"] <= 1.0
    assert 0.0 <= result["max_similarity"] <= 1.0
