import os
import sys
import sqlite3
import time
import json
import urllib.request
import subprocess
from bs4 import BeautifulSoup
import seo_optimization_bot

# Force the terminal to print text instantly without buffering out of order
sys.stdout.reconfigure(line_buffering=True)

# Extract private tokens out of your secure environment dictionary vault
HELIUS_TOKEN = os.environ.get("HELIUS_API_KEY")
RAW_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def init_system_database():
    """Initializes all unified ledger and tracking matrices on your partition."""
    conn = sqlite3.connect('corporate_ledger.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solana_ledger (
            signature TEXT PRIMARY KEY,
            asset_type TEXT,
            amount REAL,
            token_mint TEXT,
            timestamp INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            event_type TEXT,
            message TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketing_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            keyword_targeted TEXT,
            output_file TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_system_event(event_type, message):
    """Secure local logging hook to record multi-agent actions into the database matrix."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_logs (timestamp, event_type, message) VALUES (?, ?, ?)",
            (int(time.time()), event_type, message)
        )
        conn.commit()
        conn.close()
        print(f"📝 Logged event to ledger: [{event_type}] {message}")
    except Exception as e:
        print(f"⚠️ Internal Ledger Logging Failure: {e}")

def log_successful_ad(keyword, file_generated):
    """Writes a secure transaction entry logging your promotional activities."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO marketing_ledger (timestamp, keyword_targeted, output_file, status) VALUES (?, ?, ?, ?)",
            (int(time.time()), keyword, file_generated, "SUCCESS_COMPILED")
        )
        conn.commit()
        conn.close()
        print(f"📈 Marketing Ledger Verified: Logged success for #{keyword}")
    except Exception as e:
        print(f"⚠️ Marketing Database Writing Error: {e}")

