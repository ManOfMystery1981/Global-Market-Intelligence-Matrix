#!/usr/bin/env python3
import math
import random
from datetime import datetime, timezone

class MultiFactorSignalEngine:
    """
    Institutional Signal Engine: Evaluates AI Infrastructure opportunities
    across 5 distinct quantitative scoring dimensions.
    """
    def compute_composite_scores(self, raw_data):
        scored_playbook = []
        
        for asset, metrics in raw_data.items():
            # 1. Momentum Score (Velocity of price shift)
            momentum = min(100, max(5, int(metrics["volume_delta"] * 40)))
            
            # 2. Anomaly Score (Z-Score variation mapped to an integer)
            z = abs(metrics["z_score"])
            anomaly = min(100, max(5, int((1 / (1 + math.exp(-z))) * 100)))
            
            # 3. Narrative Score (Simulated attention metrics)
            narrative = random.randint(70, 98) if metrics["volume_delta"] > 1.7 else random.randint(35, 68)
            
            # 4. Liquidity Score (Calculates depth of institutional flow volume)
            liquidity = min(100, max(10, int(math.log10(metrics["volume_24h"] + 1) * 8.5)))
            
            # 5. Composite Conviction Score (Weighting formula)
            conviction = int((momentum * 0.25) + (anomaly * 0.25) + (narrative * 0.20) + (liquidity * 0.30))
            
            trend = "BREAKOUT" if conviction > 72 else "STABLE"
            
            scored_playbook.append({
                "ticker": asset,
                "category": metrics["category"],
                "price": metrics["price"],
                "trend": trend,
                "momentum_score": momentum,
                "anomaly_score": anomaly,
                "narrative_score": narrative,
                "liquidity_score": liquidity,
                "conviction_score": conviction,
                "z_score": metrics["z_score"],
                "probability_pct": metrics["probability_pct"],
                "kelly_fraction_pct": metrics["kelly_fraction_pct"],
                "source": metrics["source"],
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            
        return sorted(scored_playbook, key=lambda x: x["conviction_score"], reverse=True)
