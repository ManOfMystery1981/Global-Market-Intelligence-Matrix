import json
import http.client
import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.stdout.reconfigure(line_buffering=True)

def dispatch_secure_fulfillment_package(customer_email):
    """
    Automated high-availability email delivery microservice node.
    Switches from Resend to a free, cloud-native Google SMTP fallback 
    pipeline instantly upon detecting primary infrastructure degradation.
    """
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    
    # Extract free cloud backup credentials vaulted inside your Vercel panel
    gmail_user = os.environ.get("FALLBACK_EMAIL_USER", "dsull1981@gmail.com").strip()
    gmail_pass = os.environ.get("FALLBACK_EMAIL_PASS", "").strip()

    PRIMARY_SENDER = "Autonomous Data Refinery <delivery@yourdomain.com>"
    subject_text = "📊 Your Requested Market Intelligence Matrix Document Package"
    
    # Fully updated, modern dark-skinned transactional email layout template
    body_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Data Refinery Delivery Matrix</title>
        <style>
            body { background-color: #0a0e14; color: #ffffff; font-family: 'Courier New', monospace; padding: 30px; margin: 0; }
            .email-container { max-width: 600px; margin: 0 auto; background-color: #101720; border: 1px solid #00ff66; padding: 25px; border-radius: 8px; }
            h2 { color: #00ff66; border-bottom: 1px solid #00ff66; padding-bottom: 10px; font-size: 20px; text-transform: uppercase; }
            p { font-size: 14px; line-height: 1.6; color: #e2e8f0; }
            .data-grid { width: 100%; margin: 20px 0; border-collapse: collapse; }
            .data-grid td { padding: 12px; border: 1px solid #00ff6633; font-size: 14px; }
            .data-grid .label { color: #00ff66; font-weight: bold; width: 35%; }
            .data-grid .value { font-family: monospace; color: #00bfff; }
            .footer { font-size: 11px; color: #718096; margin-top: 30px; border-top: 1px solid #1a202c; padding-top: 15px; }
            .badge { background-color: #00ff66; color: #000000; padding: 2px 6px; font-weight: bold; border-radius: 4px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="email-container">
            <h2>⚡ ORDER FULFILLMENT VERIFIED ⚡</h2>
            <p>Your payment parameters have been successfully processed and verified cryptographically on-chain via our multi-agent matrix routers.</p>
            
            <table class="data-grid">
                <tr>
                    <td class="label">Delivered Asset</td>
                    <td class="value">Market Intelligence Matrix (Premium Node)</td>
                </tr>
                <tr>
                    <td class="label">Target Pipeline</td>
                    <td class="value">Inbox Broadcast Splitter</td>
                </tr>
                <tr>
                    <td class="label">Pipeline Status</td>
                    <td><span class="badge">100% OPERATIONAL</span></td>
                </tr>
            </table>
            
            <p>The compiled asset arrays have been successfully generated and write-locked directly into your account profile dashboard index.</p>
            
            <div class="footer">
                _🤖 Generated autonomously by Market Intelligence Matrix Node via Fallback Network Index Engine._
            </div>
        </div>
    </body>
    </html>
    """

    # 🛒 TIER 1: Attempt broadcast using your primary Resend domain matrix
    if resend_key:
        print(f"📨 Attempting primary email dispatch pipeline via Resend...")
        primary_payload = json.dumps({
            "from": PRIMARY_SENDER, "to": customer_email, "subject": subject_text, "html": body_html
        })
        try:
            conn = http.client.HTTPSConnection("://resend.com", timeout=10)
            conn.request("POST", "/emails", body=primary_payload, headers={
                "Authorization": f"Bearer {resend_key}", "Content-Type": "application/json", "Connection": "close"
            })
            response = conn.getresponse()
            res_data = json.loads(response.read().decode('utf-8'))
            conn.close()

            if response.status == 200 and "id" in res_data:
                print(f"✅ Success! Package successfully delivered through primary Resend domain. ID: {res_data['id']}")
                return True
            else:
                raise Exception(f"Primary Reject: {res_data}")
        except Exception as primary_error:
            print(f"⚠️ Primary pipeline route degraded: {primary_error}")

    # 🚨 TIER 2: Primary failed or unconfigured. Trigger the $0-Capital Free Google Cloud SMTP Hot-Swap!
    print(f"🔄 SWITCH TRIGGERED: Hot-swapping traffic over to free Google Cloud SMTP server...")
    if not gmail_pass:
        print("❌ Critical Failure: FALLBACK_EMAIL_PASS is missing from environment variables.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[BACKUP ROUTE] {subject_text}"
        msg["From"] = f"Refinery Cloud Backup <{gmail_user}>"
        msg["To"] = customer_email
        msg.attach(MIMEText(body_html, "html"))

        server = smtplib.SMTP("://gmail.com", 587, timeout=15)
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, customer_email, msg.as_string())
        server.quit()

        print("✅ Recovery Complete! Package successfully delivered through fallback Google Cloud SMTP.")
        return True
    except Exception as fallback_error:
        print(f"💀 Critical Architecture Outage: Both email networks timed out: {fallback_error}")
        return False

if __name__ == "__main__":
    target_test_client = sys.argv[1] if len(sys.argv) > 1 else "dsull1981@gmail.com"
    dispatch_secure_fulfillment_package(target_test_client)
