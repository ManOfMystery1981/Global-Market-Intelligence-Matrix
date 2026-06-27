# llm_analyst_prompt.py - Professional Arbitrage Report Version with Clear Output Instructions
import json
from datetime import datetime

def generate_arbitrage_section_prompt(section, trend_data, metrics_data, crypto_data, stock_data, os_data, company_data, market_data=None):
    """Generate prompts focused on data arbitrage spreads."""
    
    # Format data for arbitrage detection
    crypto_text = format_crypto_arbitrage(crypto_data)
    stock_text = format_stock_arbitrage(stock_data)
    os_text = format_os_data(os_data)
    company_text = format_company_arbitrage(company_data)
    
    # Strict quality rules - these are instructions, NOT output
    quality_rules = """
## ⚠️ CRITICAL QUALITY RULES (These are instructions, DO NOT output these rules)

1. **DO NOT** repeat yourself. Each section must contain unique content.
2. **DO NOT** output code, JSON, or Markdown artifacts. Output only professional English prose.
3. **DO NOT** include phrases like "Here is" or "This section covers" — just write the content directly.
4. **USE** perfect American English spelling and grammar at all times.
5. **USE** round bullet points (•) for lists.
6. **WRITE** in a professional, data-driven tone like a Wall Street analyst.
7. **CITE** specific numbers and data points from the provided data.
"""

    # This is the OUTPUT format - what the LLM should actually produce
    output_format = """
## 📋 OUTPUT FORMAT (DO NOT output this heading, just follow it)

### EXECUTIVE SUMMARY
[Write 3-4 sentences summarizing the key arbitrage opportunities identified in the data.]

### MARKET IMBALANCE
[Describe the specific structural or spatial flaw that creates the arbitrage opportunity.]

### QUANTIFIED SPREADS
[Present the exact price differences, percentages, and profit potential.]

### EXECUTION STRATEGY
[Describe the step-by-step approach to capture the spread.]

### RISK ASSESSMENT
[Identify key risks and mitigation strategies.]
"""

    if section == "executive_arbitrage_summary":
        return f"""
You are a Senior Quantitative Data Arbitrage Analyst writing for a professional investment newsletter.

{quality_rules}

## 📊 CURRENT MARKET DATA TO USE

{crypto_text}
{stock_text}
{os_text}
{company_text}

## 📝 YOUR TASK

Write the **Executive Arbitrage Summary** section of a professional report. This should be about 300-400 words.

### WHAT TO OUTPUT (Do NOT output these headings as literal text)

1. **Opening Statement** - A strong, data-driven opening that captures the current arbitrage landscape.
2. **Key Opportunity Identification** - Name 2-3 specific arbitrage opportunities from the data.
3. **Quantified Impact** - Use exact numbers: "The SOL-USD spread offers a 4.3% opportunity with a 3-day execution window."
4. **Strategic Recommendation** - Clear, actionable advice.

### WHAT NOT TO OUTPUT

- No "Here is the executive summary" or "This section covers" type phrases.
- No code blocks or JSON.
- No Markdown artifacts like `text[[...]]`.
- No repetition.

### FORMAT

Write directly as prose paragraphs with clear, professional structure. Use round bullets (•) where appropriate.

BEGIN YOUR EXECUTIVE ARBITRAGE SUMMARY NOW:
"""

    elif section == "regional_saas_arbitrage":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in SaaS and digital product arbitrage.

{quality_rules}

## 📊 CURRENT MARKET DATA TO USE

{crypto_text}
{stock_text}
{company_text}

## 📝 YOUR TASK

Write the **Regional SaaS Arbitrage Analysis** section. This should be about 400-500 words.

### WHAT TO OUTPUT (Do NOT output these headings as literal text)

1. **Identify 3 platforms** with regional price discrepancies.
2. **For each platform**, provide:
   - Platform name
   - Region A: Price in USD
   - Region B: Price in USD
   - Arbitrage percentage
   - Execution bottleneck

### FORMAT FOR EACH PLATFORM

[Platform Name]
- Regional Price Discrepancy: Region A: $X vs Region B: $Y
- Arbitrage Opportunity: X%
- Execution Strategy: Clear step-by-step approach
- Risk Factors: Key risks

### WHAT NOT TO OUTPUT

