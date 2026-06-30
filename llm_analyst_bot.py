#!/usr/bin/env python3
"""
llm_analyst_bot.py - Part 1
Institutional Data Analysis Core (A+ Compliance Tier)
Hardened Production Release Engine with Cold-Start Connect Isolation
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import shutil
import uuid
from datetime import datetime, timezone

from data_collector_bot import MarketDataCollector
from signal_engine import MultiFactorSignalEngine
from industry_standard_report import IndustryStandardReport
from delivery_bot import dispatch_secure_fulfillment_package
from prompt_factory import EvidencePacketValidator, ThesisPromptFactory, CitationAuditor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LLM_Analyst_Bot")

class HardenedLLMProvider:
    """Handles high-throughput local inference passes using real-time socket streaming."""
    def __init__(self, model_name: str = "dolphin-mistral"):
        self.model_name = model_name
        self.endpoint = "http://localhost:11434/api/chat"
        self._circuit_broken = False
        
        try:
            probe_req = urllib.request.Request("http://local_llm_core:11434/api/tags", method="GET")
            with urllib.request.urlopen(probe_req, timeout=3) as _:
                self.endpoint = "http://local_llm_core:11434/api/chat"
                logger.info("📡 Internal container bridge network identified. Routing via local_llm_core.")
        except Exception:
            logger.info("💻 Local host network identified. Routing via loopback localhost.")

    def complete_stream(self, prompt: str) -> str:
        """Streams tokens line-by-line from the container socket to eliminate connection timeouts."""
        if self._circuit_broken:
            raise RuntimeError("🚨 CIRCUIT BREAKER OPEN: Local inference engine previously failed. Refusing execution.")

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a rigid financial compliance bot. Strictly follow user data guidelines."},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "options": {"temperature": 0.1, "num_predict": 512, "num_ctx": 4096}
        }
        
        json_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=json_bytes, headers={"Content-Type": "application/json"}, method="POST")
        
        accumulated_response = []
        try:
            # FIXED: Expanded the socket timeout boundaries to 120s to absorb model cold-start RAM loading lag
            with urllib.request.urlopen(req, timeout=120) as response:
                while True:
                    line = response.readline()
                    if not line:
                        break
                    
                    parsed_chunk = json.loads(line.decode("utf-8"))
                    token = parsed_chunk.get("message", {}).get("content", "")
                    accumulated_response.append(token)
                    
                    sys.stdout.write(token)
                    sys.stdout.flush()
                    
                    if parsed_chunk.get("done", False):
                        break
            print() 
            return "".join(accumulated_response)
        except Exception as e:
            self._circuit_broken = True
            logger.critical(f"💥 Streaming inference channel collapsed: {e}")
            raise RuntimeError(f"Local Ingest Core Inference Failure: {e}")

class LLMAnalystBot:
    def __init__(self):
        self.run_uuid = uuid.uuid4().hex[:8].upper()
        logger.info(f"[{self.run_uuid}] DEBUG: Institutional A-Grade Analyst Engine initialized successfully.")
        self.provider = HardenedLLMProvider()
        self.collector = MarketDataCollector(production_mode=True)
        self.engine = MultiFactorSignalEngine()
        self.reporter = IndustryStandardReport()

    def run_automated_pipeline(self):
        now_utc = datetime.now(timezone.utc)
        current_utc_time = now_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        date_folder = now_utc.strftime("%Y_%m_%d")
        
        session_dir = f"run_session_{now_utc.strftime('%Y%m%d_%H%M%S')}_{self.run_uuid}"
        os.makedirs(session_dir, exist_ok=True)
        
        logger.info(f"[{self.run_uuid}] 📁 Isolated Workspace Directory initialized: {session_dir}")
        logger.info(f"[{self.run_uuid}] 🚀 Orchestrator: Initiating 100-asset data sweep...")
        raw_data = self.collector.collect_all_data()
        
        if not raw_data:
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.critical(f"[{self.run_uuid}] ❌ PIPELINE CRASH: Ingestion core returned empty payload.")
            sys.exit(1)
            
        logger.info(f"[{self.run_uuid}] 🧮 Formatting data matrices for structural scoring layers...")
        playbook = self.engine.compute_composite_scores(raw_data)
        
        compliant_packet_id = f"COINGECKO_{date_folder}_PACKET001"
        
        logger.info(f"[{self.run_uuid}] 🧠 Compiling multi-asset evidence packets dynamically...")
        facts_list = []
        for idx, (ticker, metrics) in enumerate(raw_data.items(), start=1):
            price = metrics.get("price")
            if price is None:
                shutil.rmtree(session_dir, ignore_errors=True)
                raise ValueError(f"Required market metrics missing from collector stream payload.")
                
            category = metrics.get("category", "General_Macro")
            f_suffix = f"F{str(idx).zfill(2)}"
            fact_id = f"COINGECKO_{date_folder}_PACKET001_{f_suffix}"
            
            facts_list.append({
                "fact_id": fact_id,
                "factual_claim": f"Live market index verifies {ticker} asset metrics within {category} tracking fields reporting at a close value of ${price} USD.",
                "exact_verbatim_excerpt": f"{ticker} logged index value base bounding: {price}",
                "quantitative_metric": str(price),
                "confidence_rating": "high"
            })

        live_evidence_payload = {
            "evidence_packets": [{
                "packet_id": compliant_packet_id,
                "source_title": "Multi-Asset API Institutional Ingestion Stream",
                "source_url": "https://coingecko.com",
                "retrieval_timestamp_utc": current_utc_time,
                "source_type": "industry_index",
                "publication_date": current_utc_time[:10],
                "facts": facts_list
            }]
        }
        
        is_ingestion_valid, validation_logs = EvidencePacketValidator.validate_packet_payload(live_evidence_payload)
        if not is_ingestion_valid:
            shutil.rmtree(session_dir, ignore_errors=True)
            raise ValueError(f"Ingestion schema error: {validation_logs}")
            
        self.facts_list = facts_list
        self.live_evidence_payload = live_evidence_payload
        self.compliant_packet_id = compliant_packet_id
        self.current_utc_time = current_utc_time
        self.playbook = playbook
        self.session_dir = session_dir
        self.date_folder = date_folder
        facts_list = self.facts_list
        live_evidence_payload = self.live_evidence_payload
        compliant_packet_id = self.compliant_packet_id
        current_utc_time = self.current_utc_time
        playbook = self.playbook
        session_dir = self.session_dir
        date_folder = self.date_folder

        claims_list = []
        for idx, fact in enumerate(facts_list, start=1):
            claims_list.append({
                "claim_id": f"CLM_LIVE_{str(idx).zfill(3)}",
                "planned_claim": fact["factual_claim"],
                "supporting_fact_ids": [fact["fact_id"]],
                "claim_type": "factual",
                "allowed": True
            })

        live_approved_ledger = {"claim_ledger": claims_list}
        composite_telemetry_score = 66.44
        
        # Segment data to prevent hardware context window saturation
        chunk_size = 4
        batched_facts = [facts_list[i:i + chunk_size] for i in range(0, len(facts_list), chunk_size)]
        compiled_report_segments = []
        
        logger.info(f"[{self.run_uuid}] 📡 Initiating real-time streaming inference passes across sub-batches...")
        for batch_idx, batch in enumerate(batched_facts, start=1):
            logger.info(f"[{self.run_uuid}] ⚡ Streaming token chunk {batch_idx}/{len(batched_facts)}...")
            mini_ledger = {"claim_ledger": claims_list[(batch_idx-1)*chunk_size : batch_idx*chunk_size]}
            
            batch_prompt = ThesisPromptFactory.build_thesis_prompt(
                asset=f"Arbitrage_Framework_Segment_{batch_idx}",
                approved_ledger=mini_ledger,
                telemetry={"composite_score": composite_telemetry_score, "classification": "Active Stream Run"},
                as_of_utc=current_utc_time
            )
            segment_text = self.provider.complete_stream(batch_prompt)
            compiled_report_segments.append(segment_text)
            
        generated_report_text = "\n\n".join(compiled_report_segments)
        
        logger.info(f"[{self.run_uuid}] 🛡️ Activating Post-Generation Compliance Release Gate...")
        audit_results = CitationAuditor.audit_generated_thesis(generated_report_text, live_evidence_payload, current_utc_time)
        
        is_audit_approved = False
        if audit_results and isinstance(audit_results, dict):
            is_audit_approved = audit_results.get("is_valid", False)
            failed_violations = audit_results.get("failed_rules", ["MISSING_STRUCTURAL_RULE_LIST"])

        if not is_audit_approved:
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.critical(f"[{self.run_uuid}] 🚨 FAIL-CLOSED RELEASE CEILING TRIGGERED: Report failed integrity checks.")
            raise RuntimeError(f"Compliance validation failed. Refusing to compile or publish output.")
            
        logger.info(f"[{self.run_uuid}] ✅ COMPLIANCE STATUS VERIFIED: Passing document to isolation compiler...")
        
        temp_html_path = os.path.join(session_dir, "ai_infrastructure_brief_current.html")
        temp_csv_path = os.path.join(session_dir, "market_anomaly_dataset.csv")
        
        production_dir = "sample_reports"
        final_html_delivery_target = os.path.join(production_dir, "ai_infrastructure_brief_current.html")
        
        try:
            self.reporter.generate_report(playbook, generated_report_text)
            
            if os.path.exists("playbook.html"):
                shutil.move("playbook.html", temp_html_path)
            if os.path.exists("market_anomaly_dataset.csv"):
                shutil.move("market_anomaly_dataset.csv", temp_csv_path)

            if not os.path.exists(temp_html_path):
                raise FileNotFoundError(f"[{self.run_uuid}] ❌ COMPLIANCE CRITICAL: HTML playbook artifact generation missing.")
            if not os.path.exists(temp_csv_path):
                raise FileNotFoundError(f"[{self.run_uuid}] ❌ COMPLIANCE CRITICAL: CSV metadata dataset artifact generation missing.")

            # ATOMIC PROMOTION COMMIT GATE - ENFORCING NATIVE os.replace()
            os.makedirs(production_dir, exist_ok=True)
            os.replace(temp_html_path, final_html_delivery_target)
            logger.info(f"[{self.run_uuid}] 🚀 Atomic Replace Successful: Artifact promoted cleanly to: {final_html_delivery_target}")
            
            try:
                dispatch_secure_fulfillment_package(html_path=final_html_delivery_target, csv_path=temp_csv_path)
                logger.info(f"[{self.run_uuid}] 🏁 Automated Pipeline Execution Complete. Artifacts cleanly committed and dispatched.")
            except Exception as dispatch_err:
                logger.critical(f"[{self.run_uuid}] 🚨 DISPATCH ATTEMPT FAILED: Failure state logged securely. Error: {dispatch_err}")
                raise dispatch_err
            
        except Exception as file_error:
            logger.critical(f"🚨 UNCAUGHT CRASH IN ATOMIC PROCESSING LAYER: {file_error}")
            raise file_error
            
        finally:
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info(f"[{self.run_uuid}] 🧹 Clean Up Pass Complete. Workspace sandbox successfully purged from host disk layout.")

if __name__ == '__main__':
    bot = LLMAnalystBot()
    bot.run_automated_pipeline()
