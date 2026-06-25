# llm_analyst_prompt.py - Complete with all requested sections
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
{format_list(trend_data)}

### KEY METRICS
{format_dict(metrics_data)}

### CRYPTO & STOCK DATA
{format_dict(crypto_data)}
{format_dict(stock_data)}

## 📝 YOUR TASK

Write an exciting, journalistic article with these sections:

1. **🚀 The Big Picture** - Executive summary of the tech landscape in 2026
2. **🏆 Top 100 Tech Titans** - Show the ranked list with highlights of the top 10
3. **📊 Top 10 by Category** - Show rankings by revenue, growth, market cap, innovation
4. **💡 Top 10 Innovations** - Software engineering breakthroughs
5. **🔬 Processor Landscape** - Intel, AMD, ARM, RISC-V, Russian/Chinese processors
6. **🛠️ Fringe Tech** - Raspberry Pi supercomputers, DIY projects, open source hardware
7. **🖥️ OS News** - Latest updates for Windows, macOS, Linux, ChromeOS, FreeBSD, Android, iOS
8. **📈 Market Projections** - AI, semiconductor, and cloud markets to 2035

## 🎯 FORMATTING

- **Top 100**: Show as a numbered list with revenue and market cap
- **Top 10 by Category**: Show with color-coded sections
- **Charts**: Use ASCII charts for rankings
- **Exciting tone** - Think "TechCrunch" meets "The Information"
- **Future-focused** - Reference 2026 and 2027 as current years

Begin your analysis now!"""
    return prompt
