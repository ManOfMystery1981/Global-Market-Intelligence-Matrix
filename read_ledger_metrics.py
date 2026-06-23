import sqlite3
import datetime

def dump_all_ledger_records():
    print("\n=================== 📊 CORPORATE LEDGER INTERROGATION MATRIX ===================")
    conn = sqlite3.connect('corporate_ledger.db')
    cursor = conn.cursor()
    
    # 1. Print System Activity Logs (Latest 5)
    print("\n[📁 SYSTEM PROCESS RECONCILIATION LOGS - LATEST 5]")
    try:
        cursor.execute("SELECT id, timestamp, event_type, message FROM system_logs ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            time_str = datetime.datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d %H:%M:%S')
            print(f" ID: {row[0]} | Time: {time_str} | Type: {row[2]} | Info: {row[3]}")
    except sqlite3.OperationalError:
        print(" ⚠ system_logs table does not exist or hasn't initialized yet.")
        
    # 2. Print Marketing Ad Generation Logs (Latest 10)
    print("\n[🎯 AUTONOMOUS MARKETING ADVERTISING LOGS - LATEST 10]")
    try:
        cursor.execute("SELECT id, timestamp, keyword_targeted, output_file, status FROM marketing_ledger ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            time_str = datetime.datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d %H:%M:%S')
            print(f" ID: {row[0]} | Time: {time_str} | Target: #{row[2]} | Path: {row[3]} | Status: {row[4]}")
    except sqlite3.OperationalError:
        print(" ⚠ marketing_ledger table does not exist or hasn't initialized yet.")
        
    print("\n================================================================================\n")
    conn.close()

if __name__ == "__main__":
    dump_all_ledger_records()
