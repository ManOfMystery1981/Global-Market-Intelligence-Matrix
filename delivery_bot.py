import os
import sys
import base64
import resend
import sqlite3
import uuid
import traceback
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- DATABASE LOGGING ---
def init_db():
    conn = sqlite3.connect('fulfillment_audit.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (id TEXT PRIMARY KEY, email TEXT, status TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_report(report_id, email, status):
    conn = sqlite3.connect('fulfillment_audit.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO reports VALUES (?, ?, ?, ?)", 
              (report_id, email, status, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# --- PDF GENERATION ENGINE ---
def generate_report_pdf(email, report_id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"GLOBAL INTELLIGENCE REPORT: {report_id}", styles['Title']),
        Spacer(1, 20),
        Paragraph(f"Prepared for: {email}", styles['Normal']),
        Spacer(1, 20),
        Paragraph("Institutional Grade Analysis completed successfully.", styles['Normal'])
    ]
    doc.build(story)
    return buffer.getvalue()

# --- DISPATCHER ---
def send_report_email(customer_email, pdf_data):
    resend.api_key = os.environ.get("RESEND_API_KEY")
    from_email = "Autonomous Data Refinery <delivery@global-market-intelligence-matrix.dedyn.io>"
    
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    params = {
        "from": from_email,
        "to": [customer_email],
        "subject": "📊 Institutional Intelligence Delivery",
        "html": "<p>Your requested market report is attached.</p>",
        "attachments": [{"filename": "Report.pdf", "content": pdf_base64}]
    }
    return resend.Emails.send(params)

# --- MAIN FULFILLMENT PIPELINE ---
def dispatch_secure_fulfillment_package(customer_email):
    report_id = str(uuid.uuid4())
    init_db()
    log_report(report_id, customer_email, "INITIATED")
    
    try:
        pdf_data = generate_report_pdf(customer_email, report_id)
        send_report_email(customer_email, pdf_data)
        log_report(report_id, customer_email, "DELIVERED")
        return True
    except Exception as e:
        print(f"Delivery failed: {e}")
        log_report(report_id, customer_email, f"FAILED: {str(e)}")
        return False
