import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler

sys.stdout.reconfigure(line_buffering=True)

def escape_html(text_string):
    return str(text_string).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Pull raw tokens dynamically out of Vercel's environment matrix
        raw_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip().replace('"', '').replace("'", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip().replace('"', '').replace("'", "")
        
        telegram_status = "SKIPPED_OR_MISSING_KEYS"
        error_logs = "None"
        signature = "fallback_cloud_sig"
        
        try:
            payload = json.loads(post_data)
            meta_data = payload.get("metaData", {})
            
            customer_email = escape_html(meta_data.get("customerEmail") or payload.get("customerEmail", "unknown_buyer@internal.com"))
            amount_sol = escape_html(payload.get("amount") or payload.get("totalAmount", 0.01))
            signature = escape_html(payload.get("signature") or payload.get("transactionId", "fallback_cloud_sig"))
            
            if raw_token and chat_id:
                # Absolute, bulletproof token sanitization logic block
                clean_token = raw_token
                
                # If the user put "bot" at the start of the environment variable, drop it
                if clean_token.lower().startswith("bot"):
                    clean_token = clean_token[3:]
                
                # Clean out any accidental recursive "bot" strings before or after colons
                if ":" in clean_token:
                    parts = clean_token.split(":")
                    prefix = parts[0].lower().replace("bot", "").strip()
                    suffix = parts[1].lower().replace("bot", "").strip()
                    # Rebuild the token using the actual case-preserved original string characters
                    clean_token = f"{raw_token.split(':')[0]}..{raw_token.split(':')[1]}".replace("bot", "").replace("BOT", "").replace("..", ":").strip()

                message_text = f"<b>💰 CRITICAL BUSINESS REVENUE LOGGED 💰</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚙️ <b>Engine</b>: Autonomous Data Refinery\n📊 <b>Asset Purchased</b>: Market Intelligence Matrix\n💸 <b>Revenue Collected</b>: {amount_sol} SOL\n📨 <b>Delivery Pipeline</b>: Dispatched to Inbox\n📧 <b>Target Client</b>: <code>{customer_email}</code>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n<i>🟢 System Node Status: 100% Operational</i>"
                
                # Assemble the url link parameters
                url = f"https://telegram.org{clean_token}/sendMessage"
                api_payload = json.dumps({
                    "chat_id": str(chat_id),
                    "text": message_text,
                    "parse_mode": "HTML"
                }).encode('utf-8')
                
                req = urllib.request.Request(url, data=api_payload, headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        res_data = json.loads(response.read().decode('utf-8'))
                        if res_data.get("ok"):
                            telegram_status = "SUCCESSFULLY_DELIVERED"
                        else:
                            telegram_status = f"TELEGRAM_REJECTED: {res_data}"
                except urllib.error.HTTPError as he:
                    telegram_status = f"HTTP_ERROR_{he.code}"
                    error_logs = he.read().decode('utf-8')
                except Exception as net_err:
                    telegram_status = "NETWORK_CONNECTION_DROPPED"
                    error_logs = str(net_err)
            else:
                telegram_status = "MISSING_ENV_VARIABLES_ON_VERCEL"
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response_data = {
                "status": "PROCESSED",
                "signature_logged": signature,
                "telegram_delivery_status": telegram_status,
                "api_error_response_details": error_logs
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "CRASHED", "details": str(e)}).encode('utf-8'))
            return
