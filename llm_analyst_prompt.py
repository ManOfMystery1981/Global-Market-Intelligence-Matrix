# llm_analyst_prompt.py - Complete file with dynamic data arbitrage value
import json
from datetime import datetime

# Import the dynamic arbitrage calculator
try:
    from data_arbitrage_value import DataArbitrageValueCalculator
except ImportError:
    # Fallback if the module doesn't exist
    class DataArbitrageValueCalculator:
        def __init__(self, crypto_data, stock_data, market_data):
            self.crypto_data = crypto_data
            self.stock_data = stock_data
            self.market_data = market_data
        def generate_arbitrage_report(self):
            return {
                "timestamp": datetime.now().isoformat(),
                "summary": "## 💰 DATA ARBITRAGE MARKET VALUE\n\nMarket data is currently being processed."
            }

# --- SECTION PROMPTS ---
def generate_section_prompt(section, trend_data, metrics_data, crypto_data, stock_data, os_data, company_data, market_data=None):
    """Generate a prompt for a specific section."""
    
    # Format the data
    trends_text = format_list(trend_data)
    metrics_text = format_dict(metrics_data)
    crypto_text = format_dict(crypto_data)
    stock_text = format_dict(stock_data)
    os_text = format_dict(os_data)
    
    # Get company data
    top_100 = company_data.get('top_100', [])
    top_100_text = format_top_100(top_100)
    top_10_categories = format_top_10_categories(company_data.get('top_10_by_category', {}))
    innovations_text = format_innovations(company_data.get('top_10_innovations', []))
    processors_text = format_processors(company_data.get('processor_manufacturers', []))
    fringe_text = format_fringe(company_data.get('fringe_tech', []))
    os_news_text = format_os_news(company_data.get('os_news', {}))
    projections_text = format_projections(company_data.get('market_projections', {}))
    
    # Calculate dynamic arbitrage value
    if market_data is None:
        market_data = {}
    
    try:
        calculator = DataArbitrageValueCalculator(crypto_data, stock_data, market_data)
        arbitrage_report = calculator.generate_arbitrage_report()
        arbitrage_text = arbitrage_report.get('summary', '')
    except Exception as e:
        print(f"⚠️ Error generating arbitrage report: {e}")
        arbitrage_text = "## 💰 DATA ARBITRAGE MARKET VALUE\n\nData arbitrage value calculations are currently unavailable."

    # Generate the appropriate prompt based on the section
    if section == "executive_summary":
        return f"""
You are a Senior Technology Journalist writing a comprehensive tech industry report for a premium newsletter. Write the Executive Summary.

## 📊 REAL-TIME MARKET DATA

### TOP SOFTWARE TRENDS (2026)
{trends_text}

### CURRENT MARKET METRICS
{metrics_text}

### CRYPTO & STOCK PRICES
{crypto_text}
{stock_text}

### TOP TECH COMPANIES (Ranked)
{top_100_text[:3000]}

{arbitrage_text}

## 📝 YOUR TASK

Write an exciting, journalistic Executive Summary (800-1200 words) that:
1. Captures the current state of the tech industry in 2026
2. Highlights the biggest stories and trends
3. Mentions the top 3 companies and their performance
4. Teases the data arbitrage opportunity
5. Sets up the rest of the report

**STYLE:** Think "TechCrunch meets The Information" — energetic, data-driven, and insightful.

**FORMAT:** Use bold headings, bullet points, and clear sections.

Begin your Executive Summary now.
"""

    elif section == "top_100":
        return f"""
You are a Senior Technology Journalist. Write a detailed section on the Top 100 Tech Companies.

## 📊 TOP 100 TECH COMPANIES DATA
{top_100_text}

## 📝 YOUR TASK

Write a comprehensive section (1000-1500 words) that:
1. Shows the full ranked list (all 100 companies)
2. Highlights the top 10 with special attention
3. Groups companies by industry
4. Includes revenue, market cap, and YTD change
5. Identifies patterns and trends among the top 100

**FORMAT:** Use clear headings, proper bullets (•), and professional formatting.

Begin your analysis now.
"""

    elif section == "top_10_categories":
        return f"""
You are a Senior Technology Journalist. Write a section on the Top 10 Companies by Category.

## 📊 TOP 10 BY CATEGORY
{top_10_categories}

## 📝 YOUR TASK

Write a detailed section (500-800 words) that:
1. Shows top 10 by revenue, growth, market cap, and innovation
2. Highlights key insights about each category
3. Explains why certain companies dominate specific categories
4. Mentions notable trends in the rankings

**FORMAT:** Use clear categories and professional formatting.

Begin your analysis now.
"""

    elif section == "innovations":
        return f"""
You are a Senior Technology Journalist. Write a section on Software Innovations.

## 📊 TOP 10 SOFTWARE INNOVATIONS
{innovations_text}

## 📝 YOUR TASK

Write a detailed section (500-800 words) that:
1. Explains each innovation and why it matters
2. Highlights the most impactful ones
3. Mentions the companies leading each innovation
4. Discusses the future potential of these innovations

**FORMAT:** Use clear headings and bullet points.

Begin your analysis now.
"""

    elif section == "fringe":
        return f"""
You are a Senior Technology Journalist. Write a section on Fringe Tech Innovations.

## 📊 FRINGE TECH INNOVATIONS
{fringe_text}

## 📝 YOUR TASK

Write an exciting section (500-800 words) that:
1. Covers the Raspberry Pi supercomputer
2. Discusses open source hardware and DIY projects
3. Highlights community-driven innovation
4. Explains why fringe tech matters for the industry

**FORMAT:** Use engaging language and clear sections.

Begin your analysis now.
"""

    elif section == "processors_os":
        return f"""
You are a Senior Technology Journalist. Write a section on the Processor Landscape and OS News.

## 📊 PROCESSOR MANUFACTURERS
{processors_text}

## 📊 OS NEWS
{os_news_text}

## 📝 YOUR TASK

Write a detailed section (500-800 words) that:
1. Covers Intel, AMD, ARM, RISC-V, Russian/Chinese processors
2. Discusses market share and performance trends
3. Includes latest OS news for each major OS
4. Explains how processors and OS trends are connected

**FORMAT:** Use clear headings and professional formatting.

Begin your analysis now.
"""

    elif section == "os_news":
        return f"""
You are a Senior Technology Journalist. Write a section on Operating System News.

## 📊 OS NEWS
{os_news_text}

## 📝 YOUR TASK

Write a detailed section (500-800 words) that:
1. Covers Windows, macOS, Linux, ChromeOS, FreeBSD, Android, iOS
2. Highlights the latest updates and news for each
3. Discusses market share trends
4. Mentions what's coming next for each OS

**FORMAT:** Use clear headings and bullet points.

Begin your analysis now.
"""

    elif section == "projections":
        return f"""
You are a Senior Technology Journalist. Write a section on Market Projections to 2035.

## 📊 MARKET PROJECTIONS
{projections_text}

## 📝 YOUR TASK

Write a detailed section (500-800 words) that:
1. Shows projections for AI, semiconductor, and cloud markets
2. Highlights key milestones and turning points
3. Discusses what drives these projections
4. Explains what this means for the tech industry

**FORMAT:** Use the table format and clear analysis.

Begin your analysis now.
"""

    elif section == "arbitrage_value":
        return f"""
You are a Senior Technology Journalist. Write a section on the Data Arbitrage Market Value.

{arbitrage_text}

## 📝 YOUR TASK

Write a compelling section (500-800 words) that:
1. Explains why data arbitrage reports sell for $50,000+
2. Details the three pricing tiers
3. Discusses the 40% net profit margin opportunity
4. Explains how this report delivers the same value at 0.01 SOL

**FORMAT:** Use clear headings, dollar amounts, and a professional tone.

Begin your analysis now.
"""

    else:
        # Default prompt
        return f"""
You are a Senior Technology Journalist. Write a professional section about {section}.

**DATA:**
- Trends: {trends_text[:500]}
- Metrics: {metrics_text[:500]}

**FORMAT:** Use clear headings and professional language.

Begin your analysis now.
"""


