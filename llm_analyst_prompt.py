import json
from datetime import datetime

def format_crypto_arbitrage(crypto_data):
    # Placeholder helper function to avoid NameError
    return f"Crypto Data Summary: {crypto_data}"

def format_stock_arbitrage(stock_data):
    # Placeholder helper function to avoid NameError
    return f"Stock Data Summary: {stock_data}"

def format_os_data(os_data):
    # Placeholder helper function to avoid NameError
    return f"OS Data Summary: {os_data}"

def format_company_arbitrage(company_data):
    # Placeholder helper function to avoid NameError
    return f"Company Data Summary: {company_data}"

def generate_arbitrage_section_prompt(section, trend_data, metrics_data, crypto_data, stock_data, os_data, company_data, market_data=None):
    """Generate prompts focused on data arbitrage spreads."""
    
    # Format data for arbitrage detection
    crypto_text = format_crypto_arbitrage(crypto_data)
    stock_text = format_stock_arbitrage(stock_data)
    os_text = format_os_data(os_data)
    company_text = format_company_arbitrage(company_data)
    
    if section == "executive_arbitrage_summary":
        return f"""
You are an elite Quantitative Data Arbitrage Analyst. Your sole objective is to scan web indexes, API endpoints, cross-border storefronts, and on-chain records to detect pricing spreads, latency discrepancies, and market inefficiencies.

## CRITICAL INSTRUCTIONS

**1. BAN EXPOSITORY TEXT:**
- Completely ignore high-level tech trends, general company revenue updates, news regarding executive changes, or generic product releases.
- **DO NOT** use phrases like "constantly pushing boundaries," "the tech industry is evolving," or "in today's digital landscape."

**2. ISOLATE THE "SPREAD":**
- Look exclusively for asymmetric, unmapped mismatches where an asset, software license, API credit, token bucket, or digital commodity is priced lower in Market A than Market B.

**3. EXTRACT METRICS:**
For every trend or insight discovered, you must extract:
- Target API or Product Asset Name
- Exact price in Market A vs Market B (and respective geographic regions or currencies)
- Real-time transaction/gas/slippage cost to execute the trade
- Estimated decay velocity (how fast the arbitrage opportunity closes)

**4. QUALITY GATE:**
If an entry cannot be broken down into a math-based execution strategy, discard it entirely.

## 📊 CURRENT MARKET DATA

{crypto_text}
{stock_text}
{os_text}
{company_text}

## 📝 OUTPUT FORMAT

Write an Executive Arbitrage Summary with these sections:

1. **The Market Imbalance** - Identify the precise structural or spatial flaw
2. **The Arbitrage Spreadsheet** - Show a markdown table outlining price differences, platform fees, and net profit spreads
3. **Execution Vector** - Describe the step-by-step technical script process required to capture the spread

**TONE:** Sharp, math-driven, authoritative. No filler words.

Begin your analysis now.
"""

    elif section == "regional_saas_arbitrage":
        return f"""
Act as a digital asset arbitrage specialized bot. Scan global currency fluctuations, regional B2B pricing schemes, and localized payment gateway web structures.

## 📊 CURRENT MARKET DATA

{crypto_text}
{stock_text}
{company_text}

## 📝 YOUR TASK

Output a data report identifying three specific enterprise software platforms or API infra providers where a significant regional price spread exists due to missing multi-currency indexation.

**OUTPUT FORMAT:**
```json
{{
  "software_asset": "[Name]",
  "highest_pricing_region": "[Region & Cost in USD]",
  "lowest_pricing_region": "[Region & Cost in USD]",
  "gross_arbitrage_delta": "[Percentage %]",
  "execution_bottleneck": "[Describe proxy barriers, localized payment verification methods, or automated checkout hurdles]"
}}
```
"""

    elif section == "api_latency_arbitrage":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in API latency arbitrage.

## 📊 CURRENT MARKET DATA

{crypto_text}
{stock_text}

## 📝 YOUR TASK

Identify milliseconds-level latency gaps between regional cloud data warehouses or token-metered model providers.

**OUTPUT FORMAT:**
```json
{{
  "api_provider": "[Name]",
  "region_a": "{{region}}: {{latency_ms}}ms, {{price_per_call}}",
  "region_b": "{{region}}: {{latency_ms}}ms, {{price_per_call}}",
  "latency_delta_ms": "[Difference in milliseconds]",
  "profit_per_call": "[Calculated profit per API call]",
  "arbitrage_opportunity": "[Describe how to exploit this gap]"
}}
```
"""

    elif section == "crypto_arbitrage_spread":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in crypto arbitrage.

## 📊 CRYPTO MARKET DATA

{crypto_text}

## 📝 YOUR TASK

Identify price spreads between exchanges or regions for major cryptocurrencies.

**OUTPUT FORMAT:**
```json
{{
  "asset": "[Name]",
  "exchange_a": "{{exchange}}: {{price}}",
  "exchange_b": "{{exchange}}: {{price}}",
  "spread_percentage": "[Calculated spread %]",
  "gas_fee": "[Transaction cost to execute]",
  "net_profit": "[Profit after fees]",
  "execution_time_window": "[How fast it closes]"
}}
```
"""

    elif section == "data_arbitrage_execution":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in execution strategies.

## 📊 CURRENT MARKET DATA

{crypto_text}
{stock_text}

## 📝 YOUR TASK

Provide a detailed execution strategy for capturing identified arbitrage spreads.

**OUTPUT FORMAT:**
```json
{{
  "asset": "[Name]",
  "execution_step_1": "[First step]",
  "execution_step_2": "[Second step]",
  "execution_step_3": "[Third step]",
  "automation_script": "[Python/Node.js script outline]",
  "estimated_profit_per_trade": "[Calculated profit]"
}}
```
"""
    else:
        return "Invalid section specified."
