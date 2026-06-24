import os
import sys
import sqlite3
import time
import http.client
import json

sys.stdout.reconfigure(line_buffering=True)

def generate_web_dashboard():
    """Reads your local corporate_ledger.db files and compiles a skinned HTML interface layout."""
    print("📊 Compiling Live Performance Portfolio Dashboard HTML using custom skin config...")
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
        print(f"⚠️ Dashboard skinning compilation aborted: {e}")

def push_telegram_sales_alert(amount_sol, customer_email):
    """Fires a high-priority HTML push notification via raw HTTPS sockets to completely bypass proxy blocks."""
    raw_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8736368782:AAGDt398paOLnHHCDNtJAJFk6bx0moJtm84").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "8794514690").strip()

    clean_token = raw_token
    if clean_token.lower().startswith("bot"):
        clean_token = clean_token[3:]

    print(f"📣 Dispatching socket metrics payload to Telegram ID: {chat_id}")
    
    message_text = f"<b>💰 CRITICAL BUSINESS REVENUE LOGGED 💰</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚙️ <b>Engine</b>: Autonomous Data Refinery\n📊 <b>Asset Purchased</b>: Market Intelligence Matrix\n💸 <b>Revenue Collected</b>: {amount_sol} SOL\n📨 <b>Delivery Pipeline</b>: Dispatched to Inbox\n📧 <b>Target Client</b>: <code>{customer_email}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n<i>🟢 System Node Status: 100% Operational</i>"

    try:
        # Isolated raw socket layout maps domain separately from the token path string
        host = "api.telegram.org"
        path = f"/bot{clean_token}/sendMessage"
        
        payload = json.dumps({
            "chat_id": str(chat_id),
            "text": message_text,
            "parse_mode": "HTML"
        })
        
        headers = {
            "Content-Type": "application/json",
            "Connection": "close"
        }
        
        conn = http.client.HTTPSConnection(host, timeout=10)
        conn.request("POST", path, body=payload, headers=headers)
        
        response = conn.getresponse()
        res_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        if res_data.get("ok"):
            print("✅ Telegram notification successfully routed to operator handheld terminal device.")
        else:
            print(f"❌ Telegram API Failure: {res_data}")
    except Exception as e:
        print(f"⚠️ Telegram alert connection routing dropped: {e}")