# --- FORMATTING FUNCTIONS ---
def format_top_100(companies):
    """Format the top 100 companies with rankings and key metrics."""
    if not companies:
        return "No company data available."
    
    lines = []
    for company in companies[:100]:
        rank = company.get('rank', 0)
        name = company.get('name', 'Unknown')
        revenue = company.get('revenue', 0)
        profit = company.get('profit', 0)
        market_cap = company.get('market_cap', 0)
        ytd_change = company.get('ytd_change', 0)
        industry = company.get('industry', 'Unknown')
        
        line = f"  #{rank}. {name} — Revenue: ${revenue}B"
        if profit:
            line += f", Profit: ${profit}B"
        if market_cap:
            line += f", Market Cap: ${market_cap}T"
        if ytd_change:
            line += f", YTD: {ytd_change}%"
        line += f" ({industry})"
        lines.append(line)
    
    return "\n".join(lines)


def format_top_10_categories(categories):
    """Format the top 10 by different categories."""
    if not categories:
        return "No category data available."
    
    lines = []
    for category, companies in categories.items():
        lines.append(f"\n  **{category.replace('_', ' ').title()}:**")
        for i, name in enumerate(companies[:10], 1):
            lines.append(f"    {i}. {name}")
    
    return "\n".join(lines)


def format_innovations(innovations):
    """Format the top 10 software engineering innovations."""
    if not innovations:
        return "No innovation data available."
    
    lines = []
    for inv in innovations:
        rank = inv.get('rank', 0)
        name = inv.get('name', 'Unknown')
        description = inv.get('description', '')
        year = inv.get('year', '')
        impact = inv.get('impact', '')
        lines.append(f"  #{rank}. {name} — {description} ({year}) [Impact: {impact}]")
    
    return "\n".join(lines)


