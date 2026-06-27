#!/usr/bin/env python3
"""
llm_analyst_bot.py
Generates professional data-arbitrage intelligence reports using the modern Gemini SDK.
Fully integrated with the unified data_collector_bot.py pipeline.
"""
import os
import sys
import time
from datetime import datetime
from google import genai
from google.genai import types

# Force local directory scanning for pipeline files
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Pipeline Ingestion & Safe Fallback Definitions
# ---------------------------------------------------------------------------
try:
    from delivery_bot import get_latest_data
except ImportError:
    print("⚠️  delivery_bot not found — using default trend structures")
    def get_latest_data():
        return {
            'trends': [
                "AI/ML adoption up 23% year-over-year across enterprise sectors",
                "Rust usage growing 15% among systems programmers",
                "Kubernetes remains dominant in cloud orchestration",
                "TypeScript surpasses Java in new project starts",
                "Edge computing frameworks see 40% increase in adoption",
            ],
            'metrics': [{"Total frameworks tracked": "45"}],
            'codebase_stats': {},
        }

try:
    from data_collector_bot import MarketDataCollector
except ImportError:
    print("⚠️  data_collector_bot not found — verify path location")
    class MarketDataCollector:
        def collect_all_data(self):
            return {"crypto": {}, "stocks": {}, "indices": {}}

# Import your centralized prompt constructor module
try:
    from llm_analyst_prompt import generate_arbitrage_section_prompt
except ImportError:
    raise ImportError("❌ Critical structural failure: llm_analyst_prompt.py is missing from this directory.")


# ---------------------------------------------------------------------------
# Gemini Execution Engine (Modern Client Framework)
# ---------------------------------------------------------------------------
class GeminiClient:
    """Thin wrapper around the modern google.genai SDK Client routing layers."""

    MODEL = "gemini-1.5-flash"  
    MAX_OUTPUT_TOKENS = 2048
    TEMPERATURE = 0.4

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set inside the runner environment. "
                "Add it as a GitHub Actions secret named GEMINI_API_KEY."
            )
        # Instantiate the official unified client object
        self.client = genai.Client(api_key=api_key)
        
        # Structure the modern system configuration block
        self.config = types.GenerateContentConfig(
            temperature=self.TEMPERATURE,
            max_output_tokens=self.MAX_OUTPUT_TOKENS,
            system_instruction=(
                "You are a Senior Quantitative Data Arbitrage Analyst writing for a "
                "professional institutional investment newsletter. "
                "Output ONLY the requested content — never echo back instructions, "
                "formatting rules, or section headings that were provided in the prompt. "
                "Write in perfect American English. Use round bullet points (•) for lists. "
                "Be precise with numbers and cite every data point you reference."
            )
        )

    def generate(self, prompt: str, section_label: str, retries: int = 3) -> str:
        """Calls the modern client execution layer to extract text payloads safely."""
        for attempt in range(1, retries + 1):
            try:
                print(f"  📡 Calling Gemini for [{section_label}] (attempt {attempt})…")
                
                # Modern SDK routing execution syntax
                response = self.client.models.generate_content(
                    model=self.MODEL,
                    contents=prompt,
                    config=self.config
                )
                
                text = response.text.strip()
                print(f"  ✅ [{section_label}] — {len(text)} chars")
                return text
            except Exception as exc:
                print(f"  ⚠️  Gemini client layer error (attempt {attempt}/{retries}): {exc}")
                if attempt < retries:
                    time.sleep(5 * attempt)
        print(f"  ❌ All {retries} production attempts failed for [{section_label}]")
        return ""


# ---------------------------------------------------------------------------
# Main Controller Execution Layer
# ---------------------------------------------------------------------------
class LLMAnalystBot:
    def __init__(self):
        self.client = GeminiClient()

    def _collect_data(self) -> dict:
        print("📊 Instantiating data pipeline ingestion matrices…")
        data: dict = {}

        try:
            base = get_latest_data()
            data['trend_data']   = base.get('trends', [])
            data['metrics_data'] = base.get('metrics', [])
        except Exception as e:
            print(f"  ⚠️  Trend layer aggregation data error: {e}")
            data['trend_data']   = []
            data['metrics_data'] = []

        try:
            market = MarketDataCollector().collect_all_data()
            data['crypto_data'] = market.get('crypto', {})
            data['stock_data']  = market.get('stocks', {})
            
            # Map parameters cleanly into the keys expected by llm_analyst_prompt.py
            data['os_data']      = market.get('os_market_share', {})
            data['company_data'] = market.get('company_metrics', {})
            data['market_data']  = market
        except Exception as e:
            print(f"  ⚠️  Market data extraction error: {e}")
            data['crypto_data'] = {}
            data['stock_data']  = {}
            data['os_data']     = {}
            data['company_data'] = {}

        return data

    def run_analysis(self):
        print("🔵 LLM Analyst Bot — Pipeline Ingestion Activated")
        raw_payload = self._collect_data()

        # Define map blocks for clear execution handoffs
        sections_to_generate = [
            ("Executive Arbitrage Summary", "executive_arbitrage_summary"),
            ("Regional SaaS Arbitrage", "regional_saas_arbitrage"),
            ("API Latency Arbitrage", "api_latency_arbitrage"),
            ("Crypto Arbitrage Spread", "crypto_arbitrage_spread"),
            ("Data Arbitrage Execution Vectors", "data_arbitrage_execution")
        ]

        sections = []
        for section_title, prompt_key in sections_to_generate:
            print(f"\n📝 Compiling Matrix Analytics for: {section_title}")
            
            # Route inputs cleanly through the imported prompt framework
            prompt = generate_arbitrage_section_prompt(
                section=prompt_key,
                trend_data=raw_payload.get('trend_data', []),
                metrics_data=raw_payload.get('metrics_data', []),
                crypto_data=raw_payload.get('crypto_data', {}),
                stock_data=raw_payload.get('stock_data', {}),
                os_data=raw_payload.get('os_data', {}),
                company_data=raw_payload.get('company_data', {}),
                market_data=raw_payload.get('market_data', {})
            )
            
            content = self.client.generate(prompt, section_title)
            if content:
                sections.append((section_title, content))
            else:
                print(f"  ⚠️  Skipping execution block for: {section_title}")

        # Assemble the clean text sections
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        article_parts = [
            f"# Data Arbitrage Intelligence Report\n\n**Generated:** {timestamp}\n",
        ]
        for name, content in sections:
            article_parts.append(f"\n## {name}\n\n{content}\n\n---\n")

        full_article = "\n".join(article_parts)

        # Write output matrix payload to disk
        fname = f"analyst_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(full_article)

        print(f"\n✅ Generation pipeline complete. Output file saved → {fname}")
        return full_article


if __name__ == "__main__":
    bot = LLMAnalystBot()
    bot.run_analysis()
