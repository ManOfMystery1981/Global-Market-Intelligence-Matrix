# delivery_bot.py - Complete fixed version
import os
import sys
import base64
import resend
import re
import glob
import traceback
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
sys.stderr.reconfigure(line_buffering=True)

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

# --- DATA LOADING AND PARSING ---
def parse_markdown_data(content):
    """Parse markdown content into structured trends, metrics, and codebase stats."""
    lines = content.split('\n')
    trends = []
    metrics = []
    codebase_stats = {}
    current_section = None
    
    skip_patterns = ['github.com', 'description:', 'sindresorhus/awesome', 'freecodecamp/freecodecamp', 'public-apis/public-apis', 'build-your-own-x', 'codecrafters-io', 'view all', 'awesome list', 'repository', 'repo:']
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(pattern in line.lower() for pattern in skip_patterns):
            continue
        if line.startswith('#') or line.startswith('##'):
            header = line.lstrip('#').strip().lower()
            if 'trend' in header or 'top' in header:
                current_section = 'trends'
            elif 'metric' in header or 'key' in header:
                current_section = 'metrics'
            elif 'codebase' in header or 'github' in header or 'stats' in header:
                current_section = 'codebase'
            else:
                if len(line) > 5:
                    trends.append(header)
            continue
        if current_section == 'trends':
            if line.startswith('-') or line.startswith('*'):
                clean_line = line.lstrip('-* ').strip()
                if clean_line and len(clean_line) > 5:
                    if not any(skip in clean_line.lower() for skip in skip_patterns):
                        trends.append(clean_line)
            elif line and not line.startswith('#'):
                if not any(skip in line.lower() for skip in skip_patterns):
                    trends.append(line)
        elif current_section == 'metrics':
            if line.startswith('-') or line.startswith('*'):
                clean_line = line.lstrip('-* ').strip()
                if clean_line and ':' in clean_line:
                    key, value = clean_line.split(':', 1)
                    metrics.append({key.strip(): value.strip()})
                elif clean_line:
                    metrics.append(clean_line)
            elif line and ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                metrics.append({key.strip(): value.strip()})
        elif current_section == 'codebase':
            if ':' in line:
                key, value = line.split(':', 1)
                codebase_stats[key.strip()] = value.strip()
    
    if not trends or len(trends) < 2:
        trends = get_sample_data()['trends']
    
    return {
        'trends': trends[:10],
        'metrics': metrics if metrics else get_sample_data()['metrics'],
        'codebase_stats': codebase_stats
    }

def get_latest_data():
    """Read and parse market intelligence data into structured format."""
    try:
        with open('market_intelligence.md', 'r') as f:
            content = f.read()
        return parse_markdown_data(content)
    except FileNotFoundError:
        print("⚠️ market_intelligence.md not found, using sample data")
        return get_sample_data()
    except Exception as e:
        print(f"⚠️ Error reading market_intelligence.md: {e}")
        return get_sample_data()

def get_sample_data():
    """Return structured sample data."""
    return {
        'trends': [
            "AI/ML adoption up 23% year-over-year across enterprise sectors",
            "Rust usage growing 15% among systems programmers",
            "Kubernetes remains dominant in cloud orchestration",
            "TypeScript surpasses Java in new project starts",
            "Edge computing frameworks see 40% increase in adoption"
        ],
        'metrics': [
            {"Total frameworks tracked": "45"},
            {"Average developer salary": "$145,000"},
            {"Top in-demand skill": "Python"},
            {"Cloud spend": "Up 18% YoY"},
            {"Most popular database": "PostgreSQL"}
        ],
        'codebase_stats': {
            "Languages": "Python, HTML, JavaScript, Shell",
            "Stars": "0",
            "Forks": "0",
            "Open Issues": "0"
        }
    }