- No "Here is the analysis" phrases.
- No code or JSON.
- No repetition.

BEGIN YOUR REGIONAL SAAS ARBITRAGE ANALYSIS NOW:
"""

    elif section == "api_latency_arbitrage":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in API latency arbitrage.

{quality_rules}

## 📊 CURRENT MARKET DATA TO USE

{crypto_text}
{stock_text}

## 📝 YOUR TASK

Write the **API Latency Arbitrage Analysis** section. This should be about 300-400 words.

### WHAT TO OUTPUT (Do NOT output these headings as literal text)

1. **Identify latency gaps** between regional cloud providers.
2. **For each gap**, provide:
   - API Provider name
   - Region A: Latency in ms, Price per call
   - Region B: Latency in ms, Price per call
   - Latency delta in ms
   - Profit potential per call
   - Arbitrage opportunity description

### WHAT NOT TO OUTPUT

- No "Here is the latency analysis" phrases.
- No code or JSON.
- No repetition.

BEGIN YOUR API LATENCY ARBITRAGE ANALYSIS NOW:
"""

    elif section == "crypto_arbitrage_spread":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in cryptocurrency arbitrage.

{quality_rules}

## 📊 CRYPTO MARKET DATA TO USE

{crypto_text}

## 📝 YOUR TASK

Write the **Crypto Arbitrage Spread Analysis** section. This should be about 300-400 words.

### WHAT TO OUTPUT (Do NOT output these headings as literal text)

1. **Identify price spreads** between exchanges for 2-3 cryptocurrencies.
2. **For each spread**, provide:
   - Cryptocurrency name
   - Exchange A: Price
   - Exchange B: Price
   - Spread percentage
   - Gas fee
   - Net profit per trade
   - Execution time window

### WHAT NOT TO OUTPUT

- No "Here is the crypto analysis" phrases.
- No code or JSON.
- No repetition.

BEGIN YOUR CRYPTO ARBITRAGE SPREAD ANALYSIS NOW:
"""

    elif section == "data_arbitrage_execution":
        return f"""
You are a Quantitative Data Arbitrage Analyst specializing in execution strategies.

{quality_rules}

## 📊 CURRENT MARKET DATA TO USE

{crypto_text}
{stock_text}

## 📝 YOUR TASK

Write the **Data Arbitrage Execution Strategy** section. This should be about 400-500 words.

### WHAT TO OUTPUT (Do NOT output these headings as literal text)

1. **Outlined Execution Process** - Step-by-step for the highest-value spread.
2. **Automation Framework** - How to automate the execution.
3. **Bottleneck Identification** - Where the strategy could fail.
4. **Risk Mitigation** - How to protect against slippage and latency.

### FORMAT

Use clear, professional prose with numbered steps where appropriate.

### WHAT NOT TO OUTPUT

- No "Here is the execution strategy" phrases.
- No code or JSON.
- No repetition.

BEGIN YOUR DATA ARBITRAGE EXECUTION STRATEGY NOW:
"""

    else:
        return f"""
You are a Senior Quantitative Data Arbitrage Analyst.

{quality_rules}

Write a professional analysis of the provided data. Focus on identifying and quantifying arbitrage opportunities. Use specific numbers from the data.

