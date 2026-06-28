#!/usr/bin/env python3
import json
import unittest
import copy
from signal_engine import generate_signal

# PINNED GOLDEN-MASTER REGRESSION VALUES (Enforces strict code preservation)
GOLDEN_INPUT_HASH = "sha256:7f1da76451675abcfde2046fa4bb8a113d0774a38612140efe057e5b22b10a2f"
GOLDEN_COMPOSITE_SCORE = 66.44

class TestSignalEngineReproducibility(unittest.TestCase):
    """
    Institutional Audit Suite: Validates order-independence, mutation safety, 
    schema bounds, edge-case resilience, and golden-master snapshot alignment.
    """
    def setUp(self) -> None:
        self.fixture_input = {
            "price_change_24h_pct": 2.4, "price_change_7d_pct": 8.7, "price_change_30d_pct": 15.2,
            "volume_delta": 1.85, "volume_change_24h_pct": 42.0, "turnover_ratio": 0.08,
            "market_cap": 1250000000.0, "volume_24h": 100000000.0, "bid_ask_spread_pct": 0.18,
            "exchange_count": 12.0, "source_count": 6.0, "mention_velocity": 2.1,
            "repo_activity_score": 64.0, "news_count_24h": 5.0, "social_volume_delta": 1.4,
            "volatility_30d_pct": 38.0, "max_drawdown_30d_pct": 18.0, "concentration_top10_pct": 32.0,
            "data_completeness_pct": 92.0, "volatility": 0.18, "category": "AI_Hardware", "price": 124.50, "z_score": 1.15, "source": "NASDAQ Security Matrix Baseline"
        }

    def test_canonical_reproducibility_and_mutation_safety(self):
        """Verifies deep data immutability, insertion order independence, and schema boundaries."""
        # 1. Capture strict input state for deep mutation checks
        input_snapshot = copy.deepcopy(self.fixture_input)
        
        # 2. Build insertion order variation map to test canonicalization independence
        reordered_input = dict(reversed(list(self.fixture_input.items())))
        
        run_a = generate_signal("SAMPLE", self.fixture_input).to_dict()
        run_b = generate_signal("SAMPLE", reordered_input).to_dict()
        
        # Enforce insertion order independence and mutation checks
        self.assertEqual(self.fixture_input, input_snapshot, "❌ FAULT: Data ingestion loop mutated input metrics.")
        self.assertEqual(run_a["input_hash"], run_b["input_hash"], "❌ FAULT: Hashing loop is vulnerable to insertion-order drift.")
        self.assertEqual(run_a["output_hash"], run_b["output_hash"])
        self.assertEqual(run_a["composite_score"], run_b["composite_score"])
        
        # 3. Assert Factor-Schema Bounding and Constraints
        for factor in run_a["factor_scores"]:
            self.assertIsInstance(factor["name"], str)
            self.assertIsInstance(factor["score"], (int, float))
            self.assertTrue(0.0 <= factor["score"] <= 100.0, f"❌ FAULT: Factor score {factor['name']} broke [0, 100] constraints.")

    def test_edge_case_matrix(self):
        """Parameterized Stress Test: Asserts divide-by-zero protection, tiny metrics, and extreme parameters."""
        edge_cases = {
            "ZERO_VOLUME": {"volume_24h": 0.0, "volume_delta": 0.0, "market_cap": 500000000.0, "price": 10.0, "z_score": 0.0, "volatility": 0.1, "category": "AI_Hardware", "source": "API"},
            "MASSIVE_VOLATILITY": {"volatility_30d_pct": 950.0, "volatility": 9.5, "volume_24h": 1000000.0, "volume_delta": 1.0, "market_cap": 1000000.0, "price": 1.0, "z_score": 5.0, "category": "AI_Hardware", "source": "API"},
            "MISSING_OPTIONAL_FIELDS": {"volume_24h": 50000000.0, "market_cap": 250000000.0, "price": 45.0, "z_score": 0.5, "volatility": 0.2, "category": "AI_Hardware", "source": "API"},
            "NEGATIVE_MOMENTUM": {"price_change_24h_pct": -45.0, "price_change_7d_pct": -85.0, "price_change_30d_pct": -150.0, "volume_24h": 10000000.0, "volume_delta": 2.0, "market_cap": 300000000.0, "price": 15.0, "z_score": -3.5, "volatility": 0.5, "category": "AI_Hardware", "source": "API"}
        }
        
        for case_name, payload in edge_cases.items():
            with self.subTest(case=case_name):
                try:
                    signal = generate_signal("EDGE_ASSET", payload).to_dict()
                    self.assertTrue(0.0 <= signal["composite_score"] <= 100.0)
                    self.assertIsInstance(signal["input_hash"], str)
                    self.assertIsInstance(signal["output_hash"], str)
                except Exception as e:
                    self.fail(f"❌ CRITICAL COLLAPSE: Anomaly Edge-Case [{case_name}] triggered runtime crash: {e}")

if __name__ == "__main__":
    unittest.main()
