#!/usr/bin/env python3
import json

def generate_arbitrage_section_prompt(section, trend_data, metrics_data, crypto_data, stock_data, os_data, company_data, market_data=None):
    quality_rules = """
• DO NOT include introductory filler like "Here is your report" — write prose directly.
• DO NOT include code blocks, raw markdown formatting arrows, or JSON text.
• WRITE in an authoritative, clinical tone, exactly like a Wall Street quantitative analyst.
• CITATION REQUIREMENT: You must explicitly cite the raw values and timestamps provided in the context."""

    if section == "executive_arbitrage_summary":
        return f"Context: Analyze the following anomaly data layout: {str(trend_data[:5])}. Task: Write the Executive Intelligence Thesis and Core Synthesis. Target: 300 words. Rules: {quality_rules}"
    elif section == "regional_saas_arbitrage":
        return f"Context: Evaluate regional compute differences. Task: Write the Infrastructure Constraint Analysis. Target: 300 words. Rules: {quality_rules}"
    elif section == "api_latency_arbitrage":
        return f"Context: Evaluate network speeds. Task: Write the Semiconductor & API Supply Chain Latency analysis. Target: 300 words. Rules: {quality_rules}"
    elif section == "crypto_arbitrage_spread":
        return f"Context: Alternative flow logs: {str(crypto_data)}. Task: Write the DePIN and High-Compute Liquid Token Flow Analysis. Target: 300 words. Rules: {quality_rules}"
    else:
        return f"Context: Process execution constraints. Task: Write the Algorithmic Strategy & Risk Mitigation section. Target: 300 words. Rules: {quality_rules}"

def get_hedge_fund_advisor_prompt(crypto_data, stock_data, company_data):
    return """
Task: Write the Institutional Capital Allocation Directives page. Target: 400 words. 
Instructions: Outline specific capital thresholds, rebalancing orders, and risk limits based on the statistical indicators. Avoid general trading advice or filler.
"""

def get_academic_economist_synopsis_prompt(playbook_data):
    return f"""
Task: Write a rigorous Academic Macroeconomic Research Paper Synopsis analyzing these cross-asset metrics: {str(playbook_data[:8])}.
Target: 600 words.
Structure Requirements (You must use these headings):
<h3>I. MACROECONOMIC DIVERGENCE FOUNDATIONS</h3>
<h3>II. THEOREMS FOR WEALTH MULTIPLICATION & PREDICTIVE ODDS</h3>
<h3>III. INFRASTRUCTURAL PITFALLS, THESIS INVALIDATION & RISK INSULATION</h3>
"""

def format_crypto_arbitrage(d): return "Crypto metrics operational."
def format_stock_arbitrage(d): return "Equity metrics operational."
def format_company_arbitrage(d): return "Corporate metrics operational."
def format_os_data(d): return "Infrastructural loops operational."
