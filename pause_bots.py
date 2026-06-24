#!/usr/bin/env python3
"""
pause_bots.py - Pause non-essential bots when resources are low.
"""

import os
import time
import sqlite3

def log_event(message):
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_logs (timestamp, event_type, message) VALUES (?, ?, ?)",
            (int(time.time()), "BOT_PAUSE", message)
        )
        conn.commit()
        conn.close()
        print(f"📝 Logged: {message}")
    except Exception as e:
        print(f"⚠️ Logging failed: {e}")

def pause_bots():
    try:
        with open('.pause_bots', 'w') as f:
            f.write(f'Paused at {time.ctime()}\nReason: Low SOL balance\n')
        log_event("Non-essential bots paused due to low SOL balance.")
        print("✅ Bots paused. Add funds and run 'python3 pause_bots.py unpause' to resume.")
    except Exception as e:
        print(f"❌ Failed to pause bots: {e}")

def unpause_bots():
    try:
        if os.path.exists('.pause_bots'):
            os.remove('.pause_bots')
            log_event("Bots unpaused.")
            print("✅ Bots unpaused.")
        else:
            print("ℹ️ Bots were not paused.")
    except Exception as e:
        print(f"❌ Failed to unpause bots: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "unpause":
        unpause_bots()
    else:
        pause_bots()
