#!/usr/bin/env python3
"""
llm_analyst_prompt.py
Institutional Quality Matrix: Enforces strict source-locked generation contracts.
Removes all freeform speculative writing capabilities from active agent pipelines.
"""

def get_compliance_rules_template() -> str:
    """Returns the non-negotiable compilation directives for LLM consumers."""
    return """
CRITICAL COMPLIANCE ACCESS RULES:
1. USE ONLY FACTS FROM THE ATTACHED APPROVED_CLAIM_LEDGER. You are strictly restricted to processing pre-authorized parameters.
2. EVERY SINGLE FACTUAL OR DECLARATIVE SENTENCE MUST INCLUDE AT LEAST ONE VALID FACT ID (e.g., [SOURCEKEY_YYYY_MM_DD_PACKETNNN_FNN]).
3. DO NOT introduce outside statistics, historical dates, percentages, corporate entities, prices, or unanchored causal claims.
4. If the ledger is insufficient to construct an academic argument for a section, you MUST write exactly: INSUFFICIENT_LEDGER_SUPPORT.
5. All interpretive or forward-looking sentences must be explicitly prefixed with either [INTERPRETATION] or [HYPOTHESIS] tags.
"""

def get_academic_structure_blueprint() -> str:
    """Returns the mandatory skeletal structure required for publication-grade layout."""
    return """
MANDATORY REPORT FORMATTING SCHEMA:
- Abstract: Concise summary of thesis pillars and raw selection parameters.
- Section I: Introduction & Macro Formulation (Defines incentives and friction).
- Section II: Literature & Source Provenance Review (Analyzes source tiers and autoridad).
- Section III: Quantitative Methodology Framework (Defines z-score thresholds and defaults).
- Section IV: Core Analysis & Evidence Pillars (Every declarative line must hold valid Fact ID brackets).
- Section V: Counterarguments & Conflicting Signals (Highlights data friction explicitly).
"""
