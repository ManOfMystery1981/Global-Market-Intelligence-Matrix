import json
import http.client
import sys

sys.stdout.reconfigure(line_buffering=True)

def main():
    token = "8736368782:AAGDt398paOLnHHCDNtJAJFk6bx0moJtm84"
    chat_id = "8794514690"
    
    print("📣 Dispatching payload via raw HTTPS socket streams...")
    
    message_text = "<b>💰 CRITICAL BUSINESS REVENUE LOGGED 💰</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚙️ <b>Engine</b>: Autonomous Data Refinery\n💸 <b>Revenue Collected</b>: 0.01 SOL\n🟢 System Node Status: 100% Operational"
    
    # 1. Manually separate the network hostname from the request path layout
    # This prevents the socket engine from ever parsing a colon inside a host string
    host = "api.telegram.org"
    path = f"/bot{token}/sendMessage"
    
    payload = json.dumps({
        "chat_id": str(chat_id),
        "text": message_text,
        "parse_mode": "HTML"
    })
    
    headers = {
        "Content-Type": "application/json",
        "Connection": "close"
    }
    
    try:
        # 2. Establish a direct, raw HTTPS socket tunnel to the Telegram api cluster
        conn = http.client.HTTPSConnection(host, timeout=10)
        conn.request("POST", path, body=payload, headers=headers)
        
        response = conn.getresponse()
        res_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        if res_data.get("ok"):
            print("✅ SUCCESS: The raw socket matrix has broken through and hit your phone!")
        else:
            print(f"❌ Telegram API Rejected: {res_data}")
            
    except Exception as e:
        print(f"❌ Socket Layer Connection Failed: {e}")

if __name__ == "__main__":
    main()