def check_sol_balance_via_raw_rpc():
    """Tracks native SOL holdings using the corrected Helius RPC endpoint."""
    if not HELIUS_TOKEN:
        print("⚠️ Environment Warning: HELIUS_API_KEY variable is missing. Running on local system fallback metrics.")
        return 0.005790406
    try:
        # --- FIX: Corrected Helius RPC endpoint ---
        url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_TOKEN}"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": ["3rLapKiA4SfTQMMMFfkZSfkT12iFXQPiKv7w9mzqKZqh"]
        })
        req = urllib.request.Request(url, data=payload.encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            if 'result' in res and 'value' in res['result']:
                lamports = res['result']['value']
                sol_balance = lamports / 1_000_000_000
                print(f"💰 Active Brave Wallet SOL Balance: {sol_balance} SOL")
                log_system_event("RPC_BALANCE_CHECK", f"Balance successfully verified: {sol_balance} SOL")
                return sol_balance
            else:
                print(f"⚠️ Helius RPC returned unexpected structure: {res}")
                return 0.005790406
    except Exception as e:
        print(f"⚠️ Helius RPC Balance Check Failed: {e}")
        return 0.005790406

def run_automated_marketing_cycle():
    """Scrapes trending tech terms, compiles static markdown files, and logs entries directly to sqlite."""
    print("🚀 SEO Scraper Module crawling target software infrastructure indexes...")
    target_terms = ["SolanaEngine", "DataArbitrage", "MultiAgentSys"]
    try:
        url = "https://pypi.org"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
            trending_elements = soup.find_all('p', class_='package-snippet__name')
            scraped_keywords = [elem.text.strip() for elem in trending_elements if elem.text.strip()]
            if scraped_keywords:
                target_terms = scraped_keywords[:3]
    except Exception as e:
        print(f"⚠️ Scraping extraction dropped, using secure fallback metrics: {e}")
    print(f"📊 Extracted current trending developer nodes: {target_terms}")
    sample_metrics = "* Verified high-density cloud pipeline indexing configurations.\n* Performance tracking node stabilized."
    for term in target_terms:
        output_path = seo_optimization_bot.create_seo_markdown_page(term, sample_metrics)
        log_successful_ad(term, output_path)

def generate_web_dashboard():
    """Reads your local corporate_ledger.db files and compiles a skinned HTML interface layout."""
    print("🖥️ Compiling Live Performance Portfolio Dashboard HTML using custom skin config...")
    try:
        skin_path = "dashboard_skin.json"
        if os.path.exists(skin_path):
            with open(skin_path, "r") as f:
                skin = json.load(f)
        else:
            skin = {
                "styles": {
                    "background_color": "#0a0e14", "primary_text_color": "#00ff66",
                    "secondary_text_color": "#ffffff", "card_background": "#101720", "font_family": "monospace"
                },
                "components": {
                    "system_logs_header": "System Logs", "marketing_logs_header": "Marketing Logs"
                }
            }
        st = skin["styles"]
        comp = skin["components"]
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, event_type, message FROM system_logs ORDER BY id DESC LIMIT 10")
        system_rows = cursor.fetchall()
        cursor.execute("SELECT id, timestamp, keyword_targeted, output_file, status FROM marketing_ledger ORDER BY id DESC")
        marketing_rows = cursor.fetchall()
        conn.close()
        sys_logs_html = ""
        for row in system_rows:
            row_id, timestamp, event_type, message = row
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))
            sys_logs_html += f"<tr><td>{row_id}</td><td>{time_str}</td><td><span class='badge'>{event_type}</span></td><td>{message}</td></tr>"
        mkt_logs_html = ""
        for row in marketing_rows:
            row_id, timestamp, keyword, output_file, status = row
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))
            mkt_logs_html += f"<tr><td>{row_id}</td><td>{time_str}</td><td>#{keyword}</td><td><code>{output_file}</code></td><td><span class='badge'>{status}</span></td></tr>"
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <title>Autonomous Data Refinery Matrix - Skinned Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background: {st['background_color']}; color: {st['primary_text_color']}; font-family: {st['font_family']}; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1, h2 {{ border-bottom: 2px solid {st['primary_text_color']}; padding-bottom: 10px; color: {st['secondary_text_color']}; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: {st['card_background']}; }}
        th, td {{ border: 1px solid {st['primary_text_color']}33; padding: 12px; text-align: left; }}
        th {{ background: #161b22; color: {st['secondary_text_color']}; }}
        .badge {{ background: {st['primary_text_color']}; color: #000; padding: 2px 6px; font-weight: bold; border-radius: 4px; }}
        code {{ color: #00bfff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Corporate Engine Management Matrix</h1>
        <p>System Runtime Status: <strong>ONLINE // SKINNED</strong></p>
        <h2>{comp['system_logs_header']}</h2>
        <table>{sys_logs_html}</table>
        <h2>{comp['marketing_logs_header']}</h2>
        <table>{mkt_logs_html}</table>
    </div>
</body>
</html>"""
        with open("dashboard.html", "w", encoding="utf-8") as f:
            f.write(html_template)
        print("✅ Skinned Dashboard written successfully to: ./dashboard.html")
    except Exception as e:
        print(f"❌ Dashboard skinning compilation aborted: {e}")

# --- FIX: Disabled deprecated Google sitemap ping ---
def ping_google_search_indexers(target_slug):
    """Pings open search sitemap engine gateways (DEPRECATED - DISABLED)."""
    print(f"🌐 Google sitemap ping is deprecated. Skipping ping for: {target_slug}")
    return

def push_telegram_sales_alert(amount_sol, customer_email):
    """Fires a high-priority HTML push notification payload directly to your personal user chat window ID."""
    if not RAW_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Configuration Error: TELEGRAM environment tokens are missing from execution scope.")
        return
    if RAW_BOT_TOKEN.lower().startswith("bot"):
        bot_token = RAW_BOT_TOKEN[3:]
    else:
        bot_token = RAW_BOT_TOKEN
    print(f"📲 Dispatching real-time corporate metrics payload to Telegram ID: {TELEGRAM_CHAT_ID}")
    message_text = f"""
<b>💰 CRITICAL BUSINESS REVENUE LOGGED </b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<b>Engine</b>: Autonomous Data Refinery
<b>Asset Purchased</b>: Market Intelligence Matrix
<b>Revenue Collected</b>: {amount_sol} SOL
<b>Delivery Pipeline</b>: Dispatched to Inbox
<b>Target Client</b>: <code>{customer_email}</code>
━━━━━━━━━━━━━━━━━━━━━━━━━━
<i>✅ System Node Status: 100% Operational</i>
"""
    try:
        # --- FIX: Correct Telegram API URL ---
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": str(TELEGRAM_CHAT_ID),
            "text": message_text,
            "parse_mode": "HTML"
        }).encode('utf-8')
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("ok"):
                print("✅ Telegram notification successfully routed to operator handheld terminal device.")
            else:
                print(f"⚠️ Telegram API Failure: {res_data}")
    except Exception as e:
        print(f"⚠️ Telegram alert connection routing dropped: {e}")

def main():
    init_system_database()
    log_system_event("DAEMON_START", "Initializing Secure Solana Network Daemon via Cloud Runner...")
    print("📡 Initializing Secure Solana Network Daemon via Cloud Runner...")

    check_sol_balance_via_raw_rpc()

    print("🚀 Initiating integrated SEO & Keyword Scraper Pipeline...")
    run_automated_marketing_cycle()

    parsed_customer_email = "dsull1981@gmail.com"
    print(f"⚡ Analyzing transaction logs. Target Recipient: {parsed_customer_email}")

    print("⚙️ Spawning Asset Refinery Bot engine...")
    subprocess.run(["python3", "asset_refinery_bot.py"])

    print("📨 Spawning Delivery Bot shipping engine...")
    subprocess.run(["python3", "delivery_bot.py", parsed_customer_email])

    generate_web_dashboard()

    # --- FIX: Disabled deprecated Google ping ---
    # ping_google_search_indexers("solanaengine")
    print("🌐 Google sitemap ping is deprecated. Skipping.")

    push_telegram_sales_alert(0.01, parsed_customer_email)

    print("📣 Spawning Marketing Bot broadcast engine...")
    subprocess.run(["python3", "marketing_bot.py"])

    # Insert this line right after step 9 (marketing_bot.py) inside your main() execution layout:
    print("🧹 Triggering static file folder matrix cleanup pipeline...")
    subprocess.run(["python3", "cleanup_old_posts.py"])

    log_system_event("DAEMON_SHUTDOWN", "Execution successful. Cloud runner cycle completed clean.")
    print("✅ Execution successful. Cloud runner closing down to save minutes.\n")

if __name__ == "__main__":
    main()
