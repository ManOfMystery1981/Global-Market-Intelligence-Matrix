#!/usr/bin/env python3
"""
collaborative_writer.py
Triple-Agent Report Generation Pipeline — Zero Cost Local Inference

Flow:
  1. finance-llama-8b  → writes dense initial report draft (2,500+ words)
                         (financially fine-tuned on 500k financial examples)
  2. deepseek-r1:7b    → audits report via chain-of-thought reasoning,
                         scores quality 0-100, flags specific issues
  3. finance-llama-8b  → rewrites based on DeepSeek R1's feedback
  4. Repeat 2-3 until quality score >= 90 or max 10 iterations
  5. Return final approved report text

Both models run locally via Ollama — zero API cost, zero rate limits.

Upgrade path (when revenue allows):
  Set WRITER_MODE=cloud and AUDITOR_MODE=cloud in environment to switch
  to DeepSeek V3 API (writer) and Grok 3 API (auditor) for higher quality.
  The rest of the pipeline is identical either way.
"""

import os
import json
import logging
import time
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger("CollaborativeWriter")

# ── Mode Selection ─────────────────────────────────────────────────────────────
# Set WRITER_MODE / AUDITOR_MODE to "cloud" to use paid APIs when available.
# Default is "local" — runs entirely free via Ollama on localhost:11434.
WRITER_MODE  = os.getenv("WRITER_MODE",  "local")   # "local" or "cloud"
AUDITOR_MODE = os.getenv("AUDITOR_MODE", "local")   # "local" or "cloud"

# ── Local Ollama Config (zero cost) ───────────────────────────────────────────
OLLAMA_HOST    = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LOCAL_WRITER   = "finance-llama-8b"    # Llama 3.1 8B fine-tuned on 500k financial examples
LOCAL_AUDITOR  = "deepseek-r1:7b"     # DeepSeek R1 — best free reasoning/audit model

# Upgrade path: Oracle Cloud with Palmyra-Fin-70B when hardware allows
ORACLE_WRITER  = "vanilj/palmyra-fin-70b-32k"  # CFA-passing 70B financial specialist

# ── Cloud API Config (paid, upgrade path only) ────────────────────────────────
DEEPSEEK_API_KEY  = os.getenv("DEEPSEEK_API_KEY", "")
GROK_API_KEY      = os.getenv("GROK_API_KEY", "")
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
GROK_ENDPOINT     = "https://api.x.ai/v1/chat/completions"
CLOUD_WRITER      = "deepseek-chat"
CLOUD_AUDITOR     = "grok-3"

# ── Pipeline Config ───────────────────────────────────────────────────────────
MAX_ITERATIONS    = 10
QUALITY_THRESHOLD = 90    # Slightly lower threshold for local 8B models vs frontier


# ── Inference Callers ─────────────────────────────────────────────────────────

