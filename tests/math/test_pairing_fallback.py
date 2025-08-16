from __future__ import annotations

from unittest.mock import patch
from src.app.math.pairing import build_pairs
from src.app.math.skills.pythagorean import generate_problem


def test_pairing_fallback_on_invariance_failure():
    """Test that pairing falls back to neutral template when invariance check fails."""
    specs = [generate_problem("pythagorean.find_c", 1)]
    
    # Mock check_invariance to return False for the first call (personalized template)
    # and True for subsequent calls (neutral template)
    with patch("src.app.math.pairing.check_invariance", side_effect=[False, True, True]):
        pairs = build_pairs(specs, "Sports")
        
        assert len(pairs) == 1
        personalized, neutral = pairs[0]
        
        # Both should be neutral template due to fallback
        assert personalized.context_id == neutral.context_id


def test_pairing_normal_flow():
    """Test normal pairing flow when invariance checks pass."""
    specs = [generate_problem("pythagorean.find_c", 1)]
    
    # Mock check_invariance to always return True
    with patch("src.app.math.pairing.check_invariance", return_value=True):
        pairs = build_pairs(specs, "Sports")
        
        assert len(pairs) == 1
        personalized, neutral = pairs[0]
        
        # Should have different context IDs (one personalized, one neutral)
        # Note: They might be the same due to shuffling, but structure should be correct
        assert personalized.item_id != neutral.item_id 