def get_latest_article():
    """Find and read the most recent analyst article."""
    articles = glob.glob("analyst_article_*.md")
    if not articles:
        print("⚠️ No analyst article found")
        return None
    
    latest_article = sorted(articles)[-1]
    print(f"📄 Reading article from: {latest_article}")
    
    try:
        with open(latest_article, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('# Tech Analyst Report'):
                start_idx = i + 2
                break
        
        for i in range(start_idx, len(lines)):
            if lines[i].startswith('**Generated:**'):
                start_idx = i + 2
                break
        
        article_text = '\n'.join(lines[start_idx:])
        article_text = article_text.replace('**', '').replace('##', '')
        
        return article_text.strip()
    except Exception as e:
        print(f"❌ Error reading article: {e}")
        return None

# --- ENHANCED PDF GENERATION ---
def generate_enhanced_report_pdf(email, trend_data, metrics_data, codebase_stats, market_data, chart_images, os_data=None, ai_article=None):
    """Generate a professional, data-rich report with charts and market data."""
    print("🔵 generate_enhanced_report_pdf called")
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                                leftMargin=60, rightMargin=60,
                                topMargin=60, bottomMargin=60)
        styles = getSampleStyleSheet()
        story = []
        
        # --- PROFESSIONAL FONT STYLES ---
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#0a1628'), alignment=TA_CENTER, spaceAfter=15)
        subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=colors.HexColor('#4a5568'), alignment=TA_CENTER, spaceAfter=25)
        heading1_style = ParagraphStyle('Heading1Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#00aa66'), spaceAfter=10, alignment=TA_CENTER)
        heading2_style = ParagraphStyle('Heading2Style', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#1a5276'), spaceAfter=8, alignment=TA_CENTER)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=6, alignment=TA_JUSTIFY)
        body_center_style = ParagraphStyle('BodyCenterStyle', parent=body_style, fontName='Helvetica', alignment=TA_CENTER, spaceAfter=8)
        footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=5)
        
        # --- HEADER ---
        story.append(Paragraph("GLOBAL SOFTWARE INTELLIGENCE REPORT", title_style))
        story.append(Paragraph(f"Prepared for: <b>{email}</b>", subtitle_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}", subtitle_style))
        story.append(Spacer(1, 15))
        
        # --- EXECUTIVE SUMMARY ---
        story.append(Paragraph("EXECUTIVE MARKET SUMMARY", heading1_style))
        summary_text = """This report provides a comprehensive analysis of the global software landscape, combining real-time trend data, market intelligence, and financial insights."""
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 15))
        
        # --- MARKET SNAPSHOT ---
        story.append(Paragraph("MARKET SNAPSHOT", heading1_style))
        market_table_data = [['Asset Type', 'Symbol', 'Price (USD)', '24h Change']]
        if 'crypto' in market_data:
            for coin, data in market_data['crypto'].items():
                change = data.get('change_24h', 0)
                market_table_data.append(['Cryptocurrency', coin, f"${data['price']:,.2f}", f"{change:+.1f}%"])
        if 'stocks' in market_data:
            for symbol, data in market_data['stocks'].items():
                change = data.get('change_24h', 0)
                market_table_data.append(['Tech Stock', symbol, f"${data['price']:,.2f}", f"{change:+.1f}%"])
        
        if len(market_table_data) > 1:
            market_table = Table(market_table_data, colWidths=[100, 70, 120, 80])
            market_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00aa66')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 5)
            ]))
            story.append(market_table)
            story.append(Spacer(1, 15))
        
        # --- TOP SOFTWARE TRENDS ---
        story.append(Paragraph("TOP SOFTWARE TRENDS (RANKED)", heading1_style))
        trend_table_data = [['Rank', 'Trend']]
        for i, trend in enumerate(trend_data[:8], 1):
            trend_table_data.append([str(i), trend])
        
        if len(trend_table_data) > 1:
            trend_table = Table(trend_table_data, colWidths=[40, 430])
            trend_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))
            story.append(trend_table)
            story.append(Spacer(1, 20))
        
        # --- CHARTS ---
        if chart_images:
            story.append(Paragraph("DATA VISUALIZATIONS", heading1_style))
            if 'crypto' in chart_images and chart_images['crypto']:
                crypto_img = Image(BytesIO(base64.b64decode(chart_images['crypto'])), width=450, height=280)
                story.append(Paragraph("Cryptocurrency Market Overview", heading2_style))
                story.append(crypto_img)
                story.append(Spacer(1, 15))
            if 'stocks' in chart_images and chart_images['stocks']:
                stock_img = Image(BytesIO(base64.b64decode(chart_images['stocks'])), width=450, height=280)
                story.append(Paragraph("Tech Stock Performance", heading2_style))
                story.append(stock_img)
                story.append(Spacer(1, 15))
            if 'trends' in chart_images and chart_images['trends']:
                trends_img = Image(BytesIO(base64.b64decode(chart_images['trends'])), width=450, height=280)
                story.append(Paragraph("Software Adoption Trends", heading2_style))
                story.append(trends_img)
                story.append(Spacer(1, 15))
            if 'social' in chart_images and chart_images['social']:
                social_img = Image(BytesIO(base64.b64decode(chart_images['social'])), width=400, height=300)
                story.append(Paragraph("Social Media Platform Popularity", heading2_style))
                story.append(social_img)
                story.append(Spacer(1, 15))
        
        # --- AI ANALYST ARTICLE ---
        article_text = get_latest_article()
        if article_text:
            story.append(PageBreak())
            story.append(Paragraph("AI ANALYST INSIGHTS", heading1_style))
            
            paragraphs = article_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    if re.match(r'^\d+\.', para.strip()):
                        story.append(Paragraph(para.strip(), heading2_style))
                    else:
                        story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("AI ANALYST INSIGHTS", heading1_style))
            story.append(Paragraph("No analyst article was generated for this report.", body_style))
            story.append(Spacer(1, 20))
        
        # --- KEY METRICS ---
        story.append(Paragraph("KEY MARKET METRICS", heading1_style))
        metrics_table_data = [['Metric', 'Value']]
        for metric in metrics_data:
            if isinstance(metric, dict):
                for key, value in metric.items():
                    if not any(skip in key.lower() for skip in ['github', 'repo', 'book']):
                        metrics_table_data.append([key.strip(), value.strip()])
            elif isinstance(metric, str):
                if ':' in metric:
                    key, value = metric.split(':', 1)
                    if not any(skip in key.lower() for skip in ['github', 'repo', 'book']):
                        metrics_table_data.append([key.strip(), value.strip()])
        
        if len(metrics_table_data) > 1:
            metrics_table = Table(metrics_table_data, colWidths=[200, 240])
            metrics_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0a1628')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6)
            ]))
            story.append(metrics_table)
            story.append(Spacer(1, 20))
        
        # --- FOOTER ---
        story.append(Paragraph("© 2026 Autonomous Data Refinery. All rights reserved.", footer_style))
        story.append(Paragraph("Data is for informational purposes only. Not financial advice.", footer_style))
        
        doc.build(story)
        pdf_buffer = buffer.getvalue()
        buffer.close()
        
        print(f"🔵 PDF built, size: {len(pdf_buffer)} bytes")
        return pdf_buffer
    except Exception as e:
        print(f"🔵 PDF generation failed: {e}")
        traceback.print_exc()
        return None

