#!/usr/bin/env python3
"""
collaborative_writer.py
Triple-Agent Report Generation Pipeline

Flow:
  1. DeepSeek V3  → writes dense initial report draft (2,500+ words)
  2. Grok 3       → audits report, scores quality, flags specific issues
  3. DeepSeek V3  → rewrites based on Grok's feedback
  4. Repeat 2-3 until Grok quality score >= 95 or max 10 iterations
  5. Return final approved report text
"""

import os
import json
import logging
import time
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

logger = logging.getLogger("CollaborativeWriter")

# ── API Configuration ─────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GROK_API_KEY     = os.getenv("GROK_API_KEY", "")

DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
GROK_ENDPOINT     = "https://api.x.ai/v1/chat/completions"

DEEPSEEK_MODEL    = "deepseek-chat"   # DeepSeek V3
GROK_MODEL        = "grok-3"          # Grok 3

MAX_ITERATIONS    = 10
QUALITY_THRESHOLD = 95                # Grok must score >= 95 to approve


def _call_api(endpoint: str, api_key: str, model: str, messages: list,
              max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Generic API caller for OpenAI-compatible endpoints."""
    if not api_key:
        raise RuntimeError(f"Missing API key for endpoint: {endpoint}")

    payload = json.dumps({
        "model":       model,
        "messages":    messages,
        "max_tokens":  max_tokens,
        "temperature": temperature,
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


def build_writer_prompt(market_data: dict, report_type: str, iteration: int,
                        previous_issues: list = None) -> list:
    """
    Constructs the DeepSeek writing prompt.
    On iteration > 1, includes Grok's specific feedback for targeted rewriting.
    """
    collected_at  = market_data.get("collected_at", "N/A")
    crypto        = market_data.get("crypto", {})
    macro         = market_data.get("macro_fred", {})
    equities      = market_data.get("equities", {})
    defi          = market_data.get("defi_tvl", {})
    discrepancies = market_data.get("crypto_discrepancies", {})

    # Build a concise data summary to keep within context limits
    crypto_summary = "\n".join([
        f"  {sym}: ${d.get('price_usd', 0):,.2f} ({d.get('change_24h_pct', 0):+.2f}% 24h)"
        for sym, d in crypto.items()
    ])

    macro_summary = "\n".join([
        f"  {name}: {d.get('value', 'N/A')} (as of {d.get('date', 'N/A')})"
        for name, d in macro.items()
    ])

    equity_summary = "\n".join([
        f"  {ticker} [{d.get('category', '')}]: ${d.get('price_usd', 0):,.2f} ({d.get('change_24h_pct', 0):+.2f}%)"
        for ticker, d in list(equities.items())[:20]
    ])

    defi_summary = "\n".join([
        f"  {chain}: TVL ${d.get('tvl_usd', 0)/1e9:.2f}B"
        for chain, d in list(defi.items())[:5]
    ])

    discrepancy_note = ""
    if discrepancies:
        discrepancy_note = "\n⚠️  CROSS-SOURCE PRICE DISCREPANCIES DETECTED (must be addressed in report):\n"
        for asset, disc in discrepancies.items():
            discrepancy_note += f"  {asset}: {disc['sources']} divergence of {disc['divergence_pct']:.2f}%\n"

    revision_note = ""
    if previous_issues and iteration > 1:
        revision_note = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVISION REQUEST (Iteration {iteration}):
The previous draft was rejected by the audit agent. Address ALL of the following:
{chr(10).join(f"  • {issue}" for issue in previous_issues)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    system_prompt = """You are a senior institutional research analyst producing premium financial intelligence reports sold to hedge funds and institutional investors at $2,500 per report.

Your reports must be:
- DENSE and SUBSTANTIVE: minimum 2,500 words of genuine analytical content
- SPECIFIC: cite exact prices, percentages, and data points from the provided data
- PROFESSIONAL: written in the style of Goldman Sachs, JP Morgan, or Bloomberg Intelligence reports
- STRUCTURED: use clear section headers, data tables, and analytical frameworks
- ACTIONABLE: provide specific insights, risk factors, and opportunity assessments
- HONEST about cross-source discrepancies when they exist

Do NOT use placeholder text, filler content, or generic observations. Every paragraph must contain specific data-backed analysis."""

    user_prompt = f"""Generate a premium {report_type} intelligence report based on the following real-time market data collected at {collected_at}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIVE CRYPTOCURRENCY PRICES (CoinGecko):
{crypto_summary}

MACROECONOMIC DATA (FRED):
{macro_summary}

EQUITY MARKET SNAPSHOT (Top 20 holdings):
{equity_summary}

DEFI ECOSYSTEM TVL:
{defi_summary}
{discrepancy_note}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{revision_note}

REQUIRED REPORT STRUCTURE:

# {report_type} — Intelligence Brief
## Executive Summary (250+ words)
Provide a dense, data-specific overview of the most critical market conditions and opportunities identified.

## Section 1: Macro Environment & Liquidity Conditions (400+ words)
Analyze FRED data (Fed Funds Rate, Treasury yields, CPI, M2) and their implications for risk assets. Include specific yield curve analysis.

## Section 2: Digital Asset Market Structure (400+ words)
Analyze each major crypto asset with specific price levels, volume patterns, and market structure observations. Address any cross-source price discrepancies noted above.

## Section 3: Equity Sector Analysis (400+ words)
Provide category-by-category analysis of the equity positions. Identify the strongest and weakest sectors with specific reasoning.

## Section 4: DeFi & On-Chain Intelligence (300+ words)
Analyze DeFi TVL trends across chains, capital flow patterns, and protocol-level observations.

## Section 5: Risk Matrix & Tail Scenarios (300+ words)
Identify specific risk factors with probability assessments. Include at least 3 distinct tail risk scenarios with trigger conditions.

## Section 6: Actionable Intelligence & Positioning (250+ words)
Provide specific, data-backed positioning recommendations. Identify the top 3 opportunities and top 3 risks for the next 30 days.

## Appendix: Data Provenance
List all data sources used with collection timestamps.

Write the complete report now. Minimum 2,500 words. Every claim must reference specific data from the provided dataset."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]


def build_audit_prompt(report_text: str, market_data: dict, iteration: int) -> list:
    """
    Constructs the Grok audit prompt.
    Grok checks factual accuracy, data citation, depth, and professional quality.
    Returns a structured JSON audit result.
    """
    crypto    = market_data.get("crypto", {})
    macro     = market_data.get("macro_fred", {})
    equities  = market_data.get("equities", {})

    # Give Grok the ground truth to verify against
    ground_truth = {
        "crypto_prices": {sym: d.get("price_usd") for sym, d in crypto.items()},
        "macro_values":  {name: d.get("value") for name, d in macro.items()},
        "equity_count":  len(equities),
        "equity_categories": list(set(d.get("category", "") for d in equities.values())),
    }

    system_prompt = """You are a ruthless financial research quality auditor. Your job is to find every flaw, factual error, unsupported claim, and quality deficiency in the report submitted to you.

You must respond ONLY with a valid JSON object. No prose, no markdown, no explanation outside the JSON structure."""

    user_prompt = f"""Audit the following financial intelligence report (Iteration {iteration}).

GROUND TRUTH DATA (verify all claims against this):
{json.dumps(ground_truth, indent=2)}

REPORT TO AUDIT:
{report_text[:8000]}

Respond with ONLY this JSON structure:
{{
  "quality_score": <integer 0-100>,
  "approved": <true if quality_score >= 95, false otherwise>,
  "word_count": <estimated word count>,
  "issues": [
    "<specific issue 1 with exact location in report>",
    "<specific issue 2>",
    ...
  ],
  "factual_errors": [
    "<any price, percentage, or data point that contradicts the ground truth>",
    ...
  ],
  "missing_sections": [
    "<any required section that is absent or under-developed>",
    ...
  ],
  "strengths": [
    "<what the report does well>",
    ...
  ],
  "revision_priority": [
    "<most critical fix needed>",
    "<second most critical fix>",
    "<third most critical fix>"
  ]
}}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]


def parse_audit_result(audit_response: str) -> Dict[str, Any]:
    """Parses Grok's JSON audit response safely."""
    try:
        # Strip any markdown code fences Grok might add
        clean = audit_response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception as e:
        logger.warning(f"Failed to parse audit JSON: {e}")
        return {
            "quality_score":      0,
            "approved":           False,
            "issues":             ["Audit response could not be parsed"],
            "factual_errors":     [],
            "missing_sections":   [],
            "revision_priority":  ["Fix all sections — audit parsing failed"],
        }


def generate_report(market_data: dict, report_type: str = "Cross-Asset Market Intelligence") -> dict:
    """
    Main entry point. Runs the DeepSeek→Grok→DeepSeek loop until
    quality >= QUALITY_THRESHOLD or MAX_ITERATIONS is reached.

    Returns:
        {
            "report_text":      str,
            "approved":         bool,
            "final_score":      int,
            "iterations_used":  int,
            "audit_history":    list,
            "generated_at":     str,
        }
    """
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY not set — cannot generate report")
    if not GROK_API_KEY:
        raise RuntimeError("GROK_API_KEY not set — cannot audit report")

    logger.info(f"📝 Starting collaborative report generation: {report_type}")
    logger.info(f"   Writer: {DEEPSEEK_MODEL} | Auditor: {GROK_MODEL}")
    logger.info(f"   Quality threshold: {QUALITY_THRESHOLD}% | Max iterations: {MAX_ITERATIONS}")

    audit_history   = []
    current_report  = ""
    previous_issues = []
    final_score     = 0
    approved        = False

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f"\n{'━'*50}")
        logger.info(f"  Iteration {iteration}/{MAX_ITERATIONS}")
        logger.info(f"{'━'*50}")

        # ── Step 1: DeepSeek writes (or rewrites) the report ─────────────────
        logger.info(f"  ✍️  DeepSeek writing draft...")
        try:
            writer_messages = build_writer_prompt(
                market_data, report_type, iteration, previous_issues
            )
            current_report = _call_api(
                DEEPSEEK_ENDPOINT, DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
                writer_messages, max_tokens=4096, temperature=0.3
            )
            word_count = len(current_report.split())
            logger.info(f"  ✅ Draft complete: {word_count} words")
        except Exception as e:
            logger.error(f"  ❌ DeepSeek write failed: {e}")
            raise RuntimeError(f"DeepSeek writer failed on iteration {iteration}: {e}")

        # ── Step 2: Grok audits the report ───────────────────────────────────
        logger.info(f"  🔍 Grok auditing draft...")
        try:
            audit_messages = build_audit_prompt(current_report, market_data, iteration)
            audit_response = _call_api(
                GROK_ENDPOINT, GROK_API_KEY, GROK_MODEL,
                audit_messages, max_tokens=1024, temperature=0.0
            )
            audit_result = parse_audit_result(audit_response)
        except Exception as e:
            logger.error(f"  ❌ Grok audit failed: {e}")
            raise RuntimeError(f"Grok auditor failed on iteration {iteration}: {e}")

        final_score = audit_result.get("quality_score", 0)
        approved    = audit_result.get("approved", False) or final_score >= QUALITY_THRESHOLD

        audit_history.append({
            "iteration":    iteration,
            "quality_score": final_score,
            "approved":     approved,
            "issues":       audit_result.get("issues", []),
            "factual_errors": audit_result.get("factual_errors", []),
        })

        logger.info(f"  📊 Grok score: {final_score}/100 | Approved: {approved}")

        if audit_result.get("issues"):
            logger.info(f"  📋 Issues found: {len(audit_result['issues'])}")
            for issue in audit_result["issues"][:3]:
                logger.info(f"     • {issue}")

        if approved:
            logger.info(f"\n  🏆 REPORT APPROVED on iteration {iteration} with score {final_score}/100")
            break

        if iteration < MAX_ITERATIONS:
            # Prepare consolidated feedback for next DeepSeek pass
            previous_issues = (
                audit_result.get("revision_priority", []) +
                audit_result.get("factual_errors", []) +
                audit_result.get("missing_sections", [])
            )
            logger.info(f"  🔄 Sending {len(previous_issues)} revision requests to DeepSeek...")
            time.sleep(2)  # Brief pause between iterations
        else:
            logger.warning(f"\n  ⚠️  Max iterations reached. Final score: {final_score}/100")

    return {
        "report_text":      current_report,
        "approved":         approved,
        "final_score":      final_score,
        "iterations_used":  len(audit_history),
        "audit_history":    audit_history,
        "report_type":      report_type,
        "generated_at":     datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


if __name__ == "__main__":
    # Test with minimal mock data
    mock_data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "crypto": {
            "BTC": {"price_usd": 43256.78, "change_24h_pct": 2.34},
            "ETH": {"price_usd": 2356.42,  "change_24h_pct": -1.23},
        },
        "macro_fred": {
            "fed_funds_rate": {"value": 5.33, "date": "2026-06-01"},
            "10y_treasury":   {"value": 4.68, "date": "2026-06-30"},
        },
        "equities":    {},
        "defi_tvl":    {},
        "crypto_discrepancies": {},
    }
    result = generate_report(mock_data, "Arbitrage Opportunity Matrix")
    print(f"Score: {result['final_score']}/100 | Iterations: {result['iterations_used']}")
    print(result["report_text"][:500])