def _call_ollama(model: str, messages: list, max_tokens: int = 2048,
                 temperature: float = 0.3) -> str:
    """
    Calls local Ollama instance via /api/chat endpoint.
    Streams token-by-token to avoid connection timeouts on slow CPU inference.
    """
    endpoint = f"{OLLAMA_HOST}/api/chat"
    payload = json.dumps({
        "model":    model,
        "messages": messages,
        "stream":   True,
        "options":  {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx":     4096,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    accumulated = []
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            while True:
                line = response.readline()
                if not line:
                    break
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        accumulated.append(token)
                    if chunk.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        return "".join(accumulated).strip()
    except Exception as e:
        raise RuntimeError(f"Ollama inference failed [{model}]: {e}")


def _call_cloud_api(endpoint: str, api_key: str, model: str, messages: list,
                    max_tokens: int = 4096, temperature: float = 0.3) -> str:
    """Calls a cloud API endpoint (OpenAI-compatible format)."""
    if not api_key:
        raise RuntimeError(f"No API key set for cloud model {model}. "
                           f"Set WRITER_MODE=local to use free local inference.")

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


def _write(messages: list, max_tokens: int = 2048) -> str:
    """Routes writing task to local or cloud model based on WRITER_MODE."""
    if WRITER_MODE == "cloud" and DEEPSEEK_API_KEY:
        logger.info(f"  ✍️  Writer: {CLOUD_WRITER} (cloud)")
        return _call_cloud_api(DEEPSEEK_ENDPOINT, DEEPSEEK_API_KEY,
                               CLOUD_WRITER, messages, max_tokens)
    else:
        logger.info(f"  ✍️  Writer: {LOCAL_WRITER} (local Ollama — free)")
        return _call_ollama(LOCAL_WRITER, messages, max_tokens)


def _audit(messages: list) -> str:
    """Routes audit task to local or cloud model based on AUDITOR_MODE."""
    if AUDITOR_MODE == "cloud" and GROK_API_KEY:
        logger.info(f"  🔍 Auditor: {CLOUD_AUDITOR} (cloud)")
        return _call_cloud_api(GROK_ENDPOINT, GROK_API_KEY,
                               CLOUD_AUDITOR, messages, 1024, 0.0)
    else:
        logger.info(f"  🔍 Auditor: {LOCAL_AUDITOR} (local Ollama — free)")
        return _call_ollama(LOCAL_AUDITOR, messages, 512, 0.0)


# ── Prompt Builders ───────────────────────────────────────────────────────────

def build_writer_messages(market_data: dict, report_type: str,
                          iteration: int, previous_issues: list = None) -> list:
    """Builds the writer prompt. On revision passes includes auditor feedback."""

    collected_at = market_data.get("collected_at", "N/A")
    crypto       = market_data.get("crypto", {})
    macro        = market_data.get("macro_fred", {})
    equities     = market_data.get("equities", {})
    defi         = market_data.get("defi_tvl", {})
    discrepancies = market_data.get("crypto_discrepancies", {})

    crypto_lines = "\n".join([
        f"  {sym}: ${d.get('price_usd', 0):,.2f} "
        f"({d.get('change_24h_pct', 0):+.2f}% 24h) "
        f"[Source: {d.get('source', 'CoinGecko')}]"
        for sym, d in crypto.items()
    ])

    macro_lines = "\n".join([
        f"  {name.replace('_',' ').title()}: {d.get('value','N/A')} "
        f"(as of {d.get('date','N/A')}) [FRED]"
        for name, d in macro.items()
    ])

    equity_lines = "\n".join([
        f"  {ticker} [{d.get('category','')}]: "
        f"${d.get('price_usd', 0):,.2f} ({d.get('change_24h_pct', 0):+.2f}%)"
        for ticker, d in list(equities.items())[:20]
    ])

    defi_lines = "\n".join([
        f"  {chain}: TVL ${d.get('tvl_usd', 0)/1e9:.2f}B"
        for chain, d in list(defi.items())[:5]
    ])

    discrepancy_note = ""
    if discrepancies:
        discrepancy_note = "\n⚠️  CROSS-SOURCE PRICE DISCREPANCIES — must be addressed:\n"
        for asset, d in discrepancies.items():
            discrepancy_note += (
                f"  {asset}: {d['sources']} — {d['divergence_pct']:.2f}% divergence\n"
            )

    revision_note = ""
    if previous_issues and iteration > 1:
        revision_note = (
            f"\n{'━'*50}\n"
            f"REVISION REQUIRED (Iteration {iteration}):\n"
            f"Address ALL of the following issues from the previous audit:\n"
            + "\n".join(f"  • {issue}" for issue in previous_issues)
            + f"\n{'━'*50}\n"
        )

    system = (
        "You are a senior institutional financial analyst specializing in "
        "quantitative market intelligence. You write premium research reports "
        "sold to hedge funds and institutional investors. Your writing is dense, "
        "specific, data-driven, and professional — in the style of top-tier "
        "investment bank research. Every paragraph cites specific numbers from "
        "the provided data. Never use filler or generic observations. "
        "Minimum 2,500 words per report."
    )

    user = f"""Generate a premium {report_type} intelligence report.
Data collected: {collected_at}

{'━'*50}
LIVE CRYPTOCURRENCY DATA:
{crypto_lines}

MACROECONOMIC INDICATORS (FRED):
{macro_lines}

EQUITY MARKET DATA:
{equity_lines}

DEFI ECOSYSTEM TVL:
{defi_lines}
{discrepancy_note}
{'━'*50}
{revision_note}

REPORT STRUCTURE (minimum word counts per section):

# {report_type} — Market Intelligence Brief
## Executive Summary (250+ words)
Dense, data-specific synthesis of the most critical market conditions.

## Section 1: Macroeconomic Environment & Liquidity (400+ words)
Analyze Fed policy, Treasury yields, CPI, M2 supply and their implications
for risk assets. Include yield curve analysis with specific basis point data.

## Section 2: Digital Asset Market Structure (400+ words)
Analyze each crypto asset with exact prices, volume trends, and market
structure. Address any cross-source discrepancies explicitly.

## Section 3: Equity Sector Analysis (400+ words)
Category-by-category breakdown. Identify strongest/weakest sectors
with specific price action and volume data.

## Section 4: DeFi & On-Chain Intelligence (300+ words)
TVL trends, capital flow patterns, protocol observations.

## Section 5: Risk Matrix & Tail Scenarios (300+ words)
At least 3 specific tail risk scenarios with trigger conditions
and probability assessments.

## Section 6: Actionable Intelligence (250+ words)
Top 3 specific opportunities and top 3 risks for the next 30 days.
Data-backed, not generic.

## Data Provenance
All sources with collection timestamps.

Write the complete report now. Minimum 2,500 words."""

    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]


def build_audit_messages(report_text: str, market_data: dict,
                         iteration: int) -> list:
    """Builds the DeepSeek R1 audit prompt. Requests structured JSON output."""

    crypto   = market_data.get("crypto", {})
    macro    = market_data.get("macro_fred", {})
    equities = market_data.get("equities", {})

    ground_truth = {
        "crypto_prices":      {sym: d.get("price_usd") for sym, d in crypto.items()},
        "macro_values":       {name: d.get("value") for name, d in macro.items()},
        "equity_ticker_count": len(equities),
        "equity_categories":  list(set(
            d.get("category", "") for d in equities.values()
        )),
    }

    system = (
        "You are a rigorous financial research quality auditor. "
        "Your job is to find every flaw, factual error, unsupported claim, "
        "and quality deficiency in submitted financial reports. "
        "You must respond ONLY with valid JSON. No prose outside the JSON."
    )

    user = f"""Audit this financial intelligence report (Iteration {iteration}).

VERIFIED GROUND TRUTH DATA:
{json.dumps(ground_truth, indent=2)}

REPORT TEXT (first 6000 chars):
{report_text[:6000]}

Return ONLY this JSON — no other text:
{{
  "quality_score": <integer 0-100>,
  "approved": <true if quality_score >= 90>,
  "word_count_estimate": <integer>,
  "issues": [
    "<specific issue with exact location>"
  ],
  "factual_errors": [
    "<any number/price contradicting ground truth>"
  ],
  "missing_sections": [
    "<any required section absent or thin>"
  ],
  "strengths": [
    "<what the report does well>"
  ],
  "revision_priority": [
    "<most critical fix>",
    "<second most critical>",
    "<third most critical>"
  ]
}}"""

    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user},
    ]


