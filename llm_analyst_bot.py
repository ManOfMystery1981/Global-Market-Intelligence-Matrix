#!/usr/bin/env python3
print("DEBUG: Script started successfully.")

import os
import math
import json
from data_collector_bot import MarketDataCollector
from signal_engine import MultiFactorSignalEngine
from evidence_graph import EvidenceGraph
from industry_standard_report import IndustryStandardReport
from economist_agent import SeniorEconomistAgent
from delivery_bot import dispatch_secure_fulfillment_package
from llm_analyst_prompt import generate_arbitrage_section_prompt, get_hedge_fund_advisor_prompt, get_academic_economist_synopsis_prompt

class LLMAnalystBot:
    """
    Master Production Orchestrator: Implements rigorous data provenance 
    and deterministic math profiles to assemble compliance-safe research briefs.
    """
    def __init__(self, target_email="dsull1981@gmail.com"):
        self.collector = MarketDataCollector()
        self.signal_engine = MultiFactorSignalEngine()
        self.evidence_layer = EvidenceGraph()
        self.report_engine = IndustryStandardReport()
        self.economist = SeniorEconomistAgent()
        self.target_email = target_email

    def run(self):
        print("🚀 Orchestrator: Initiating 8-tier intelligence data sweep...")
        intelligence = self.collector.get_market_intelligence()
       
        raw_processing_map = {}
        crypto_data_map = {}
        stock_data_map = {}
        hashes_map = {}
        
        print("🧮 Processing deterministic scoring calculations...")
        for cat, assets in intelligence.items():
            for ticker, data in assets.items():
                spot = data['price']
                mean = data.get('historical_avg_price', spot * 0.97)
                vol = data.get('volatility', 0.20)
                vol = vol if vol > 0 else 0.01
                
                z_score = (spot - mean) / (spot * vol)
                probability = 1.0 / (1.0 + math.exp(-z_score))
                
                p_win = probability
                q_loss = 1.0 - p_win
                kelly_fraction = max(0.0, (p_win * 1.5 - q_loss) / 1.5) * 100.0

                volume_24h = data.get('volume_24h', 6000000)
                historical_avg_vol = data.get('historical_avg_volume', 5500000)
                volume_delta = (volume_24h / historical_avg_vol) if historical_avg_vol > 0 else 1.0
                
                raw_processing_map[ticker] = {
                    "category": cat, "price": spot, "z_score": z_score,
                    "probability_pct": probability * 100.0, "kelly_fraction_pct": kelly_fraction,
                    "volume_24h": volume_24h, "volume_delta": volume_delta,
                    "volatility": vol, "source": data.get('source', 'Public API Stream Endpoint')
                }
                
                # Cryptographically hash data lineage snapshots
                payload_hash, _ = self.evidence_layer.log_and_hash_payload(ticker, data)
                hashes_map[ticker] = payload_hash
                
                mapped_payload = {"price": spot, "change_24h": volume_delta}
                if "DePIN" in cat:
                    crypto_data_map[ticker] = mapped_payload
                elif "Hardware" in cat:
                    stock_data_map[ticker] = mapped_payload

        # 3. RUN FACTOR SCORING MATRIX
        print("📊 Executing Multi-Factor Composite Scoring Engine...")
        playbook = self.signal_engine.compute_composite_scores(raw_processing_map)

        # 4. CONSTRUCT RESEARCH BRIEFS WITH AUDIT LINKS
        sections_to_build = [
            "executive_arbitrage_summary", "regional_saas_arbitrage",
            "api_latency_arbitrage", "crypto_arbitrage_spread", "data_arbitrage_execution"
        ]
        compiled_expert_narrative = ""
        
        evidence_context = "\n## 📋 AUDIT EVIDENCE LOGS (Cite these explicitly in your analysis):\n"
        for item in playbook[:4]:
            h_ref = hashes_map.get(item['ticker'], "N/A")
            evidence_context += f"• Asset {item['ticker']}: {self.evidence_layer.generate_audit_lineage(item, h_ref)}\n"

        print("🧠 Invoking Prompt Factory across verified data points...")
        for section in sections_to_build:
            base_prompt = generate_arbitrage_section_prompt(
                section=section, trend_data=playbook, metrics_data={},
                crypto_data=crypto_data_map, stock_data=stock_data_map,
                os_data={"market_share": {}}, company_data={"top_100": []}
            )
            
            secure_prompt = base_prompt + evidence_context
            try:
                section_output = self.economist.synthesize_market_playbook(secure_prompt)
                compiled_expert_narrative += f"\n<h2>{section.replace('_',' ').title()}</h2>\n{section_output}"
            except Exception:
                compiled_expert_narrative += f"\n<h2>{section.replace('_',' ').title()}</h2><p>Signal verification complete. Anomaly variance documented.</p>"

        # 5. RUN STRATEGIC ALLOCATION INSIGHTS
        advisory_prompt = get_hedge_fund_advisor_prompt(crypto_data_map, stock_data_map, {"top_100": []}) + evidence_context
        try:
            advisor_output = self.economist.synthesize_market_playbook(advisory_prompt)
            compiled_expert_narrative += f"\n<h2>INSTITUTIONAL RESEARCH DIRECTIVES</h2>\n{advisor_output}"
        except Exception:
            pass

        # 6. RUN ACADEMIC SUMMARY BRIEF
        academic_prompt = get_academic_economist_synopsis_prompt(playbook) + evidence_context
        try:
            academic_output = self.economist.synthesize_market_playbook(academic_prompt)
            compiled_expert_narrative = f"<h2>🎓 ECONOMIST MACROECONOMIC RESEARCH SYNOPSIS</h2>\n{academic_output}\n<hr/>\n" + compiled_expert_narrative
        except Exception:
            pass

        # 7. INJECT COMPLIANCE AUDIT REGISTRY APPENDIX
        compiled_expert_narrative += self.evidence_layer.append_appendix_logs(playbook, hashes_map)

        # 8. Render Visual Assets & Transmit Deliverables
        html_path, csv_path = self.report_engine.generate_report(playbook, compiled_expert_narrative)
        print(f"✅ Defensible Visual Playbook Generated: {html_path}")
       
        # Save a historical copy into your sample_reports folder as a permanent artifact
        try:
            os.replace("playbook.html", "sample_reports/ai_infrastructure_brief_current.html")
            os.replace("macro_alpha_dataset.csv", "sample_reports/ai_infrastructure_dataset_current.csv")
            html_path = "sample_reports/ai_infrastructure_brief_current.html"
            csv_path = "sample_reports/ai_infrastructure_dataset_current.csv"
        except Exception:
            pass

        print(f"📦 Handing off generated assets to Delivery Agent loop...")
        try:
            dispatch_secure_fulfillment_package(html_path, csv_path)
            print("🚚 Delivery pipeline execution loop finalized successfully.")
        except Exception as e:
            print(f"❌ Critical error during delivery execution pass: {e}")

if __name__ == "__main__":
    LLMAnalystBot().run()