BEGIN YOUR ANALYSIS NOW:
"""


# --- FORMATTING FUNCTIONS FOR ARBITRAGE DATA ---

def format_crypto_arbitrage(crypto_data):
    """Format crypto data for arbitrage detection."""
    if not crypto_data:
        return "No crypto data available."
    
    lines = ["CRYPTO PRICE SPREADS:"]
    for coin, data in crypto_data.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"• {coin}: ${price:.2f} (24h: {change:+.1f}%)")
    
    return "\n".join(lines)


def format_stock_arbitrage(stock_data):
    """Format stock data for arbitrage detection."""
    if not stock_data:
        return "No stock data available."
    
    lines = ["TECH STOCK PERFORMANCE:"]
    for symbol, data in stock_data.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"• {symbol}: ${price:.2f} (24h: {change:+.1f}%)")
    
    return "\n".join(lines)


def format_company_arbitrage(company_data):
    """Format company data for arbitrage detection."""
    if not company_data:
        return "No company data available."
    
    top_100 = company_data.get('top_100', [])
    lines = ["TOP TECH COMPANIES:"]
    for c in top_100[:20]:
        rank = c.get('rank', 0)
        name = c.get('name', 'Unknown')
        rev = c.get('revenue', 0)
        mc = c.get('market_cap', 0)
        lines.append(f"• #{rank}. {name}: Revenue ${rev}B, Market Cap ${mc}T")
    
    return "\n".join(lines)


def format_os_data(os_data):
    """Format OS data."""
    if not os_data:
        return "No OS data available."
    
    lines = ["OPERATING SYSTEM MARKET SHARE:"]
    market_share = os_data.get('market_share', {})
    for os_name, data in market_share.items():
        share = data.get('market_share', 0)
        trend = data.get('trend', 'stable')
        lines.append(f"• {os_name}: {share}% ({trend})")
    
    return "\n".join(lines)


def format_top_100(companies):
    if not companies:
        return "No company data available."
    lines = []
    for c in companies[:50]:
        rank = c.get('rank', 0)
        name = c.get('name', 'Unknown')
        rev = c.get('revenue', 0)
        mc = c.get('market_cap', 0)
        ytd = c.get('ytd_change', 0)
        industry = c.get('industry', '')
        lines.append(f"{rank}. {name} — Revenue: ${rev}B, Market Cap: ${mc}T, YTD: {ytd}%, {industry}")
    return "\n".join(lines)


def format_top_10_categories(categories):
    if not categories:
        return "No category data available."
    lines = []
    for cat, items in categories.items():
        lines.append(f"{cat.replace('_', ' ').title()}:")
        for i, name in enumerate(items[:10], 1):
            lines.append(f"  {i}. {name}")
    return "\n".join(lines)


def format_innovations(innovations):
    if not innovations:
        return "No data available."
    lines = []
    for i in innovations:
        name = i.get('name', '')
        desc = i.get('description', '')
        year = i.get('year', '')
        impact = i.get('impact', '')
        lines.append(f"• {name} — {desc} ({year}) [Impact: {impact}]")
    return "\n".join(lines)


def format_processors(processors):
    if not processors:
        return "No data available."
    lines = []
    for p in processors:
        name = p.get('name', '')
        country = p.get('country', '')
        share = p.get('market_share', 0)
        rev = p.get('revenue', 0)
        products = p.get('key_products', '')
        lines.append(f"• {name} ({country}) — Market Share: {share}%, Revenue: ${rev}B")
        lines.append(f"  Products: {products}")
    return "\n".join(lines)


def format_fringe(fringe):
    if not fringe:
        return "No data available."
    lines = []
    for f in fringe:
        name = f.get('name', '')
        desc = f.get('description', '')
        year = f.get('year', '')
        impact = f.get('impact', '')
        lines.append(f"• {name} ({year}) — {desc}")
        lines.append(f"  Impact: {impact}")
    return "\n".join(lines)


def format_os_news(os_data):
    if not os_data:
        return "No data available."
    lines = []
    for os_name, data in os_data.items():
        news = data.get('news', '')
        version = data.get('version', '')
        share = data.get('market_share', 0)
        trend = data.get('trend', '')
        emoji = "📈" if trend == "growing" else "📉" if trend == "declining" else "➡️"
        lines.append(f"• {os_name} {emoji} (Market Share: {share}%)")
        lines.append(f"  Version: {version}")
        lines.append(f"  News: {news}")
    return "\n".join(lines)


def format_projections(projections):
    if not projections:
        return "No data available."
    yearly = projections.get('yearly_projections', {})
    if not yearly:
        return "No yearly projections available."
    lines = ["| Year | AI Market ($B) | Semiconductor ($B) | Cloud ($B) |"]
    lines.append("|------|----------------|-------------------|------------|")
    for year, data in yearly.items():
        ai = data.get('AI_market', 0)
        semi = data.get('semiconductor_market', 0)
        cloud = data.get('cloud_market', 0)
        lines.append(f"| {year} | {ai} | {semi} | {cloud} |")
    return "\n".join(lines)


def format_list(items):
    if not items:
        return "No data available."
    return "\n".join([f"• {item}" for item in items])


def format_dict(data):
    if not data:
        return "No data available."
    if isinstance(data, dict):
        return "\n".join([f"• {k}: {v}" for k, v in data.items()])
    return str(data)
