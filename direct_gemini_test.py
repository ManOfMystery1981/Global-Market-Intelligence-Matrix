#!/usr/bin/env python3
import os
import sys
import json
import logging
import requests
from data_collector_bot import MarketDataCollector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Direct_Gemini_Test")

class DirectTest:
    def __init__(self):
        self.collector = MarketDataCollector(production_mode=True)
        self.gemini_token = os.getenv("GEMINI_API_KEY")
        if not self.gemini_token:
            logger.critical("❌ Missing GEMINI_API_KEY environment variable.")
            sys.exit(1)

    def run(self):
        logger.info("🚀 Loading live market metrics directly from your collector...")
        raw_data = self.collector.collect_all_data()
        
        sol_price = raw_data.get("DEPI_1", {}).get("price", 75.00)
        btc_price = raw_data.get("MACR_1", {}).get("price", 60000.00)
        
        test_prompt = f"Analyze this data arbitrage profile. Solana spot index is currently at ${sol_price} USD and Bitcoin is tracking at ${btc_price} USD. Provide a brief 3-sentence risk thesis statement."
        
        logger.info("📡 Invoking absolute raw Google Gemini REST endpoint...")
        endpoint = "https://googleapis.com"
        
        payload = {
            "contents": [{"parts": [{"text": test_prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1000}
        }
        
        try:
            res = requests.post(endpoint, params={"key": self.gemini_token}, json=payload, timeout=30)
            logger.info(f"Target URL requested: {res.url}")
            res.raise_for_status()
            
            response_data = res.json()
            report_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            print("🔥 LIVE GEMINI RESPONSE TEXT:")
            print(report_text)
        except Exception as e:
            logger.error(f"❌ RAW ENDPOINT CRASH: {e}")

if __name__ == "__main__":
    DirectTest().run()
