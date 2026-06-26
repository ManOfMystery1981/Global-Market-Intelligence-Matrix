# generate_full_report.py - Only create PDF from existing article
import os
import sys
import subprocess
import glob

def main():
    # Find the most recent article
    article_files = glob.glob("analyst_article_*.md")
    if not article_files:
        print("❌ No article file found!")
        print("📄 Available files:", glob.glob("*.md"))
        sys.exit(1)
    
    latest_article = sorted(article_files, key=os.path.getmtime)[-1]
    print(f"📄 Using existing article: {latest_article}")
    
    email = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUSTOMER_EMAIL", "")
    
    if not email:
        print("⚠️ No email provided.")
        sys.exit(0)
    
    os.environ["ANALYST_ARTICLE_PATH"] = latest_article
    
    # Only run delivery_bot.py - NOT llm_analyst_bot.py
    print(f"📄 Generating PDF for {email}...")
    result = subprocess.run([sys.executable, "delivery_bot.py", email], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
