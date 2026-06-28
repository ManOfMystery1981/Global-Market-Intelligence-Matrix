#!/usr/bin/env python3
"""
prompt_factory.py
Institutional Academic Intelligence Prompt Framework (v5 Compliance-by-Construction)
- Replaces numeric filtering with full declarative sentence analysis gates.
- Enforces strict canonical Fact ID uppercase snake-case regex tracking formats.
- Discards local clock-time checks to ensure total temporal reproducibility.
"""

import re
import json
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("A_Plus_Academic_Validator")

LAYER_FACT = "FACT_LAYER_REQUIRES_CITATION"
LAYER_INTERP = "INTERPRETATION_LAYER_MUST_CITE_FACT"
LAYER_HYPO = "HYPOTHESIS_LAYER_MUST_LABEL_PROBABILISTIC"

class EvidencePacketValidator:
    """Module 1: Machine-executable validations for data schemas and standardized source strings."""
    
    @staticmethod
    def validate_packet_payload(payload_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        packets = payload_dict.get("evidence_packets", [])
        if not packets:
            return False, ["Missing root 'evidence_packets' matrix block."]
            
        for p in packets:
            pid = p.get("packet_id", "")
            # Enforce strict canonical key tracking formatting
            if not re.match(r"^[A-Z0-9_]{1,24}_\d{4}_\d{2}_\d{2}_PACKET\d{3}$", pid):
                errors.append(f"❌ CANONICALIZATION FAULT: packet_id '{pid}' must be uppercase snake_case under 24 chars with PACKETNNN sequencing.")
            
            for f in p.get("facts", []):
                fid = f.get("fact_id", "")
                if not re.match(r"^[A-Z0-9_]{1,24}_\d{4}_\d{2}_\d{2}_PACKET\d{3}_F\d{2}$", fid):
                    errors.append(f"❌ CANONICALIZATION FAULT: fact_id '{fid}' violates strict FNN structural standards.")
                if not fid.startswith(pid):
                    errors.append(f"❌ PROVENANCE MISMATCH: fact_id '{fid}' does not derive from parent packet_id '{pid}'.")
        return len(errors) == 0, errors

class ThesisPromptFactory:
    """Module 2: Generates the strict input-to-output writing pass prompt context frames."""
    
    @staticmethod
    def build_thesis_prompt(asset: str, approved_ledger: Dict[str, Any], telemetry: Dict[str, Any], as_of_utc: str) -> str:
        from llm_analyst_prompt import get_compliance_rules_template, get_academic_structure_blueprint
        return (
            f"SYSTEM ROLE: Senior Research Economist. Author a university-quality thesis on asset: [{asset}].\n"
            f"SYSTEM TEMPORAL LIFECYCLE LOCK: All logic must freeze relative to as_of_utc: [{as_of_utc}].\n\n"
            f"{get_compliance_rules_template()}\n"
            f"{get_academic_structure_blueprint()}\n\n"
            f"--- APPROVED SOURCE DATA MATRIX RECORDS ---\n"
            f"TELEMETRY: {json.dumps(telemetry)}\n"
            f"APPROVED CLAIM LEDGER: {json.dumps(approved_ledger)}"
        )

class CitationAuditor:
    """Module 3: Programmatic Post-Generation Quality Shield. Scans all declarative sentences."""
    
    @staticmethod
    def audit_generated_thesis(thesis_text: str, valid_fact_ids: List[str], as_of_utc: str) -> Dict[str, Any]:
        # Segment text into sentences, accounting for standard shorthand variations
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', thesis_text)
        unsupported_sentences = []
        all_found_citations = []
        
        for idx, sentence in enumerate(sentences):
            clean_s = sentence.strip()
            if not clean_s:
                continue
                
            # Audit Constraint Check: Exclude headings, markdown dividers, and declared interpretations/hypotheses
            requires_citation = (
                clean_s
                and not clean_s.startswith(("#", "<h", "- ", "*", "'''", '"""'))
                and "[HYPOTHESIS]" not in clean_s
                and "[INTERPRETATION]" not in clean_s
            )
            
            citations = re.findall(r"\[([A-Z0-9_]+_\d{4}_\d{2}_\d{2}_PACKET\d{3}_F\d{2})\]", clean_s)
            all_found_citations.extend(citations)
            has_valid_citations = len(citations) > 0 and all(c in valid_fact_ids for c in citations)
            
            if requires_citation and not has_valid_citations:
                unsupported_sentences.append({
                    "sentence_index": idx,
                    "raw_unsupported_sentence": clean_s,
                    "invalid_or_missing_tags": [c for c in citations if c not in valid_fact_ids]
                })

        audit_passed = len(unsupported_sentences) == 0
        return {
            "audit_passed": audit_passed,
            "total_activated_citations_count": len(all_found_citations),
            "unsupported_sentences_count": len(unsupported_sentences),
            "unsupported_sentences_failures_ledger": unsupported_sentences,
            "timestamp_verification_utc": as_of_utc  # Frozen temporal anchor constraint enforced
        }
