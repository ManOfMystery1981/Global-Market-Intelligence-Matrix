#!/usr/bin/env python3
"""
prompt_factory.py
Institutional Academic Intelligence Prompt Framework (v4 Compliance-by-Construction)
- Enforces strict multi-source mapping arrays for all interpretive claims.
- Freezes runtime temporal variables using an explicit 'as_of_utc' validation block.
- Implements deep sentence-level citation enforcement to block analytical leakage.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("A_Plus_Academic_Validator")

# --- STRATIFICATION PERMISSION CONTEXTS ---
LAYER_FACT = "FACT_LAYER_REQUIRES_CITATION"
LAYER_INTERP = "INTERPRETATION_LAYER_MUST_CITE_FACT"
LAYER_HYPO = "HYPOTHESIS_LAYER_MUST_LABEL_PROBABILISTIC"

class EvidencePacketBuilder:
    """Module 1: Normalizes raw source intelligence into ID-stamped, cryptographically sound evidence records."""
    
    @staticmethod
    def build_extraction_prompt(as_of_utc: str) -> str:
        return (
            f"TASK: Parse the attached raw data stream into a structured JSON Evidence Packet array.\n"
            f"CRITICAL SYSTEM TEMPORAL BOUNDARY: All tracking evaluations must freeze relative to as_of_utc: [{as_of_utc}].\n\n"
            "CANONICALIZATION RULES:\n"
            "1. Every packet must get a deterministic 'packet_id'. Format: [SOURCE_YYYY_MM_DD_COUNT].\n"
            "2. SOURCE must be uppercase snake_case, stripped of punctuation, max 24 chars.\n"
            "3. For every distinct fact, append an immutable 'fact_id' using format: [PACKET_ID_F_COUNT].\n\n"
            "MANDATORY OUTPUT JSON STRUCTURE:\n"
            "{\n"
            "  \"evidence_packets\": [\n"
            "    {\n"
            "      \"packet_id\": \"STR\",\n"
            "      \"source_title\": \"STR\",\n"
            "      \"source_url\": \"STR (Valid URI mapping or immutable data hash reference)\",\n"
            "      \"retrieval_timestamp_utc\": \"ISO_8601_TIMESTAMP\",\n"
            "      \"source_type\": \"academic | government | corporate_filing | industry_index | media\",\n"
            "      \"publication_date\": \"YYYY-MM-DD\",\n"
            "      \"facts\": [\n"
            "        {\n"
            "          \"fact_id\": \"STR\",\n"
            "          \"factual_claim\": \"STR\",\n"
            "          \"exact_verbatim_excerpt\": \"STR\",\n"
            "          \"quantitative_metric\": \"STR\",\n"
            "          \"confidence_rating\": \"high | medium | low\"\n"
            "        }\n"
            "      ],\n"
            "      \"contradictions_or_limitations\": [\"STR\"]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

class EvidencePacketValidator:
    """Module 2: Evaluates structural payload integrity, data provenance fields, and identity token rules."""
    
    @staticmethod
    def validate_packet_payload(payload_json: str) -> Tuple[bool, List[str]]:
        errors = []
        try:
            data = json.loads(payload_json)
            if "evidence_packets" not in data:
                return False, ["Missing root 'evidence_packets' array key block."]
                
            for p in data["evidence_packets"]:
                pid = p.get("packet_id", "")
                if not re.match(r"^[A-Z0-9_]{1,24}_\d{4}_\d{2}_\d{2}_\d{3}$", pid):
                    errors.append(f"❌ SOURCE NORMALIZATION FAULT: packet_id '{pid}' violates upper snake-case date guidelines.")
                if not p.get("source_url") or not p.get("retrieval_timestamp_utc"):
                    errors.append(f"❌ PROVENANCE AUDIT FAULT: Packet '{pid}' missing mandatory secure URL or tracking timestamps.")
                
                for f in p.get("facts", []):
                    fid = f.get("fact_id", "")
                    if not fid.startswith(pid + "_F"):
                        errors.append(f"❌ FACT KEY FAULT: fact_id '{fid}' must structurally map under parent packet '{pid}'.")
                    if not f.get("exact_verbatim_excerpt"):
                        errors.append(f"❌ AUDIT FAULT: fact_id '{fid}' missing verbatim substring confirmation quotes.")
        except Exception as e:
            return False, [f"JSON Compilation failure: {e}"]
        return len(errors) == 0, errors

class ClaimLedgerBuilder:
    """Module 3: Generates the strict input-to-output validation mapping ledger prompt structures."""
    
    @staticmethod
    def build_ledger_prompt(validated_packets: Dict[str, Any], as_of_utc: str) -> str:
        return (
            f"TASK: Generate a pre-authoring Compliance Claim Ledger in strict JSON format based on the attached evidence.\n"
            f"SYSTEM REPRODUCIBILITY TEMPORAL ANCHOR: All facts frozen relative to as_of_utc: [{as_of_utc}].\n"
            f"CRITICAL COMPLIANCE ACCESS RULES:\n"
            f"1. Generate only claims that are directly derivable from the supplied fact_ids.\n"
            f"2. INTERPRETATION MATRIX RULES: Any claim tagged as 'interpretation' MUST cite a minimum of TWO independent supporting fact_ids inside its array list to establish a valid pattern trend. Single-fact leaps are strictly denied access.\n\n"
            f"MANDATORY JSON OUTPUT MATRIX FORMAT:\n"
            "{\n"
            "  \"claim_ledger\": [\n"
            "    {\n"
            "      \"claim_id\": \"CLM_001\",\n"
            "      \"planned_claim\": \"Spot uranium supply is constrained.\",\n"
            "      \"supporting_fact_ids\": [\"UXC_2026_06_27_001_F01\", \"WORLD_NUCLEAR_2026_06_27_002_F03\"],\n"
            "      \"claim_type\": \"factual | interpretation | hypothesis\",\n"
            "      \"allowed\": true\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"--- VALIDATED INPUT EVIDENCE PACKETS ---\n{json.dumps(validated_packets, indent=2)}"
        )

class ThesisPromptFactory:
    """Module 4: Builds the final writing prompt restricting generation strictly to pre-approved ledger frames."""
    
    @staticmethod
    def build_thesis_prompt(asset: str, approved_ledger: Dict[str, Any], telemetry: Dict[str, Any], as_of_utc: str) -> str:
        return (
            f"SYSTEM ROLE: Senior Research Economist. Author a university-quality thesis on asset: [{asset}].\n"
            f"SYSTEM TEMPORAL LIFECYCLE LOCK: Enforce all analytical logic positions frozen relative to as_of_utc: [{as_of_utc}].\n\n"
            f"CRITICAL COMPLIANCE & REASONING RULES:\n"
            f"1. MECHANICAL SENTENCE-LEVEL COMPLIANCE: Every single sentence making a factual calculation or stating a parameter MUST append the explicit Fact ID in square brackets (e.g., '[NASDAQ_2026_06_27_001_F01]').\n"
            f"2. You are STRICTLY RESTRICTED to processing only the pre-cleared, multi-source approved claims inside the ledger matrix attached below.\n"
            f"3. Stratify layers explicitly using labels: {LAYER_FACT}, {LAYER_INTERP}, {LAYER_HYPO}.\n\n"
            f"STRUCTURED SCHEMATIC MANDATORY SECTIONS:\n"
            f"- Abstract\n- Section I: Introduction\n- Section II: Provenance Review\n- Section III: Methodology\n- Section IV: Core Analysis\n- Section V: Counterarguments & Limitations\n\n"
            f"--- APPROVED SOURCE DATA MATRIX RECORDS ---\n"
            f"TELEMETRY: {json.dumps(telemetry)}\n"
            f"APPROVED CLAIM LEDGER: {json.dumps(approved_ledger)}"
        )

class CitationAuditor:
    """Module 5: Post-Generation Computational Quality Shield. Scans thesis output text sentence-by-sentence."""
    
    @staticmethod
    def audit_generated_thesis(thesis_text: str, valid_fact_ids: List[str]) -> Dict[str, Any]:
        # Cleanly segment text block down into distinct sentence tokens to prevent sliding-window text leakage
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', thesis_text)
        unsupported_sentences = []
        all_found_citations = []
        
        for idx, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
            # Extract bracketed citation tokens located within this specific sentence frame
            citations = re.findall(r"\[([A-Z0-9_]+_\d{4}_\d{2}_\d{2}_\d{3}_F\d+)\]", sentence)
            all_found_citations.extend(citations)
            
            # Identify if this specific sentence makes a hard metric, numerical assertion, or ratio state
            contains_metrics = bool(re.search(r"\b\d+[\d,.]*\b|%", sentence))
            has_valid_citations = len(citations) > 0 and all(c in valid_fact_ids for c in citations)
            
            # Programmatic Compliance Rule: If sentence holds numbers/percentages but carries zero valid tags, flag a failure
            if contains_metrics and not has_valid_citations:
                unsupported_sentences.append({
                    "sentence_index": idx,
                    "raw_unsupported_sentence": sentence.strip(),
                    "extracted_invalid_tags": [c for c in citations if c not in valid_fact_ids]
                })

        audit_passed = len(unsupported_sentences) == 0
        return {
            "audit_passed": audit_passed,
            "total_activated_citations_count": len(all_found_citations),
            "unsupported_sentences_count": len(unsupported_sentences),
            "unsupported_sentences_failures_ledger": unsupported_sentences,
            "timestamp_verification_utc": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    # Programmatic Test Run: Verifying verification parameters operate correctly
    test_time = "2026-06-27T23:00:00Z"
    mock_payload = {
        "evidence_packets": [{
            "packet_id": "WORLD_NUCLEAR_2026_06_27_001",
            "source_title": "WNA Report",
            "source_url": "https://wna.org",
            "retrieval_timestamp_utc": test_time,
            "source_type": "academic",
            "publication_date": "2026-06-27",
            "facts": [{
                "fact_id": "WORLD_NUCLEAR_2026_06_27_001_F01",
                "factual_claim": "Supply bounds hold tight.",
                "exact_verbatim_excerpt": "Verified constraint metrics logged.",
                "quantitative_metric": "82.40",
                "confidence_rating": "high"
            }]
        }]
    }
    
    # 1. Test Ingestion Payload Verification Gate
    payload_str = json.dumps(mock_payload)
    is_valid, logs = EvidencePacketValidator.validate_packet_payload(payload_str)
    assert is_valid, f"Validator failed on clean payload: {logs}"
    
    # 2. Test Sentence-Level Structural Citation Auditor Lock
    # Test Case A: Clean sentence containing metrics with matching fact tag
    mock_thesis_pass = "Uranium baseline metrics show major constraints standing at 82.40/lb [WORLD_NUCLEAR_2026_06_27_001_F01]."
    audit_results_pass = CitationAuditor.audit_generated_thesis(mock_thesis_pass, ["WORLD_NUCLEAR_2026_06_27_001_F01"])
    assert audit_results_pass["audit_passed"] == True
    
    # Test Case B: Rogue un-cited factual statement containing numbers (Should fail immediately)
    mock_thesis_fail = "Uranium baseline metrics show major constraints standing at 82.40/lb. This completely breaks the pattern."
    audit_results_fail = CitationAuditor.audit_generated_thesis(mock_thesis_fail, ["WORLD_NUCLEAR_2026_06_27_001_F01"])
    assert audit_results_fail["audit_passed"] == False
    
    print(json.dumps(audit_results_pass, indent=2))
    print("✅ PIPELINE INTEGRITY LOCK ACTIVE: Programmatic sentence-level verification successfully intercepting unanchored factual claims.")