def format_processors(processors):
    """Format processor manufacturers with key details."""
    if not processors:
        return "No processor data available."
    
    lines = []
    for p in processors:
        name = p.get('name', 'Unknown')
        country = p.get('country', '')
        products = p.get('key_products', '')
        market_share = p.get('market_share', 0)
        revenue = p.get('revenue', 0)
        lines.append(f"  • {name} ({country}) — Market Share: {market_share}%, Revenue: ${revenue}B")
        lines.append(f"    Products: {products}")
    
    return "\n".join(lines)


def format_fringe(fringe):
    """Format fringe tech innovations."""
    if not fringe:
        return "No fringe tech data available."
    
    lines = []
    for item in fringe:
        name = item.get('name', 'Unknown')
        description = item.get('description', '')
        year = item.get('year', '')
        impact = item.get('impact', '')
        lines.append(f"  • {name} ({year}) — {description}")
        lines.append(f"    Impact: {impact}")
    
    return "\n".join(lines)


def format_os_news(os_data):
    """Format OS news with latest updates."""
    if not os_data:
        return "No OS news data available."
    
    lines = []
    for os_name, data in os_data.items():
        news = data.get('news', '')
        version = data.get('version', '')
        market_share = data.get('market_share', 0)
        trend = data.get('trend', '')
        emoji = "📈" if trend == "growing" else "📉" if trend == "declining" else "➡️"
        lines.append(f"\n  **{os_name}** {emoji} (Market Share: {market_share}%)")
        lines.append(f"    Version: {version}")
        lines.append(f"    News: {news}")
    
    return "\n".join(lines)


def format_projections(projections):
    """Format market projections to 2035."""
    if not projections:
        return "No projection data available."
    
    yearly = projections.get('yearly_projections', {})
    if not yearly:
        return "No yearly projection data available."
    
    lines = ["  Year | AI Market ($B) | Semiconductor ($B) | Cloud ($B)"]
    lines.append("  -----|----------------|-------------------|------------")
    
    for year, data in yearly.items():
        ai = data.get('AI_market', 0)
        semi = data.get('semiconductor_market', 0)
        cloud = data.get('cloud_market', 0)
        lines.append(f"  {year}  | {ai:14} | {semi:17} | {cloud:10}")
    
    return "\n".join(lines)


def format_list(items):
    """Format a list with bullet points."""
    if not items:
        return "No data available."
    return "\n".join([f"  • {item}" for item in items])


def format_dict(data):
    """Format a dictionary with bullet points."""
    if not data:
        return "No data available."
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"  • {key}: {value}")
            else:
                lines.append(f"  • {key}: {value}")
        return "\n".join(lines) if lines else "No data available."
    return str(data)
