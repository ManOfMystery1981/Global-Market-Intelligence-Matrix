# llm_analyst_bot.py - Complete corrected version
import os
import sys
import json
import requests
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import data sources with fallbacks
try:
    from delivery_bot import get_latest_data, get_sample_data, parse_markdown_data
except ImportError:
    print("⚠️ Could not import from delivery_bot.py, using fallback data functions")
    
    def get_latest_data():
        return {
            'trends': [
                "AI/ML adoption up 23% year-over-year across enterprise sectors",
                "Rust usage growing 15% among systems programmers",
                "Kubernetes remains dominant in cloud orchestration"
            ],
            'metrics': [
                {"Total frameworks tracked": "45"},
                {"Average developer salary": "$145,000"}
            ],
            'codebase_stats': {
                "Languages": "Python, HTML, JavaScript, Shell",
                "Stars": "0",
                "Forks": "0"
            }
        }
    
    def get_sample_data():
        return get_latest_data()
    
    def parse_markdown_data(content):
        return get_latest_data()

try:
    from data_collector_bot import MarketDataCollector
except ImportError:
    print("⚠️ Could not import data_collector_bot.py")
    class MarketDataCollector:
        def collect_all_data(self):
            return {"crypto": {}, "stocks": {}, "indices": {}}

try:
    from os_data_collector import OSDataCollector
except ImportError:
    print("⚠️ Could not import os_data_collector.py")
    class OSDataCollector:
        def collect_all_data(self):
            return {"market_share": {}}

try:
    from company_data_collector import TechCompanyDataCollector
except ImportError:
    print("⚠️ Could not import company_data_collector.py")
    class TechCompanyDataCollector:
        def collect_all_data(self):
            return {"top_100": [], "top_10_by_category": {}, "top_10_innovations": []}

try:
    from llm_analyst_prompt import generate_section_prompt
except ImportError:
    print("⚠️ Could not import llm_analyst_prompt.py, using built-in prompt")
    def generate_section_prompt(section, *args, **kwargs):
        return f"Write a section about {section} based on the provided data."


