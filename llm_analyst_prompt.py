# llm_analyst_prompt.py - Section prompts
def generate_section_prompt(section, trend_data, metrics_data, crypto_data, stock_data, os_data, company_data):
    """Generate a prompt for a specific section."""
    
    # Common data formatting
    trends_text = format_list(trend_data)
    metrics_text = format_dict(metrics_data)
    crypto_text = format_dict(crypto_data)
    stock_text = format_dict(stock_data)
    os_text = format_dict(os_data)
    
    top_100_text = format_top_100(company_data.get('top_100', []))
    top_10_categories = format_top_10_categories(company_data.get('top_10_by_category', {}))
    innovations_text = format_innovations(company_data.get('top_10_innovations', []))
    processors_text = format_processors(company_data.get('processor_manufacturers', []))
    fringe_text = format_fringe(company_data.get('fringe_tech', []))
    os_news_text = format_os_news(company_data.get('os_news', {}))
    projections_text = format_projections(company_data.get('market_projections', {}))
    
    if section == "executive_summary":
        return f"""You are a Senior Technology Journalist. Write an exciting Executive Summary for a tech industry report.

**DATA:**
- Trends: {trends_text}
- Top Companies: {top_100_text[:500]}
- Projections: {projections_text}

**RULES:**
- Write with excitement and energy
- Highlight the biggest stories of 2026
- Mention the top 3 companies by name
- Keep it to 1-2 paragraphs

**OUTPUT:** Write the Executive Summary in journalistic style with bold headings and clear takeaways.
"""
    
    elif section == "top_100":
        return f"""You are a Senior Technology Journalist. Write a detailed section on the Top 100 Tech Companies.

**DATA:**
{top_100_text}

**RULES:**
- Show the full ranked list (all 100 companies)
- Highlight the top 10 with special attention
- Use a clean, readable format
- Include revenue, market cap, and YTD change
- Use proper bullets (•) and formatting

**OUTPUT:** Write the full section with clear formatting and professional presentation.
"""
    
    elif section == "top_10_categories":
        return f"""You are a Senior Technology Journalist. Write a section on the Top 10 Companies by Category.

**DATA:**
{top_10_categories}

**RULES:**
- Show top 10 by revenue, growth, market cap, and innovation
- Highlight key insights about each category
- Use professional formatting

**OUTPUT:** Write the section with clear categories and insights.
"""
    
    elif section == "innovations":
        return f"""You are a Senior Technology Journalist. Write a section on Software Innovations and Fringe Tech.

**DATA:**
- Top 10 Innovations: {innovations_text}
- Fringe Tech: {fringe_text}

**RULES:**
- Be exciting and engaging
- Highlight the most impactful innovations
- Mention the Raspberry Pi supercomputer
- Use proper formatting

**OUTPUT:** Write the section with energy and insight.
"""
    
    elif section == "processors_os":
        return f"""You are a Senior Technology Journalist. Write a section on Processors and OS News.

**DATA:**
- Processors: {processors_text}
- OS News: {os_news_text}

**RULES:**
- Cover Intel, AMD, ARM, RISC-V, Russian/Chinese
- Include latest OS news for each major OS
- Show market share and trends

**OUTPUT:** Write the section with clear headings and bullet points.
"""
    
    elif section == "projections":
        return f"""You are a Senior Technology Journalist. Write a section on Market Projections to 2035.

**DATA:**
{projections_text}

**RULES:**
- Show projections for AI, semiconductor, and cloud markets
- Include the year-by-year table
- Highlight key milestones and trends
- Be exciting about future possibilities

**OUTPUT:** Write the section with the table and analysis.
"""
    
    else:
        return "Write a general tech industry section."

def format_top_100(companies):
    """Format top 100 companies."""
    if not companies:
        return "No data available."
    lines = []
    for c in companies:
        rank = c.get('rank', 0)
        name = c.get('name', 'Unknown')
        rev = c.get('revenue', 0)
        mc = c.get('market_cap', 0)
        ytd = c.get('ytd_change', 0)
        industry = c.get('industry', '')
        lines.append(f"{rank}. {name} — Revenue: ${rev}B, Market Cap: ${mc}T, YTD: {ytd}%, {industry}")
    return "\n".join(lines)

def format_top_10_categories(categories):
    """Format top 10 by category."""
    if not categories:
        return "No data available."
    lines = []
    for cat, items in categories.items():
        lines.append(f"**{cat.replace('_', ' ').title()}:**")
        for i, name in enumerate(items[:10], 1):
            lines.append(f"  {i}. {name}")
    return "\n".join(lines)

def format_innovations(innovations):
    """Format innovations list."""
    if not innovations:
        return "No data available."
    lines = []
    for i in innovations:
        name = i.get('name', '')
        desc = i.get('description', '')
        year = i.get('year', '')
        impact = i.get('impact', '')
        lines.append(f"• **{name}** — {desc} ({year}) [Impact: {impact}]")
    return "\n".join(lines)

def format_processors(processors):
    """Format processor list."""
    if not processors:
        return "No data available."
    lines = []
    for p in processors:
        name = p.get('name', '')
        country = p.get('country', '')
        share = p.get('market_share', 0)
        rev = p.get('revenue', 0)
        products = p.get('key_products', '')
        lines.append(f"• **{name}** ({country}) — Market Share: {share}%, Revenue: ${rev}B")
        lines.append(f"  Products: {products}")
    return "\n".join(lines)

def format_fringe(fringe):
    """Format fringe tech list."""
    if not fringe:
        return "No data available."
    lines = []
    for f in fringe:
        name = f.get('name', '')
        desc = f.get('description', '')
        year = f.get('year', '')
        impact = f.get('impact', '')
        lines.append(f"• **{name}** ({year}) — {desc}")
        lines.append(f"  Impact: {impact}")
    return "\n".join(lines)

def format_os_news(os_data):
    """Format OS news."""
    if not os_data:
        return "No data available."
    lines = []
    for os_name, data in os_data.items():
        news = data.get('news', '')
        version = data.get('version', '')
        share = data.get('market_share', 0)
        trend = data.get('trend', '')
        emoji = "📈" if trend == "growing" else "📉" if trend == "declining" else "➡️"
        lines.append(f"• **{os_name}** {emoji} (Market Share: {share}%)")
        lines.append(f"  Version: {version}")
        lines.append(f"  News: {news}")
    return "\n".join(lines)

def format_projections(projections):
    """Format market projections."""
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
