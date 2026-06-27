#!/usr/bin/env python3
import math
import hashlib
from datetime import datetime, timezone

class MultiFactorSignalEngine:
    """
    Institutional Signal Engine: Evaluates AI Infrastructure opportunities
    across 5 completely deterministic, reproducible scoring dimensions.
    """
    def compute_composite_scores(self, raw_data):
        scored_playbook = []
        
        for asset, metrics in raw_data.items():
            # 1. Momentum Intensity (Velocity of volume shift)
            momentum = min(100, max(5, int(metrics["volume_delta"] * 40)))
            
            # 2. Anomaly Intensity (Z-Score variance mapped to an integer)
            z = abs(metrics["z_score"])
            anomaly = min(100, max(5, int((1 / (1 + math.exp(-z))) * 100)))
            
            # 3. Narrative Velocity Intensity (DETERMINISTIC: Mapped to real endpoint volatility)
            # Replaces legacy random.randint() completely to guarantee audit repeatability
            narrative = min(100, max(10, int(metrics["volatility"] * 200)))
            
            # 4. Liquidity Depth Score (Calculates log-scaled capital flow depth)
            liquidity = min(100, max(10, int(math.log10(metrics["volume_24h"] + 1) * 8.5)))
            
            # 5. Composite Signal Confidence (Independent factor agreement weighting)
            composite_score = int((momentum * 0.25) + (anomaly * 0.25) + (narrative * 0.20) + (liquidity * 0.30))
            
            # Compliance terminology shift away from trade advisory
            signal_status = "EXTREME_ANOMALY" if composite_score > 72 else "NOMINAL_VARIANCE"
            
            scored_playbook.append({
                "ticker": asset,
                "category": metrics["category"],
                "price": metrics["price"],
                "trend": signal_status,
                "momentum_score": momentum,
                "anomaly_score": anomaly,
                "narrative_score": narrative,
                "liquidity_score": liquidity,
                "conviction_score": composite_score,
                "z_score": metrics["z_score"],
                "probability_pct": metrics["probability_pct"],
                "kelly_fraction_pct": metrics["kelly_fraction_pct"],
                "source": metrics["source"],
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            
        return sorted(scored_playbook, key=lambda x: x["conviction_score"], reverse=True)
