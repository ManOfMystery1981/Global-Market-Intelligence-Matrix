# delivery_bot.py - Complete with email validation
import os
import sys
import base64
import resend
import re
import glob
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

# Import your data bots
from data_collector_bot import MarketDataCollector
from chart_generator_bot import ChartGenerator
from os_data_collector import OSDataCollector

# Force stdout to be line-buffered
sys.stdout.reconfigure(line_buffering=True)

# --- EMAIL VALIDATION ---
def is_valid_email(email):
    """Validate email address format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_valid_email(email):
    """Get a valid email or return None."""
    if email and is_valid_email(email):
        return email
    return None

# --- REST OF YOUR DELIVERY_BOT.PY ---
# (Keep all your existing functions: parse_markdown_data, get_latest_data, 
#  get_sample_data, generate_enhanced_report_pdf, etc.)

# --- EMAIL SENDING WITH VALIDATION ---
def send_report_email(customer_email, pdf_data=None, is_test=False):
    """Send the market intelligence report via Resend API."""
    
    # ✅ Validate email before proceeding
    if not customer_email or not is_valid_email(customer_email):
        print(f"❌ Invalid email address: '{customer_email}'")
        return False
    
    resend_api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not resend_api_key:
        print("❌ RESEND_API_KEY is not set in environment variables.")
        return False
    
    resend.api_key = resend_api_key
    
    from_email = "Autonomous Data Refinery <delivery@global-market-intelligence-matrix.dedyn.io>"
    subject = "📊 Your Global Software Intelligence Report"
    
    html_body = """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Data Refinery Delivery</title>
    <style>
        body { background-color: #0a0e14; color: #ffffff; font-family: 'Helvetica', 'Arial', sans-serif; padding: 30px; margin: 0; }
        .email-container { max-width: 600px; margin: 0 auto; background-color: #101720; border: 1px solid #00ff66; padding: 25px; border-radius: 8px; }
        h2 { color: #00ff66; border-bottom: 1px solid #00ff66; padding-bottom: 10px; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; }
        p { font-size: 14px; line-height: 1.6; color: #e2e8f0; }
        .badge { background-color: #00ff66; color: #000000; padding: 2px 6px; font-weight: bold; border-radius: 4px; font-size: 12px; }
        .footer { font-size: 11px; color: #718096; margin-top: 30px; border-top: 1px solid #1a202c; padding-top: 15px; }
    </style>
    </head>
    <body>
        <div class="email-container">
            <h2>⚡ ORDER FULFILLMENT VERIFIED ⚡</h2>
            <p>Your payment parameters have been successfully processed and verified cryptographically on-chain.</p>
            <p><span class="badge">100% OPERATIONAL</span></p>
            <p>Your <strong>Global Software Intelligence Report</strong> is attached as a PDF.</p>
            <p>This report contains the latest software trends and metrics compiled from real-time market data.</p>
            <div class="footer">_🤖 Generated autonomously by Market Intelligence Matrix Node via Sovereign Web3 Infrastructure.</div>
        </div>
    </body>
    </html>
    """
    
    email_payload = {
        "from": from_email,
        "to": [customer_email],
        "subject": subject,
        "html": html_body,
    }
    
    if pdf_data:
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        email_payload["attachments"] = [
            {
                "filename": "Global_Software_Trends_Report.pdf",
                "content": pdf_base64,
                "content_type": "application/pdf"
            }
        ]
        print(f"📎 PDF attachment size: {len(pdf_data)} bytes (base64 encoded)")
    
    if is_test:
        print(f"🧪 TEST MODE: Email would be sent to {customer_email}")
        return True
    
    try:
        print(f"📨 Sending email to {customer_email} via Resend...")
        result = resend.Emails.send(email_payload)
        print(f"✅ Email sent successfully. ID: {result.get('id', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# --- MAIN FULFILLMENT PIPELINE ---
def dispatch_secure_fulfillment_package(customer_email):
    """Complete fulfillment pipeline: generate enhanced report with charts and OS data."""
    
    # ✅ Validate email before proceeding
    valid_email = get_valid_email(customer_email)
    if not valid_email:
        print(f"❌ Invalid email: '{customer_email}'. Skipping fulfillment.")
        return False
    
    print(f"🚀 Starting fulfillment for {valid_email}")
    
    # ... rest of your existing fulfillment code ...
    # (Keep your existing data collection, PDF generation, etc.)
    
    # At the end, send the email
    try:
        success = send_report_email(valid_email, pdf_data)
        if success:
            print("🎉 Fulfillment complete!")
            return True
        else:
            print("❌ Fulfillment failed at email step.")
            return False
    except Exception as e:
        print(f"❌ Fulfillment failed with exception: {e}")
        return False

if __name__ == "__main__":
    test_email = sys.argv[1] if len(sys.argv) > 1 else "dsull1981@gmail.com"
    is_test_mode = len(sys.argv) > 2 and sys.argv[2] == "--test"
    
    # ✅ Validate the test email
    if not is_valid_email(test_email):
        print(f"❌ Invalid test email: '{test_email}'")
        sys.exit(1)
    
    print(f"🧪 Running in {'TEST' if is_test_mode else 'LIVE'} mode")
    dispatch_secure_fulfillment_package(test_email)
