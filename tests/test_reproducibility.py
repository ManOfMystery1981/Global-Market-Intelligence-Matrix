#!/usr/bin/env python3
import json
import unittest
import copy
from signal_engine import generate_signal

# REGRESSION LOCK CONSTANTS (Enforces absolute logic preservation)
GOLDEN_INPUT_HASH = "sha256:ffd40cfb5dc399f541fb03bf07573de059c21b1935a8abe0841af69e3b16fa6d"
GOLDEN_OUTPUT_HASH = "sha256:c3df6f26cb439d64dbeb63d6b3bd77b2948c455d79ab35def0b37244aa7c98d8"
GOLDEN_COMPOSITE_SCORE = 66.44
GOLDEN_OUTPUT_HASH = "sha256:c3df6f26cb439d64dbeb63d6b3bd77b2948c455d79ab35def0b37244aa7c98d8"
GOLDEN_COMPOSITE_SCORE = 66.44


GOLDEN_FACTOR_SCORES = {
    "price_momentum": 58.63,
    "volume_confirmation": 71.53,
    "liquidity_quality": 78.07,
    "research_attention": 53.98,
    "risk_adjustment": 73.75
}

class TestSignalEngineReproducibility(unittest.TestCase):
    """
    Institutional Audit Suite: Enforces golden-master preservation,
    uniqueness, mutation boundaries, and edge-case score bands.
    """
    def setUp(self) -> None:
        self.fixture_input = {
            "price_change_24h_pct": 2.4, "price_change_7d_pct": 8.7, "price_change_30d_pct": 15.2,
            "volume_delta": 1.85, "volume_change_24h_pct": 42.0, "turnover_ratio": 0.08,
            "market_cap": 1250000000.0, "volume_24h": 100000000.0, "bid_ask_spread_pct": 0.18,
            "exchange_count": 12.0, "source_count": 6.0, "mention_velocity": 2.1,
            "repo_activity_score": 64.0, "news_count_24h": 5.0, "social_volume_delta": 1.4,
            "volatility_30d_pct": 38.0, "max_drawdown_30d_pct": 18.0, "concentration_top10_pct": 32.0,
            "data_completeness_pct": 92.0, "volatility": 0.18, "category": "AI_Hardware", "price": 124.50, "z_score": 1.15, "source": "Local Verification Stream"
        }

    def test_canonical_reproducibility_and_mutation_safety(self):
        """Verifies deep data immutability, insertion order independence, and enforces golden master anchors."""
        input_snapshot = copy.deepcopy(self.fixture_input)
        reordered_input = dict(reversed(list(self.fixture_input.items())))
        
        run_a = generate_signal("SAMPLE", self.fixture_input).to_dict()
        run_b = generate_signal("SAMPLE", reordered_input).to_dict()
        
        # 1. Self-Consistency and Mutation Checks
        self.assertEqual(self.fixture_input, input_snapshot, "❌ FAULT: Data ingestion loop mutated input metrics.")
        self.assertEqual(run_a["input_hash"], run_b["input_hash"], "❌ FAULT: Hashing loop is vulnerable to insertion-order drift.")
        self.assertEqual(run_a["output_hash"], run_b["output_hash"])
        self.assertEqual(run_a["composite_score"], run_b["composite_score"])
        
        # 2. HARD ENFORCEMENT OF HISTORICAL GOLDEN MASTER VALUES
        self.assertEqual(run_a["input_hash"], GOLDEN_INPUT_HASH, "❌ REGRESSION: Input canonical hash has mutated.")
        self.assertEqual(run_a["output_hash"], GOLDEN_OUTPUT_HASH, "❌ REGRESSION: Output canonical hash has mutated.")
        self.assertEqual(run_a["composite_score"], GOLDEN_COMPOSITE_SCORE, "❌ REGRESSION: Math core drift detected.")
        
        # 3. Factor-Level Score Map Alignment Lock
        actual_factor_scores = {f["name"]: f["score"] for f in run_a["factor_scores"]}
        self.assertEqual(actual_factor_scores, GOLDEN_FACTOR_SCORES, "❌ REGRESSION: Internal factor weight distribution drift.")
        
        # 4. Duplicate Factor Name Elimination Check
        factor_names = [f["name"] for f in run_a["factor_scores"]]
        self.assertEqual(len(factor_names), len(set(factor_names)), "❌ SECURITY FAULT: Duplicate factor identifiers encountered.")

        # 5. Assert Factor Schema Bounding and Full Payload Integrity Constraints
        expected_keys = {"asset", "composite_score", "factor_scores", "input_hash", "output_hash", "classification", "confidence_band", "generated_at_utc", "model_version"}
        self.assertTrue(expected_keys.issubset(set(run_a.keys())), "❌ REGRESSION: Signal output payload structure has drifted or keys are missing.")

        for factor in run_a["factor_scores"]:
            self.assertIsInstance(factor["name"], str)
            self.assertIsInstance(factor["score"], (int, float))
            self.assertTrue(0.0 <= factor["score"] <= 100.0, f"❌ FAULT: Factor score {factor['name']} broke constraints.")

    def test_edge_case_matrix(self):
        """Parameterized Stress Test: Checks divide-by-zero bounds and asserts expected behavioral scoring ranges."""
        edge_cases = {
            "ZERO_VOLUME": {"volume_24h": 0.0, "volume_delta": 0.0, "market_cap": 500000000.0, "price": 10.0, "z_score": 0.0, "volatility": 0.1, "category": "AI_Hardware", "source": "API"},
            "MASSIVE_VOLATILITY": {"volatility_30d_pct": 950.0, "volatility": 9.5, "volume_24h": 1000000.0, "volume_delta": 1.0, "market_cap": 1000000.0, "price": 1.0, "z_score": 5.0, "category": "AI_Hardware", "source": "API"},
            "MISSING_OPTIONAL_FIELDS": {"volume_24h": 50000000.0, "market_cap": 250000000.0, "price": 45.0, "z_score": 0.5, "volatility": 0.2, "category": "AI_Hardware", "source": "API"},
            "NEGATIVE_MOMENTUM": {"price_change_24h_pct": -45.0, "price_change_7d_pct": -85.0, "price_change_30d_pct": -150.0, "volume_24h": 10000000.0, "volume_delta": 2.0, "market_cap": 300000000.0, "price": 15.0, "z_score": -3.5, "volatility": 0.5, "category": "AI_Hardware", "source": "API"}
        }
        
        # Enforce operational value boundaries per alternative trend anomaly
        expected_ranges = {
            "ZERO_VOLUME": (0.0, 60.0),
            "MASSIVE_VOLATILITY": (0.0, 55.0),
            "MISSING_OPTIONAL_FIELDS": (10.0, 90.0),
            "NEGATIVE_MOMENTUM": (0.0, 50.0)
        }
        
        for case_name, payload in edge_cases.items():
            with self.subTest(case=case_name):
                signal = generate_signal("EDGE_ASSET", payload).to_dict()
                score = signal["composite_score"]
                
                min_bound, max_bound = expected_ranges[case_name]
                self.assertTrue(min_bound <= score <= max_bound, f"❌ FAIL: Edge case [{case_name}] produced unexpected outlying score: {score}")

if __name__ == "__main__":
    unittest.main()
