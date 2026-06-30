"""
signal_engine.py

Deterministic 5-factor market anomaly signal engine.
- Convert public market/research metrics into reproducible 0-100 factor scores.
- Generate a composite research signal with full traceability.
- Avoid random, stochastic, or non-repeatable scoring behavior.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional
import json
import math

MODEL_VERSION = "5_factor_deterministic_v1.0.0"

def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    if value is None or math.isnan(float(value)): return lower
    return max(lower, min(upper, float(value)))

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None: return default
        return float(value)
    except (TypeError, ValueError):
        return default

def stable_hash(payload: Dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + sha256(normalized.encode("utf-8")).hexdigest()

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

@dataclass(frozen=True)
class FactorScore:
    name: str
    score: float
    weight: float
    explanation: str
    inputs: Dict[str, Any]

@dataclass(frozen=True)
class CompositeSignal:
    asset: str
    model_version: str
    generated_at_utc: str
    composite_score: float
    classification: str
    confidence_band: str
    factor_scores: List[FactorScore]
    input_hash: str
    output_hash: str
    limitations: List[str]
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MultiFactorSignalEngine:
    """
    Institutional Signal Engine: Evaluates AI Infrastructure opportunities
    across 5 completely deterministic, reproducible scoring dimensions.
    """
    def compute_composite_scores(self, raw_data):
        scored_playbook = []
        
        for asset, metrics in raw_data.items():
            volume_delta = metrics.get("volume_delta", 0.0)
            z_score_raw = metrics.get("z_score", 0.0)
            volatility = metrics.get("volatility", 0.0)
            volume_24h = metrics.get("volume_24h", 0.0)

            momentum = min(100, max(5, int(volume_delta * 40)))
            z = abs(z_score_raw)
            anomaly = min(100, max(5, int((1 / (1 + math.exp(-z))) * 100)))
            narrative = min(100, max(10, int(volatility * 200)))
            liquidity = min(100, max(10, int(math.log10(volume_24h + 1) * 8.5)))
            composite_score = int((momentum * 0.25) + (anomaly * 0.25) + (narrative * 0.20) + (liquidity * 0.30))
            
            signal_status = "EXTREME_ANOMALY" if composite_score > 72 else "NOMINAL_VARIANCE"
            
            scored_playbook.append({
                "ticker": asset,
                "category": metrics.get("category", "AI Infrastructure"),
                "price": safe_float(metrics.get("price")),
                "trend": signal_status,
                "momentum_score": momentum,
                "anomaly_score": anomaly,
                "narrative_score": narrative,
                "liquidity_score": liquidity,
                "conviction_score": composite_score,
                "z_score": z,
                "model_score": safe_float(metrics.get("model_score", 50.0)),
                "signal_strength_pct": safe_float(metrics.get("signal_strength_pct", 50.0)),
                "source": metrics.get("source", "Public Exchange Feed"),
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            })

            
        return sorted(scored_playbook, key=lambda x: x["conviction_score"], reverse=True)

def score_price_momentum(metrics: Dict[str, Any]) -> FactorScore:
    change_24h = safe_float(metrics.get("price_change_24h_pct"))
    change_7d = safe_float(metrics.get("price_change_7d_pct"))
    change_30d = safe_float(metrics.get("price_change_30d_pct"))
    raw = (50.0 + change_24h * 0.70 + change_7d * 0.45 + change_30d * 0.20)
    score = clamp(raw)
    return FactorScore(
        name="price_momentum", score=round(score, 2), weight=0.25,
        explanation="Scores recent price strength using weighted 24h, 7d, and 30d percentage changes.",
        inputs={"price_change_24h_pct": change_24h, "price_change_7d_pct": change_7d, "price_change_30d_pct": change_30d}
    )

def score_volume_confirmation(metrics: Dict[str, Any]) -> FactorScore:
    volume_delta = safe_float(metrics.get("volume_delta"), 1.0)
    volume_change_24h_pct = safe_float(metrics.get("volume_change_24h_pct"))
    turnover_ratio = safe_float(metrics.get("turnover_ratio"))
    volume_delta_score = clamp((volume_delta - 1.0) * 45.0 + 50.0)
    volume_change_score = clamp(volume_change_24h_pct * 0.35 + 50.0)
    turnover_score = clamp(turnover_ratio * 500.0) if turnover_ratio > 0 else 50.0
    score = (volume_delta_score * 0.50 + volume_change_score * 0.30 + turnover_score * 0.20)
    return FactorScore(
        name="volume_confirmation", score=round(clamp(score), 2), weight=0.20,
        explanation="Scores whether trading activity confirms the observed market move.",
        inputs={"volume_delta": volume_delta, "volume_change_24h_pct": volume_change_24h_pct, "turnover_ratio": turnover_ratio, "volume_delta_score": round(volume_delta_score, 2), "volume_change_score": round(volume_change_score, 2), "turnover_score": round(turnover_score, 2)}
    )

def score_liquidity_quality(metrics: Dict[str, Any]) -> FactorScore:
    market_cap = safe_float(metrics.get("market_cap"))
    volume_24h = safe_float(metrics.get("volume_24h"))
    bid_ask_spread_pct = safe_float(metrics.get("bid_ask_spread_pct"), 1.0)
    exchange_count = safe_float(metrics.get("exchange_count"), 1.0)
    turnover = volume_24h / market_cap if market_cap > 0 else 0.0
    market_cap_score = clamp(math.log10(max(market_cap, 1.0)) * 8.0)
    turnover_score = clamp(turnover * 700.0)
    spread_score = clamp(100.0 - bid_ask_spread_pct * 25.0)
    venue_score = clamp(exchange_count * 8.0)
    score = (market_cap_score * 0.25 + turnover_score * 0.30 + spread_score * 0.25 + venue_score * 0.20)
    return FactorScore(
        name="liquidity_quality", score=round(clamp(score), 2), weight=0.20,
        explanation="Scores market depth, turnover, spread quality, and venue availability.",
        inputs={"market_cap": market_cap, "volume_24h": volume_24h, "turnover": round(turnover, 6), "bid_ask_spread_pct": bid_ask_spread_pct, "exchange_count": exchange_count, "market_cap_score": round(market_cap_score, 2), "turnover_score": round(turnover_score, 2), "spread_score": round(spread_score, 2), "venue_score": round(venue_score, 2)}
    )

def score_research_attention(metrics: Dict[str, Any]) -> FactorScore:
    source_count = safe_float(metrics.get("source_count"))
    mention_velocity = safe_float(metrics.get("mention_velocity"))
    repo_activity_score = safe_float(metrics.get("repo_activity_score"))
    news_count_24h = safe_float(metrics.get("news_count_24h"))
    social_volume_delta = safe_float(metrics.get("social_volume_delta"))
    volume_delta = safe_float(metrics.get("volume_delta"), 1.0)
    has_attention_inputs = any([source_count > 0, mention_velocity > 0, repo_activity_score > 0, news_count_24h > 0, social_volume_delta > 0])
    if has_attention_inputs:
        source_score = clamp(source_count * 8.0)
        velocity_score = clamp(mention_velocity * 25.0)
        repo_score = clamp(repo_activity_score)
        news_score = clamp(news_count_24h * 7.0)
        social_score = clamp((social_volume_delta - 1.0) * 40.0 + 50.0)
        score = (source_score * 0.20 + velocity_score * 0.25 + repo_score * 0.20 + news_score * 0.15 + social_score * 0.20)
        explanation = "Scores research attention using source breadth, mention velocity, repo activity, news count, and social-volume change."
    else:
        source_score = velocity_score = repo_score = news_score = social_score = 0.0
        score = clamp(volume_delta * 35.0)
        explanation = "Fallback deterministic attention score using volume_delta because richer attention inputs were unavailable."
    return FactorScore(
        name="research_attention", score=round(clamp(score), 2), weight=0.20, explanation=explanation,
        inputs={"source_count": source_count, "mention_velocity": mention_velocity, "repo_activity_score": repo_activity_score, "news_count_24h": news_count_24h, "social_volume_delta": social_volume_delta, "volume_delta_fallback": volume_delta, "source_score": round(source_score, 2), "velocity_score": round(velocity_score, 2), "repo_score": round(repo_score, 2), "news_score": round(news_score, 2), "social_score": round(social_score, 2), "used_fallback": not has_attention_inputs}
    )

def score_risk_adjustment(metrics: Dict[str, Any]) -> FactorScore:
    volatility_30d_pct = safe_float(metrics.get("volatility_30d_pct"), 50.0)
    max_drawdown_30d_pct = abs(safe_float(metrics.get("max_drawdown_30d_pct"), 25.0))
    concentration_top10_pct = safe_float(metrics.get("concentration_top10_pct"), 50.0)
    data_completeness_pct = safe_float(metrics.get("data_completeness_pct"), 75.0)
    volatility_score = clamp(100.0 - volatility_30d_pct)
    drawdown_score = clamp(100.0 - max_drawdown_30d_pct * 1.5)
    concentration_score = clamp(100.0 - concentration_top10_pct)
    completeness_score = clamp(data_completeness_pct)
    score = (volatility_score * 0.25 + drawdown_score * 0.25 + concentration_score * 0.25 + completeness_score * 0.25)
    return FactorScore(
        name="risk_adjustment", score=round(clamp(score), 2), weight=0.15,
        explanation="Scores volatility metrics, systemic holder concentrations, and structural data completeness parameters.",
        inputs={"volatility_30d_pct": volatility_30d_pct, "max_drawdown_30d_pct": max_drawdown_30d_pct, "concentration_top10_pct": concentration_top10_pct, "data_completeness_pct": data_completeness_pct}
    )

def classify_score(score: float) -> str:
    if score >= 85: return "Very Strong Research Signal"
    if score >= 70: return "Strong Research Signal"
    if score >= 55: return "Moderate Research Signal"
    if score >= 40: return "Weak / Mixed Research Signal"
    return "Low Research Signal"

def confidence_band(score: float) -> str:
    if score >= 80: return "High"
    if score >= 60: return "Medium"
    if score >= 45: return "Low-Medium"
    return "Low"

def compute_composite_score(factors: List[FactorScore]) -> float:
    total_weight = sum(f.weight for f in factors)
    if total_weight <= 0: return 0.0
    weighted_sum = sum(f.score * f.weight for f in factors)
    return round(clamp(weighted_sum / total_weight), 2)

def build_limitations(metrics: Dict[str, Any]) -> List[str]:
    limitations: List[str] = []
    required_fields = ["price_change_24h_pct", "price_change_7d_pct", "price_change_30d_pct", "volume_delta", "market_cap", "volume_24h"]
    missing = [field for field in required_fields if field not in metrics or metrics.get(field) is None]
    if missing: limitations.append(f"Missing core fields: {', '.join(missing)}.")
    attention_fields = ["source_count", "mention_velocity", "repo_activity_score", "news_count_24h", "social_volume_delta"]
    if not any(safe_float(metrics.get(field)) > 0 for field in attention_fields):
        limitations.append("Research attention score used deterministic fallback because richer attention inputs were unavailable.")
    if safe_float(metrics.get("data_completeness_pct"), 75.0) < 70:
        limitations.append("Data completeness is below preferred threshold; composite confidence should be discounted.")
    if safe_float(metrics.get("market_cap")) <= 0:
        limitations.append("Market capitalization unavailable or invalid; liquidity quality score may be less reliable.")
    if not limitations:
        limitations.append("Scores are deterministic and reproducible, but still dependent on source data quality and refresh cadence.")
    return limitations

def generate_signal(asset: str, metrics: Dict[str, Any]) -> CompositeSignal:
    normalized_input = {"asset": asset, "model_version": MODEL_VERSION, "metrics": metrics}
    input_hash = stable_hash(normalized_input)
    factors = [score_price_momentum(metrics), score_volume_confirmation(metrics), score_liquidity_quality(metrics), score_research_attention(metrics), score_risk_adjustment(metrics)]
    composite = compute_composite_score(factors)
    preliminary_output = {"asset": asset, "model_version": MODEL_VERSION, "composite_score": composite, "classification": classify_score(composite), "confidence_band": confidence_band(composite), "factor_scores": [asdict(factor) for factor in factors], "input_hash": input_hash, "limitations": build_limitations(metrics)}
    output_hash = stable_hash(preliminary_output)
    return CompositeSignal(asset=asset, model_version=MODEL_VERSION, generated_at_utc=utc_now_iso(), composite_score=composite, classification=classify_score(composite), confidence_band=confidence_band(composite), factor_scores=factors, input_hash=input_hash, output_hash=output_hash, limitations=build_limitations(metrics), metrics=metrics)

def calculate_signal(asset: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    return generate_signal(asset, metrics).to_dict()

def compute_composite_scores(asset_metrics: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for asset, metrics in asset_metrics.items():
        signal = generate_signal(asset=asset, metrics=metrics)
        results.append(signal.to_dict())
    return sorted(results, key=lambda row: row["composite_score"], reverse=True)

if __name__ == "__main__":
    sample_metrics = {
        "price_change_24h_pct": 2.4, "price_change_7d_pct": 8.7, "price_change_30d_pct": 15.2,
        "volume_delta": 1.85, "volume_change_24h_pct": 42.0, "turnover_ratio": 0.08,
        "market_cap": 1250000000, "volume_24h": 100_000_000, "bid_ask_spread_pct": 0.18,
        "exchange_count": 12, "source_count": 6, "mention_velocity": 2.1,
        "repo_activity_score": 64, "news_count_24h": 5, "social_volume_delta": 1.4,
        "volatility_30d_pct": 38, "max_drawdown_30d_pct": 18, "concentration_top10_pct": 32, "data_completeness_pct": 92
    }
    signal = generate_signal("SAMPLE", sample_metrics)
    print(json.dumps(signal.to_dict(), indent=2))
