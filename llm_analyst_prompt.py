# llm_analyst_prompt.py - Complete version with all formatting functions
import json
from datetime import datetime

def generate_analyst_prompt(trend_data, metrics_data, crypto_data, stock_data, os_data, company_data=None):
    """Generate the complete prompt with all sections."""
    
    if company_data is None:
        from company_data_collector import TechCompanyDataCollector
        collector = TechCompanyDataCollector()
        company_data = collector.collect_all_data()
    
    # Format all sections
    top_100_text = format_top_100(company_data.get('top_100', []))
    top_10_by_category_text = format_top_10_by_category(company_data.get('top_10_by_category', {}))
    innovations_text = format_top_10_innovations(company_data.get('top_10_innovations', []))
    processors_text = format_processors(company_data.get('processor_manufacturers', []))
    fringe_text = format_fringe_tech(company_data.get('fringe_tech', []))
    os_news_text = format_os_news(company_data.get('os_news', {}))
    projections_text = format_market_projections(company_data.get('market_projections', {}))
    
    prompt = f"""You are a Senior Technology Journalist with 20 years of experience covering the tech industry. Write an exciting, data-driven article for a premium tech newsletter. Use ONLY the data provided below.

## 📊 COMPLETE MARKET DATA

### TOP 100 TECH COMPANIES (Ranked 1-100)
{top_100_text}

### TOP 10 BY CATEGORY
{top_10_by_category_text}

### TOP 10 SOFTWARE ENGINEERING INNOVATIONS
{innovations_text}

### PROCESSOR MANUFACTURERS (Including Intel, AMD, ARM, Russian/Chinese)
{processors_text}

### FRINGE TECH INNOVATIONS
{fringe_text}

### LATEST OS NEWS
{os_news_text}

### MARKET PROJECTIONS (2025-2035)
{projections_text}

### TOP SOFTWARE TRENDS
{format_trends(trend_data)}

### KEY METRICS
{format_metrics(metrics_data)}

### CRYPTO & STOCK DATA
{format_crypto(crypto_data)}
{format_stocks(stock_data)}

## 📝 YOUR TASK

Write an exciting, journalistic article with these sections:

1. 🚀 The Big Picture - Executive summary of the tech landscape in 2026
2. 🏆 Top 100 Tech Titans - Show the ranked list with highlights of the top 10
3. 📊 Top 10 by Category - Show rankings by revenue, growth, market cap, innovation
4. 💡 Top 10 Innovations - Software engineering breakthroughs
5. 🔬 Processor Landscape - Intel, AMD, ARM, RISC-V, Russian/Chinese processors
6. 🛠️ Fringe Tech - Raspberry Pi supercomputers, DIY projects, open source hardware
7. 🖥️ OS News - Latest updates for Windows, macOS, Linux, ChromeOS, FreeBSD, Android, iOS
8. 📈 Market Projections - AI, semiconductor, and cloud markets to 2035

## 🎯 FORMATTING

- Top 100: Show as a numbered list with revenue and market cap
- Top 10 by Category: Show with sections
- Exciting tone - Think "TechCrunch" meets "The Information"
- Future-focused - Reference 2026 and 2027 as current years

Begin your analysis now!"""
    return prompt


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


def format_top_10_by_category(categories):
    """Format the top 10 by different categories."""
    if not categories:
        return "No category data available."
    
    lines = []
    for category, companies in categories.items():
        lines.append(f"\n  **{category.replace('_', ' ').title()}:**")
        for i, name in enumerate(companies[:10], 1):
            lines.append(f"    {i}. {name}")
    
    return "\n".join(lines)


def format_top_10_innovations(innovations):
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


def format_fringe_tech(fringe):
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


def format_market_projections(projections):
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


def format_trends(trends):
    """Format trends data."""
    if not trends:
        return "No trend data available."
    return "\n".join([f"  • {trend}" for trend in trends])


def format_metrics(metrics):
    """Format metrics data."""
    if not metrics:
        return "No metrics data available."
    lines = []
    for metric in metrics:
        if isinstance(metric, dict):
            for key, value in metric.items():
                lines.append(f"  • {key}: {value}")
        else:
            lines.append(f"  • {metric}")
    return "\n".join(lines)


def format_crypto(crypto):
    """Format crypto data."""
    if not crypto:
        return "No crypto data available."
    lines = []
    for coin, data in crypto.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"  • {coin}: ${price:.2f} (24h: {change:+.1f}%)")
    return "\n".join(lines)


def format_stocks(stocks):
    """Format stock data."""
    if not stocks:
        return "No stock data available."
    lines = []
    for symbol, data in stocks.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"  • {symbol}: ${price:.2f} (24h: {change:+.1f}%)")
    return "\n".join(lines)