def parse_audit(raw: str) -> dict:
    """Safely parses the auditor's JSON response."""
    try:
        clean = raw.strip()
        # Strip <think> blocks from DeepSeek R1's chain-of-thought
        if "<think>" in clean and "</think>" in clean:
            clean = clean.split("</think>", 1)[-1].strip()
        # Strip markdown fences
        if "```" in clean:
            parts = clean.split("```")
            for part in parts:
                candidate = part.strip()
                if candidate.startswith("json"):
                    candidate = candidate[4:].strip()
                if candidate.startswith("{"):
                    clean = candidate
                    break
        return json.loads(clean)
    except Exception as e:
        logger.warning(f"Audit JSON parse failed: {e}. Raw: {raw[:200]}")
        return {
            "quality_score":     0,
            "approved":          False,
            "issues":            ["Audit response could not be parsed"],
            "factual_errors":    [],
            "missing_sections":  [],
            "revision_priority": ["Full rewrite required — audit parsing failed"],
        }


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def generate_report(market_data: dict,
                    report_type: str = "Cross-Asset Market Intelligence") -> dict:
    """
    Main entry point. Runs the writer→auditor→writer loop until
    quality >= QUALITY_THRESHOLD or MAX_ITERATIONS is reached.

    Returns:
        {
            "report_text":     str,
            "approved":        bool,
            "final_score":     int,
            "iterations_used": int,
            "audit_history":   list,
            "generated_at":    str,
            "models_used":     dict,
        }
    """
    writer_label  = CLOUD_WRITER  if WRITER_MODE  == "cloud" else LOCAL_WRITER
    auditor_label = CLOUD_AUDITOR if AUDITOR_MODE == "cloud" else LOCAL_AUDITOR

    logger.info(f"\n{'═'*55}")
    logger.info(f"  GMIM Collaborative Report Pipeline")
    logger.info(f"  Writer:  {writer_label} ({WRITER_MODE})")
    logger.info(f"  Auditor: {auditor_label} ({AUDITOR_MODE})")
    logger.info(f"  Report:  {report_type}")
    logger.info(f"  Max iterations: {MAX_ITERATIONS} | Threshold: {QUALITY_THRESHOLD}%")
    logger.info(f"{'═'*55}\n")

    audit_history   = []
    current_report  = ""
    previous_issues = []
    final_score     = 0
    approved        = False

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(f"{'─'*45}")
        logger.info(f"  Iteration {iteration}/{MAX_ITERATIONS}")
        logger.info(f"{'─'*45}")

        # ── Step 1: Writer generates (or revises) report ──────────────────────
        try:
            writer_msgs = build_writer_messages(
                market_data, report_type, iteration, previous_issues
            )
            current_report = _write(writer_msgs, max_tokens=2048)
            word_count = len(current_report.split())
            logger.info(f"  ✅ Draft complete: ~{word_count} words")
        except Exception as e:
            logger.error(f"  ❌ Writer failed: {e}")
            raise RuntimeError(f"Writer failed on iteration {iteration}: {e}")

        # ── Step 2: Auditor reviews the report ────────────────────────────────
        try:
            audit_msgs   = build_audit_messages(current_report, market_data, iteration)
            audit_raw    = _audit(audit_msgs)
            audit_result = parse_audit(audit_raw)
        except Exception as e:
            logger.error(f"  ❌ Auditor failed: {e}")
            raise RuntimeError(f"Auditor failed on iteration {iteration}: {e}")

        final_score = audit_result.get("quality_score", 0)
        approved    = audit_result.get("approved", False) or final_score >= QUALITY_THRESHOLD

        audit_history.append({
            "iteration":      iteration,
            "quality_score":  final_score,
            "approved":       approved,
            "word_count":     audit_result.get("word_count_estimate", 0),
            "issues":         audit_result.get("issues", []),
            "factual_errors": audit_result.get("factual_errors", []),
        })

        logger.info(f"  📊 Quality score: {final_score}/100 | Approved: {approved}")
        if audit_result.get("issues"):
            logger.info(f"  📋 Issues: {len(audit_result['issues'])}")
            for issue in audit_result["issues"][:3]:
                logger.info(f"     • {issue}")

        if approved:
            logger.info(f"\n  🏆 APPROVED on iteration {iteration} — score {final_score}/100")
            break

        if iteration < MAX_ITERATIONS:
            previous_issues = (
                audit_result.get("revision_priority", []) +
                audit_result.get("factual_errors", []) +
                audit_result.get("missing_sections", [])
            )
            logger.info(f"  🔄 Sending {len(previous_issues)} revision requests to writer...")
            time.sleep(1)
        else:
            logger.warning(f"\n  ⚠️  Max iterations reached. Final score: {final_score}/100")

    return {
        "report_text":     current_report,
        "approved":        approved,
        "final_score":     final_score,
        "iterations_used": len(audit_history),
        "audit_history":   audit_history,
        "report_type":     report_type,
        "generated_at":    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "models_used": {
            "writer":  writer_label,
            "auditor": auditor_label,
            "mode":    f"writer={WRITER_MODE}, auditor={AUDITOR_MODE}",
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    mock_data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "crypto": {
            "BTC": {"price_usd": 43256.78, "change_24h_pct": 2.34, "source": "CoinGecko"},
            "ETH": {"price_usd": 2356.42,  "change_24h_pct": -1.23, "source": "CoinGecko"},
            "SOL": {"price_usd": 98.32,    "change_24h_pct": 5.67, "source": "CoinGecko"},
        },
        "macro_fred": {
            "fed_funds_rate": {"value": 5.33, "date": "2026-06-01"},
            "10y_treasury":   {"value": 4.68, "date": "2026-06-30"},
            "cpi_inflation":  {"value": 3.1,  "date": "2026-05-01"},
        },
        "equities":             {},
        "defi_tvl":             {},
        "crypto_discrepancies": {},
    }
    result = generate_report(mock_data, "Arbitrage Opportunity Matrix")
    print(f"\nScore: {result['final_score']}/100 | "
          f"Iterations: {result['iterations_used']} | "
          f"Models: {result['models_used']}")
    print("\n--- First 500 chars of report ---")
    print(result["report_text"][:500])
