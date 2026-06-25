# llm_analyst_prompt.py - Journalistic Style with Top 100
def generate_analyst_prompt(trend_data, metrics_data, crypto_data, stock_data, os_data, company_data=None):
    """Generate a comprehensive prompt with journalistic style and top 100 companies."""
    
    if company_data is None:
        from company_data_collector import TechCompanyDataCollector
        collector = TechCompanyDataCollector()
        company_data = collector.collect_all_data()
    
    # Format all data
    trends_text = format_trends_with_data(trend_data)
    metrics_text = format_metrics_with_data(metrics_data)
    crypto_text = format_crypto_with_data(crypto_data)
    stock_text = format_stocks_with_data(stock_data)
    os_text = format_os_with_data(os_data)
    companies_text = format_top_100_companies(company_data.get('top_companies', []))
    trending_text = format_trending_companies(company_data.get('trending_companies', []))
    trends_list_text = format_cutting_edge_trends(company_data.get('cutting_edge_trends', []))
    
    prompt = f"""You are a Senior Technology Journalist writing for a premier tech industry newsletter. Write with excitement, energy, and insight — like a journalist covering the most exciting developments in tech. The current year is 2026, and we're looking ahead to 2027.

## ⚠️ CRITICAL RULES
1. **ONLY use the data provided in this prompt**
2. **Write with journalistic excitement and energy** — this should feel like a must-read tech newsletter
3. **Highlight the top 10 companies** with their rankings and what makes them special
4. **Reference 2025, 2026, and 2027** as the current and upcoming years
5. **Make it engaging** — use bold statements, exciting language, and clear takeaways

## 📊 REAL DATA (USE ONLY THIS)

### TOP SOFTWARE TRENDS (2025-2026)
{trends_text}

### KEY METRICS (Current)
{metrics_text}

### CRYPTO MARKET DATA (Current)
{crypto_text}

### TECH STOCK PERFORMANCE (Current)
{stock_text}

### OPERATING SYSTEM POPULARITY (Current)
{os_text}

### TOP 100 TECH COMPANIES (Ranked) - USE THESE RANKINGS
{companies_text}

### TOP 10 TRENDING COMPANIES (by Growth) - HIGHLIGHT THESE
{trending_text}

### CUTTING-EDGE SOFTWARE TRENDS (2026-2027)
{trends_list_text}

## 📝 YOUR TASK

Write an exciting, journalistic tech article (1000-1500 words) with these sections:

1. **🚀 The Big Picture** - Executive summary with excitement about the tech landscape
2. **📊 Top 10 Tech Titans** - Highlight the top 10 companies with their rankings and why they dominate
3. **🔥 Trends That Are Reshaping Everything** - Deep dive into the hottest trends
4. **💡 Innovations That Will Define 2027** - Cutting-edge trends and what's next
5. **🎯 What This Means for You** - Strategic recommendations for CTOs, Developers, Founders, Recruiters

## 🎯 STYLE REQUIREMENTS

- **Journalistic tone** — think "TechCrunch" meets "The Information"
- **Exciting language** — use phrases like "breaking new ground," "reshaping the industry," "blockbuster year"
- **Clear takeaways** — every section should have a key insight
- **Rankings matter** — reference the top 10 companies by name and rank
- **Future-focused** — talk about 2026 and 2027 trends

## 🚫 ABSOLUTELY FORBIDDEN
- No boring, dry corporate language
- No data from before 2024
- No invented acquisitions or mergers
- No speculation about financial results not provided

Begin your exciting analysis now!"""
    return prompt

def format_top_100_companies(companies):
    """Format the top 100 companies with rankings and key metrics."""
    if not companies:
        return "No company data available."
    
    lines = []
    # Add the top 10 with special formatting
    lines.append("🏆 **TOP 10 TECH TITANS (Ranked):**")
    for company in companies[:10]:
        name = company.get('name', 'Unknown')
        rank = company.get('rank', 0)
        revenue = company.get('revenue_billions', 0)
        market_cap = company.get('market_cap_trillions', 0)
        ytd_change = company.get('ytd_change', 0)
        industry = company.get('industry', 'Unknown')
        trending = company.get('trending', '')
        
        line = f"  #{rank}. **{name}** — Revenue: ${revenue}B"
        if market_cap:
            line += f" | Market Cap: ${market_cap}T"
        if ytd_change:
            line += f" | YTD: {ytd_change}%"
        if trending:
            line += f" | 🔥 {trending}"
        lines.append(line)
    
    # Add the rest (ranks 11-100)
    lines.append("\n📊 **Top 100 Tech Companies (Ranks 11-100):**")
    for company in companies[10:]:
        name = company.get('name', 'Unknown')
        rank = company.get('rank', 0)
        revenue = company.get('revenue_billions', 0)
        industry = company.get('industry', 'Unknown')
        lines.append(f"  #{rank}. {name} — ${revenue}B revenue ({industry})")
    
    return "\n".join(lines)

def format_trending_companies(companies):
    """Format the top 10 trending companies with excitement."""
    if not companies:
        return "No trending company data available."
    
    lines = ["🚀 **TOP 10 TRENDING COMPANIES (by Growth):**"]
    for company in companies[:10]:
        name = company.get('name', 'Unknown')
        ytd_change = company.get('ytd_change', 0)
        industry = company.get('industry', 'Unknown')
        lines.append(f"  • {name}: {ytd_change}% YTD ({industry}) — 🔥 on fire!")
    
    return "\n".join(lines)

def format_cutting_edge_trends(trends):
    """Format cutting-edge trends with excitement."""
    if not trends:
        return "No trend data available."
    
    lines = ["💡 **CUTTING-EDGE TRENDS (2026-2027):**"]
    for trend in trends:
        name = trend.get('trend', 'Unknown')
        description = trend.get('description', '')
        adoption = trend.get('adoption_rate', 0)
        players = ', '.join(trend.get('key_players', []))
        lines.append(f"  • {name}: {description} (Adoption: {adoption}%, Key Players: {players})")
    
    return "\n".join(lines)

def format_trends_with_data(trends):
    """Format trends with specific data points."""
    if not trends:
        return "No trend data available."
    return "\n".join([f"  • {trend}" for trend in trends])

def format_metrics_with_data(metrics):
    """Format metrics with specific values."""
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

def format_crypto_with_data(crypto):
    """Format crypto data with specific prices."""
    if not crypto:
        return "No crypto data available."
    lines = []
    for coin, data in crypto.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"  • {coin}: ${price:.2f} (24h: {change:+.1f}%)")
    return "\n".join(lines)

def format_stocks_with_data(stocks):
    """Format stock data with specific prices."""
    if not stocks:
        return "No stock data available."
    lines = []
    for symbol, data in stocks.items():
        price = data.get('price', 0)
        change = data.get('change_24h', 0)
        lines.append(f"  • {symbol}: ${price:.2f} (24h: {change:+.1f}%)")
    return "\n".join(lines)

def format_os_with_data(os_data):
    """Format OS data with specific market shares."""
    if not os_data:
        return "No OS data available."
    lines = []
    market_share = os_data.get('market_share', {})
    for os_name, data in market_share.items():
        share = data.get('market_share', 0)
        trend = data.get('trend', 'stable')
        category = data.get('category', 'Unknown')
        emoji = "📈" if trend == "growing" else "📉" if trend == "declining" else "➡️"
        lines.append(f"  • {os_name}: {share}% market share {emoji} ({category})")
    return "\n".join(lines)
