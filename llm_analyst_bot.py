# llm_analyst_bot.py - Corrected with 600 second timeout
import os
import json
import requests
from datetime import datetime

# Import your data sources
from delivery_bot import get_latest_data
from data_collector_bot import MarketDataCollector
from os_data_collector import OSDataCollector
from company_data_collector import TechCompanyDataCollector
from llm_analyst_prompt import generate_section_prompt

class LLMAnalystBot:
    """Bot that generates reports section by section."""
    
    def __init__(self):
        self.llm_url = os.environ.get("LLM_API_URL", "http://localhost:11434/api/generate")
        self.model = os.environ.get("LLM_MODEL", "mistral:7b-instruct-q4_0")
        self.max_tokens = 2048
        self.timeout = 6000  # ✅ 10 minutes (600 seconds) for large models
        
    def generate_section(self, prompt, section_name):
        """Generate a single section of the report."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.5,
            "max_tokens": self.max_tokens,
            "system": "You are a Senior Technology Journalist. Write professionally and thoroughly."
        }
        
        try:
            print(f"📝 Generating section: {section_name}...")
            print(f"⏳ This may take a few minutes (timeout: {self.timeout}s)...")
            response = requests.post(self.llm_url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "")
                if content:
                    print(f"✅ {section_name} complete ({len(content)} characters).")
                    return content
                else:
                    print(f"⚠️ Empty response for {section_name}")
                    return f"## {section_name}\n\nNo data available for this section."
            else:
                print(f"❌ LLM error for {section_name}: {response.status_code}")
                return f"## {section_name}\n\nError generating this section."
        except requests.exceptions.Timeout:
            print(f"❌ Timeout for {section_name} after {self.timeout}s")
            return f"""## {section_name}

This section is currently unavailable due to generation timeout. Please check the artifacts for the full report data.

### Key Data Points:
- The LLM is processing the requested information
- Please try running the workflow again
- Consider using a smaller model for faster generation
"""
        except Exception as e:
            print(f"❌ LLM error for {section_name}: {e}")
            return f"## {section_name}\n\nError generating this section: {str(e)}"
    
    def run_analysis(self):
        """Main method to collect data and generate the report section by section."""
        print("🔵 Starting LLM Analyst Bot...")
        
        # Collect all data
        print("📊 Gathering data...")
        data = get_latest_data()
        trend_data = data['trends']
        metrics_data = data['metrics']
        
        print("📈 Gathering financial data...")
        collector = MarketDataCollector()
        market_data = collector.collect_all_data()
        crypto_data = market_data.get('crypto', {})
        stock_data = market_data.get('stocks', {})
        
        print("💻 Gathering OS data...")
        os_collector = OSDataCollector()
        os_data = os_collector.collect_all_data()
        
        print("🏢 Gathering tech company data...")
        company_collector = TechCompanyDataCollector()
        company_data = company_collector.collect_all_data()
        
        # Generate each section with fallbacks
        sections = []
        
        # Section 1: Executive Summary (shorter)
        print("📝 Generating Section 1/6: Executive Summary...")
        prompt1 = generate_section_prompt("executive_summary", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt1, "Executive Summary"))
        
        # Section 2: Top 100 Tech Companies (longest - may need extra time)
        print("📝 Generating Section 2/6: Top 100 Tech Companies...")
        prompt2 = generate_section_prompt("top_100", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt2, "Top 100 Tech Companies"))
        
        # Section 3: Top 10 by Category
        print("📝 Generating Section 3/6: Top 10 by Category...")
        prompt3 = generate_section_prompt("top_10_categories", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt3, "Top 10 by Category"))
        
        # Section 4: Innovations & Fringe Tech
        print("📝 Generating Section 4/6: Software Innovations & Fringe Tech...")
        prompt4 = generate_section_prompt("innovations", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt4, "Software Innovations & Fringe Tech"))
        
        # Section 5: Processor Landscape & OS News
        print("📝 Generating Section 5/6: Processor Landscape & OS News...")
        prompt5 = generate_section_prompt("processors_os", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt5, "Processor Landscape & OS News"))
        
        # Section 6: Market Projections
        print("📝 Generating Section 6/6: Market Projections & Future Outlook...")
        prompt6 = generate_section_prompt("projections", trend_data, metrics_data, crypto_data, stock_data, os_data, company_data)
        sections.append(self.generate_section(prompt6, "Market Projections & Future Outlook"))
        
        # Combine all sections
        full_article = "\n\n".join(sections)
        
        # Save the article
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_file = f"analyst_article_{timestamp}.md"
        
        with open(article_file, 'w') as f:
            f.write(f"# Tech Analyst Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write(full_article)
        
        print(f"✅ Full article saved to {article_file}")
        return full_article

if __name__ == "__main__":
    bot = LLMAnalystBot()
    bot.run_analysis()