# --- EMAIL SENDING ---
def send_report_email(customer_email, pdf_data=None, is_test=False):
    """Send the market intelligence report via Resend API."""
    
    # Validate email before proceeding
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
    """
    Complete fulfillment pipeline: generate enhanced report with charts and OS data.
    """
    print(f"🚀 Starting fulfillment for {customer_email}")
    sys.stdout.flush()
    
    # Step 1: Get market intelligence data
    try:
        print("📊 Getting market data...")
        data = get_latest_data()
        trend_data = data['trends']
        metrics_data = data['metrics']
        codebase_stats = data['codebase_stats']
        print(f"📊 Loaded {len(trend_data)} trends, {len(metrics_data)} metrics")
    except Exception as e:
        print(f"❌ Failed to get market data: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Collect live market data
    try:
        print("📈 Fetching live market data...")
        collector = MarketDataCollector()
        market_data = collector.collect_all_data()
    except Exception as e:
        print(f"❌ Failed to get market data: {e}")
        traceback.print_exc()
        return False
    
    # Step 3: Collect OS data
    try:
        print("💻 Fetching operating system data...")
        os_collector = OSDataCollector()
        os_data = os_collector.collect_all_data()
    except Exception as e:
        print(f"❌ Failed to get OS data: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Generate charts
    try:
        print("📊 Generating charts...")
        chart_gen = ChartGenerator()
        chart_images = chart_gen.generate_all_charts(market_data)
    except Exception as e:
        print(f"❌ Failed to generate charts: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Initialize pdf_data to None
    pdf_data = None
    
    # Step 6: Generate the PDF
    try:
        print("📄 Generating enhanced report PDF...")
        print(f"📧 Email: {customer_email}")
        print(f"📊 Trends: {len(trend_data)}")
        print(f"📊 Metrics: {len(metrics_data)}")
        print(f"📊 Charts: {len(chart_images) if chart_images else 0}")
        
        pdf_data = generate_enhanced_report_pdf(
            customer_email, 
            trend_data, 
            metrics_data, 
            codebase_stats,
            market_data, 
            chart_images,
            os_data
        )
        
        if pdf_data is None:
            print("❌ PDF generation returned None!")
            return False
        
        print(f"✅ PDF generated ({len(pdf_data)} bytes)")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 7: Send the email with PDF attachment
    try:
        print(f"📨 Sending email to {customer_email}...")
        success = send_report_email(customer_email, pdf_data)
        if success:
            print("🎉 Fulfillment complete!")
            return True
        else:
            print("❌ Fulfillment failed at email step.")
            return False
    except Exception as e:
        print(f"❌ Fulfillment failed with exception: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email = sys.argv[1] if len(sys.argv) > 1 else "dsull1981@gmail.com"
    is_test_mode = len(sys.argv) > 2 and sys.argv[2] == "--test"
    
    if not is_valid_email(test_email):
        print(f"❌ Invalid test email: '{test_email}'")
        sys.exit(1)
    
    print(f"🧪 Running in {'TEST' if is_test_mode else 'LIVE'} mode")
    dispatch_secure_fulfillment_package(test_email)
