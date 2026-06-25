# generate_full_report.py - Combined script for full report generation
import os
import sys
import subprocess

# Step 1: Run the LLM analyst bot to generate the article
print("🤖 Step 1: Generating LLM analyst article...")
subprocess.run([sys.executable, "llm_analyst_bot.py"], check=True)

# Step 2: Find the most recent article file
import glob
import re
article_files = glob.glob("analyst_article_*.md")
if article_files:
    latest_article = sorted(article_files)[-1]
    print(f"📄 Found article: {latest_article}")
    
    # Read the article content
    with open(latest_article, 'r') as f:
        article_content = f.read()
    
    # Step 3: Get the email from arguments or environment
    email = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUSTOMER_EMAIL", "dsull1981@gmail.com")
    
    # Step 4: Run the delivery bot with the article
    print("📄 Step 3: Generating PDF with article...")
    # Pass the article file path to delivery_bot via environment
    os.environ["ANALYST_ARTICLE_PATH"] = latest_article
    subprocess.run([sys.executable, "delivery_bot.py", email], check=True)
else:
    print("❌ No article file found!")
    sys.exit(1)
