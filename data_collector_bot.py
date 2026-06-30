#!/usr/bin/env python3
"""
data_collector_bot.py
Dynamic Ingestion Core with Intermittent Low-TTL Micro-Burst Subroutines
"""

import os
import json
import logging
import time
import re
import urllib.request
import urllib.parse
import urllib.error
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A_Plus_Compliance_Collector")

class MarketDataCollector:
    def __init__(self, production_mode: bool = True):
        self.production_mode = production_mode
        self.endpoint = "http://localhost:11434/api/generate"
        try:
            probe_req = urllib.request.Request("http://local_llm_core:11434/api/tags", method="GET")
            with urllib.request.urlopen(probe_req, timeout=2) as _:
                self.endpoint = "http://local_llm_core:11434/api/generate"
        except Exception:
            pass

    def _query_ai_short_burst(self, prompt: str, token_limit: int = 128) -> str:
        """Executes a quick connection pass with low TTL to keep bandwidth lean and avoid hangs."""
        payload = {
            "model": "dolphin-mistral",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": token_limit}
        }
        try:
            json_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.endpoint, data=json_bytes, headers={"Content-Type": "application/json"}, method="POST")
            # Tight 45-second socket window pings often but prevents the server from timing out
            with urllib.request.urlopen(req, timeout=45) as response:
                res = json.loads(response.read().decode("utf-8"))
            return res["response"].strip()
        except Exception as e:
            logger.warning(f"⚠️ Micro-burst subroutine timed out or failed: {e}")
            return ""

    def _discover_trending_categories_via_ai(self) -> list:
        logger.info("🧠 Polling local AI to dynamically extract prominent macro thematic sectors...")
        cat_prompt = (
            "Identify exactly 5 prominent unique trending tech sectors driving current market liquidity. "
            "Wrap your output array inside structural anchor tags exactly like this: "
            "START_MATRIX[\"AI_Hardware\", \"Data_Centers\"]END_MATRIX. Do not provide conversational filler."
        )
        cat_raw = self._query_ai_short_burst(cat_prompt, token_limit=192)
        cat_match = re.search(r'START_MATRIX(.*?)END_MATRIX', cat_raw, re.DOTALL)
        
        if cat_match:
            try:
                return json.loads(cat_match.group(1).strip())[:5]
            except Exception:
                pass
        return ["AI_Hardware", "Data_Centers", "Uranium_Feeds", "Grid_Power", "Semiconductors"]

    def _resolve_category_to_tickers_subroutine(self, category: str) -> list:
        """Subroutine: Extracts tickers individually in chunks of 2 to lower traffic and avoid flooding."""
        clean_category = str(category).replace(" ", "_")
        logger.info(f"📡 Invoking ticker extraction subroutine for category: {clean_category}...")
        
        ticker_prompt = (
            f"For the technology field '{clean_category}', provide exactly 2 highly liquid stock tickers or index ETFs. "
            "Wrap your response inside structural tags exactly like this: START_TICKERS[\"NVDA\", \"AMD\"]END_TICKERS. "
            "Output ONLY clean tickers. Never include exchange prefixes like NASDAQ:."
        )
        ticker_raw = self._query_ai_short_burst(ticker_prompt, token_limit=64)
        ticker_match = re.search(r'START_TICKERS(.*?)END_TICKERS', ticker_raw, re.DOTALL)
        
        if ticker_match:
            try:
                return json.loads(ticker_match.group(1).strip())[:2]
            except Exception:
                pass
        return ["SPY", "QQQ"]

    def get_market_intelligence(self) -> dict:
        intelligence = {}
        discovered_categories = self._discover_trending_categories_via_ai()
        
        for category in discovered_categories:
            tickers = self._resolve_category_to_tickers_subroutine(category)
            for ticker in tickers:
                ticker_str = str(ticker).upper().strip().split(":")[-1]
                if ticker_str == "FB": ticker_str = "META"
                if ticker_str in intelligence: continue

                try:
                    t = yf.Ticker(ticker_str)
                    hist = t.history(period="30d")
                    if not hist.empty and len(hist) >= 2:
                        current_price = float(hist["Close"].iloc[-1])
                        price_24h_ago = float(hist["Close"].iloc[-2])
                        historical_avg_volume = float(hist["Volume"].mean())
                        volume_24h = float(hist["Volume"].iloc[-1])
                        
                        # Claude's Defensive Patch: Collect parameters safely without hard collisions
                        intelligence[ticker_str] = {
                            "price": round(current_price, 2),
                            "volume_24h": volume_24h,
                            "historical_avg_volume": historical_avg_volume,
                            "volatility": round(float(hist["Close"].pct_change().std()), 4),
                            "volume_delta": round(volume_24h / historical_avg_volume, 4) if historical_avg_volume else 1.0,
                            "category": str(category).replace(" ", "_"),
                            "z_score": 0.0,
                            "price_change_24h_pct": round(((current_price - price_24h_ago) / price_24h_ago * 100), 2) if price_24h_ago else 0.0,
                        }
                except Exception:
                    pass
                time.sleep(0.1) # Shorter intermittent cool-down gap 
                
        return intelligence

    def collect_all_data(self) -> dict:
        return self.get_market_intelligence()

if __name__ == "__main__":
    for ticker, payload in MarketDataCollector(production_mode=False).collect_all_data().items():
        print(ticker, payload)
