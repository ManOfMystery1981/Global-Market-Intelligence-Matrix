# generate_full_report.py - ONLY use existing article, NEVER regenerate
import os
import sys
import subprocess
import glob

def main():
    # Step 1: Find the most recent article (DO NOT regenerate)
    article_files = glob.glob("analyst_article_*.md")
    if not article_files:
        print("❌ No article file found! Please run llm_analyst_bot.py first.")
        sys.exit(1)
    
    # Get the latest article (by modification time or filename)
    latest_article = sorted(article_files, key=os.path.getmtime)[-1]
    print(f"📄 Using existing article: {latest_article}")
    
    # Read the article content to verify it's valid
    with open(latest_article, 'r') as f:
        content = f.read()
        if len(content) < 100:
            print(f"⚠️ Article file {latest_article} seems empty or too short ({len(content)} bytes)")
            # Try the next most recent
            if len(article_files) > 1:
                latest_article = sorted(article_files, key=os.path.getmtime)[-2]
                print(f"📄 Trying next article: {latest_article}")
    
    # Step 2: Get the email from arguments or environment
    email = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUSTOMER_EMAIL", "")
    
    if not email:
        print("⚠️ No email provided. Skipping PDF generation.")
        sys.exit(0)
    
    # Step 3: Set the article path for delivery_bot
    os.environ["ANALYST_ARTICLE_PATH"] = latest_article
    
    # Step 4: Run the delivery bot with the existing article
    print(f"📄 Generating PDF with existing article for {email}...")
    result = subprocess.run([sys.executable, "delivery_bot.py", email], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print("🎉 Report generation complete!")
    else:
        print("❌ Report generation failed!")

if __name__ == "__main__":
    main()