class LLMAnalystBot:
    """Bot that generates reports using a conversation-style segmented approach."""
    
    def __init__(self):
        self.llm_url = os.environ.get("LLM_API_URL", "http://localhost:11434/api/generate")
        self.model = os.environ.get("LLM_MODEL", "mistral:7b-instruct-q4_0")
        self.max_tokens = 2048
        self.timeout = 600  # 10 minutes per segment
        self.segments_per_section = 3
        
    def generate_segment(self, prompt: str, segment_name: str, context: str = "") -> str:
        """Generate a single segment of the article."""
        full_prompt = prompt
        if context:
            full_prompt = f"{prompt}\n\n**Previous context:**\n{context}\n\n**Continue from where you left off:**"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.5,
            "max_tokens": self.max_tokens,
            "num_ctx": 4096,
            "system": "You are a Senior Technology Journalist writing a comprehensive report. Continue the article naturally."
        }
        
        try:
            print(f"📝 Generating segment: {segment_name}...")
            session = requests.Session()
            response = session.post(
                self.llm_url,
                json=payload,
                timeout=(30, self.timeout)
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "")
                if content:
                    print(f"✅ {segment_name} complete ({len(content)} characters).")
                    return content
                else:
                    print(f"⚠️ Empty response for {segment_name}")
                    return ""
            else:
                print(f"❌ LLM error for {segment_name}: {response.status_code}")
                return ""
        except requests.exceptions.Timeout:
            print(f"❌ Timeout for {segment_name} after {self.timeout}s")
            return ""
        except Exception as e:
            print(f"❌ LLM error for {segment_name}: {e}")
            return ""
    
    def generate_section_with_segments(self, section_name: str, prompt_func, data: Dict) -> str:
        """Generate a complete section using multiple segments."""
        print(f"\n📝 Generating section: {section_name}")
        
        prompt = prompt_func(section_name, data)
        full_section = ""
        segment_count = 0
        context = ""
        
        for i in range(self.segments_per_section):
            segment_name = f"{section_name} (Segment {i+1}/{self.segments_per_section})"
            
            segment = self.generate_segment(prompt, segment_name, context)
            
            if segment:
                full_section += segment + "\n\n"
                segment_count += 1
                context = full_section[-2000:]
                print(f"📊 {section_name}: {len(full_section)} characters so far")
                
                prompt = f"""
Continue the {section_name} section of the tech analyst report.

**Context from previous segments:**
{context}

**Continue writing the {section_name} section.**
- Maintain the same professional, journalistic tone
- Add more detail and specific examples
- Use proper formatting with headings and bullets
- This is segment {i+2} of {self.segments_per_section}
"""
            else:
                print(f"⚠️ Empty segment, stopping early for {section_name}")
                break
        
        print(f"✅ {section_name} complete: {len(full_section)} characters, {segment_count} segments")
        return full_section
    
    def run_analysis(self) -> str:
        """Main method to collect data and generate the report section by section."""
        print("🔵 Starting LLM Analyst Bot with segmented generation...")
        
        # Collect all data
        print("📊 Gathering data...")
        try:
            data = get_latest_data()
            trend_data = data.get('trends', [])
            metrics_data = data.get('metrics', [])
        except Exception as e:
            print(f"⚠️ Error getting market data: {e}")
            trend_data = []
            metrics_data = []
        
        print("📈 Gathering financial data...")
        try:
            collector = MarketDataCollector()
            market_data = collector.collect_all_data()
            crypto_data = market_data.get('crypto', {})
            stock_data = market_data.get('stocks', {})
        except Exception as e:
            print(f"⚠️ Error getting financial data: {e}")
            crypto_data = {}
            stock_data = {}
        
        print("💻 Gathering OS data...")
        try:
            os_collector = OSDataCollector()
            os_data = os_collector.collect_all_data()
        except Exception as e:
            print(f"⚠️ Error getting OS data: {e}")
            os_data = {}
        
        print("🏢 Gathering tech company data...")
        try:
            company_collector = TechCompanyDataCollector()
            company_data = company_collector.collect_all_data()
        except Exception as e:
            print(f"⚠️ Error getting company data: {e}")
            company_data = {}
        
        # Combine data for prompts
        all_data = {
            'trend_data': trend_data,
            'metrics_data': metrics_data,
            'crypto_data': crypto_data,
            'stock_data': stock_data,
            'os_data': os_data,
            'company_data': company_data,
            'market_data': market_data if 'market_data' in locals() else {}
        }
        
        # Generate each section with segments
        sections = []
        section_names = [
            "Executive Summary",
            "Top 100 Tech Companies",
            "Top 10 by Category",
            "Software Innovations",
            "Fringe Tech Innovations",
            "Processor Landscape",
            "Operating System News",
            "Market Projections",
            "Data Arbitrage Value"
        ]
        
        for section_name in section_names:
            section_content = self.generate_section_with_segments(
                section_name,
                lambda s, d: generate_section_prompt(s, d.get('trend_data', []), d.get('metrics_data', []), d.get('crypto_data', {}), d.get('stock_data', {}), d.get('os_data', {}), d.get('company_data', {}), d.get('market_data', {})),
                all_data
            )
            if section_content:
                sections.append((section_name, section_content))
        
        # Combine all sections with headers
        full_article = ""
        for section_name, section_content in sections:
            if section_content:
                full_article += f"## {section_name}\n\n"
                full_article += section_content
                full_article += "\n\n---\n\n"
        
        # Save the article
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        article_file = f"analyst_article_{timestamp}.md"
        
        with open(article_file, 'w') as f:
            f.write(f"# Tech Analyst Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write(full_article)
        
        # Print file size
        file_size = os.path.getsize(article_file)
        print(f"\n✅ Full article saved to {article_file} ({file_size} bytes)")
        return full_article


if __name__ == "__main__":
    bot = LLMAnalystBot()
    bot.run_analysis()
