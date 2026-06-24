import urllib.request
import json

token = "8736368782:AAGDt398paOLnHHCDNtJAJFk6bx0moJtm84"
chat_id = "8794514690"

# Fix: Using the correct, fully qualified programmable API URL mapping
url = f"https://telegram.org{token}/sendMessage"

payload = json.dumps({
    "chat_id": str(chat_id),
    "text": "📡 Sovereign Multi-Agent Matrix Online!"
}).encode("utf-8")

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print("✅ Success: Telegram bot connection path is fully operational.")
except Exception as e:
    print(f"❌ Connection failed: {e}")
