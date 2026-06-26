# generate_full_report.py - Use existing article, don't regenerate
import os
import sys
import subprocess
import glob

def main():
    # Step 1: Find the most recent article
    article_files = glob.glob("analyst_article_*.md")
    if not article_files:
        print("❌ No article file found! Generating one...")
        # Only generate if no article exists
        subprocess.run([sys.executable, "llm_analyst_bot.py"], check=True)
        article_files = glob.glob("analyst_article_*.md")
        if not article_files:
            print("❌ Still no article file found!")
            sys.exit(1)
    
    latest_article = sorted(article_files)[-1]
    print(f"📄 Using existing article: {latest_article}")
    
    # Step 2: Get the email from arguments or environment
    email = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CUSTOMER_EMAIL", "")
    
    if not email:
        print("⚠️ No email provided. Skipping PDF generation.")
        sys.exit(0)
    
    # Step 3: Set the article path for delivery_bot
    os.environ["ANALYST_ARTICLE_PATH"] = latest_article
    
    # Step 4: Run the delivery bot with the existing article
    print(f"📄 Generating PDF with existing article for {email}...")
    subprocess.run([sys.executable, "delivery_bot.py", email], check=True)
    
    print("🎉 Report generation complete!")

if __name__ == "__main__":
    main()
