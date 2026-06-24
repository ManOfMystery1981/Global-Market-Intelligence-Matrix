#!/usr/bin/env python3
"""
decision_engine.py - Autonomous System Decision Engine
Runs every 6 hours to monitor, analyze, and act.
"""

import os
import sys
import sqlite3
import json
import time
import subprocess
import urllib.request
from datetime import datetime, timedelta

# --- Configuration ---
HELIUS_TOKEN = os.environ.get("HELIUS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WALLET_ADDRESS = "3rLapKiA4SfTQMMMFfkZSfkT12iFXQPiKv7w9mzqKZqh"
WEBHOOK_URL = "https://autonomous-data-refiner.vercel.app/api/webhook"

# --- Logging ---
def log_decision(event_type, message):
    """Log decisions to the system ledger."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS decision_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, event_type TEXT, message TEXT)"
        )
        cursor.execute(
            "INSERT INTO decision_log (timestamp, event_type, message) VALUES (?, ?, ?)",
            (int(time.time()), event_type, message)
        )
        conn.commit()
        conn.close()
        print(f"🧠 Decision logged: [{event_type}] {message}")
    except Exception as e:
        print(f"⚠️ Decision logging failed: {e}")

def send_telegram_alert(message):
    """Send a Telegram alert."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        bot_token = TELEGRAM_BOT_TOKEN[3:] if TELEGRAM_BOT_TOKEN.lower().startswith("bot") else TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": str(TELEGRAM_CHAT_ID),
            "text": f"🧠 DECISION ENGINE ALERT:\n\n{message}",
            "parse_mode": "HTML"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if json.loads(response.read().decode('utf-8')).get("ok"):
                print("📲 Telegram alert sent.")
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")

# --- Observers ---

def check_wallet_balance():
    """Check SOL balance via Helius RPC."""
    if not HELIUS_TOKEN:
        return 0.005790406
    try:
        url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_TOKEN}"
        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [WALLET_ADDRESS]
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            if 'result' in res and 'value' in res['result']:
                return res['result']['value'] / 1_000_000_000
    except Exception as e:
        print(f"⚠️ Balance check failed: {e}")
    return 0.005790406

def check_recent_sales(days=7):
    """Count only real sales (source = 'webhook' or status = 'SALE')."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cutoff = int(time.time()) - (days * 86400)
        cursor.execute(
            "SELECT COUNT(*) FROM marketing_ledger WHERE timestamp > ? AND (status = 'SALE' OR source = 'webhook')",
            (cutoff,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"⚠️ Sales check failed: {e}")
        return 0

def check_webhook_health():
    """Ping the webhook to ensure it's alive."""
    try:
        req = urllib.request.Request(WEBHOOK_URL, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception:
        return False

def check_system_logs():
    """Check for recent errors in system_logs."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cutoff = int(time.time()) - 86400  # Last 24 hours
        cursor.execute(
            "SELECT COUNT(*) FROM system_logs WHERE timestamp > ? AND event_type LIKE '%ERROR%'",
            (cutoff,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"⚠️ Log check failed: {e}")
        return 0

# --- Decision Makers ---

def make_decisions():
    """Run all checks and take actions."""
    log_decision("CYCLE_START", "Decision engine cycle started.")
    print("🧠 Running decision engine cycle...")

    # --- 1. Check wallet balance ---
    balance = check_wallet_balance()
    print(f"💰 Current SOL balance: {balance}")
    if balance < 0.01:
        msg = f"⚠️ Low balance: {balance} SOL. Pausing non-essential bots."
        log_decision("LOW_BALANCE", msg)
        send_telegram_alert(msg)
        subprocess.run(["python3", "pause_bots.py"])

    # --- 2. Check sales performance (now accurate) ---
    sales = check_recent_sales(7)
    print(f"📊 Real sales in last 7 days: {sales}")
    if sales < 2:
        msg = f"⚠️ Low sales: {sales} in 7 days. Adjusting marketing."
        log_decision("LOW_SALES", msg)
        send_telegram_alert(msg)
        subprocess.run(["python3", "adaptive_marketing.py"])

    # --- 3. Check webhook health ---
    webhook_ok = check_webhook_health()
    print(f"🌐 Webhook health: {'✅ OK' if webhook_ok else '❌ DOWN'}")
    if not webhook_ok:
        msg = "🚨 Webhook is down! Check Vercel deployment."
        log_decision("WEBHOOK_DOWN", msg)
        send_telegram_alert(msg)

    # --- 4. Check for system errors ---
    errors = check_system_logs()
    print(f"📝 Errors in last 24h: {errors}")
    if errors > 5:
        msg = f"⚠️ High error rate: {errors} errors in last 24h."
        log_decision("HIGH_ERROR_RATE", msg)
        send_telegram_alert(msg)

    # --- 5. Check if reports are being generated ---
    try:
        with open("market_intelligence.md", "r") as f:
            content = f.read()
            if len(content) < 100:
                msg = "⚠️ Report file is too small. Possible generation issue."
                log_decision("REPORT_ISSUE", msg)
                send_telegram_alert(msg)
    except FileNotFoundError:
        msg = "🚨 market_intelligence.md not found!"
        log_decision("REPORT_MISSING", msg)
        send_telegram_alert(msg)

    # --- 6. Check SEO pages ---
    posts_dir = "./posts"
    if os.path.exists(posts_dir):
        post_count = len([f for f in os.listdir(posts_dir) if f.endswith('.md')])
        print(f"📄 SEO pages: {post_count}")
        if post_count < 10:
            msg = f"⚠️ Low SEO page count: {post_count}. Run SEO bot."
            log_decision("LOW_SEO_PAGES", msg)
            send_telegram_alert(msg)
            subprocess.run(["python3", "seo_optimization_bot.py"])

    log_decision("CYCLE_END", "Decision engine cycle completed.")
    print("🧠 Decision engine cycle completed.\n")

if __name__ == "__main__":
    make_decisions()
