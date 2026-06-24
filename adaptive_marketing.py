#!/usr/bin/env python3
"""
adaptive_marketing.py - Adjusts marketing strategy based on performance.
"""

import sqlite3
import time
import subprocess

def get_top_performing_keywords():
    """Query marketing_ledger for keywords that generated sales."""
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT keyword_targeted, COUNT(*) FROM marketing_ledger WHERE status = 'SALE' GROUP BY keyword_targeted ORDER BY COUNT(*) DESC LIMIT 3"
        )
        results = cursor.fetchall()
        conn.close()
        return [row[0] for row in results] if results else ["SolanaEngine", "DataArbitrage", "MultiAgentSys"]
    except Exception as e:
        print(f"⚠️ Keyword query failed: {e}")
        return ["SolanaEngine", "DataArbitrage", "MultiAgentSys"]

def adjust_marketing():
    """Adjust marketing bot based on performance."""
    top_keywords = get_top_performing_keywords()
    print(f"📊 Top performing keywords: {top_keywords}")
    
    try:
        conn = sqlite3.connect('corporate_ledger.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO system_logs (timestamp, event_type, message) VALUES (?, ?, ?)",
            (int(time.time()), "MARKETING_ADJUST", f"Adjusted to keywords: {', '.join(top_keywords)}")
        )
        conn.commit()
        conn.close()
        print("✅ Marketing adjustment logged.")
    except Exception as e:
        print(f"⚠️ Adjustment logging failed: {e}")

if __name__ == "__main__":
    adjust_marketing()
