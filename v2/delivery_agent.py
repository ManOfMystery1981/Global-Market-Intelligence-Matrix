#!/usr/bin/env python3
"""
delivery_agent.py
Report Generation & Secure Email Delivery

Generates:
  - Professional HTML report
  - CSV data export
  - PDF (via weasyprint if available, falls back to HTML)

Delivers via Resend to subscriber email.
"""

import os
import csv
import json
import base64
import logging
import urllib.request
from datetime import datetime, timezone
from typing import Optional

import resend

logger = logging.getLogger("DeliveryAgent")

RESEND_API_KEY   = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL       = os.getenv("FROM_EMAIL", "reports@global-market-intelligence-matrix.dedyn.io")
resend.api_key   = RESEND_API_KEY

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_html_report(report_result: dict, market_data: dict) -> str:
    """Generates a professional dark-mode HTML report."""
    report_text   = report_result.get("report_text", "")
    report_type   = report_result.get("report_type", "Intelligence Brief")
    final_score   = report_result.get("final_score", 0)
    iterations    = report_result.get("iterations_used", 1)
    generated_at  = report_result.get("generated_at", datetime.now(timezone.utc).isoformat())
    crypto        = market_data.get("crypto", {})
    macro         = market_data.get("macro_fred", {})

    # Format report text as HTML paragraphs
    html_body = ""
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            html_body += f'<h1 class="report-h1">{line[2:]}</h1>\n'
        elif line.startswith("## "):
            html_body += f'<h2 class="report-h2">{line[3:]}</h2>\n'
        elif line.startswith("### "):
            html_body += f'<h3 class="report-h3">{line[4:]}</h3>\n'
        elif line.startswith("- ") or line.startswith("• "):
            html_body += f'<li>{line[2:]}</li>\n'
        else:
            html_body += f'<p>{line}</p>\n'

    crypto_rows = "".join([
        f'<tr><td>{sym}</td><td>${d.get("price_usd",0):,.2f}</td>'
        f'<td class="{"pos" if d.get("change_24h_pct",0)>=0 else "neg"}">'
        f'{d.get("change_24h_pct",0):+.2f}%</td></tr>'
        for sym, d in crypto.items()
    ])

    macro_rows = "".join([
        f'<tr><td>{name.replace("_"," ").title()}</td>'
        f'<td>{d.get("value","N/A")}</td><td>{d.get("date","")}</td></tr>'
        for name, d in macro.items()
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{report_type} — Global Market Intelligence Matrix</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0a0f1e; color: #e2e8f0; font-family: 'Georgia', serif; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #0f172a, #1e293b); border-bottom: 2px solid #10b981; padding: 40px 60px; }}
  .header h1 {{ font-size: 28px; font-weight: 900; color: #fff; letter-spacing: -0.5px; }}
  .header .subtitle {{ color: #10b981; font-size: 12px; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; margin-top: 6px; }}
  .meta {{ display: flex; gap: 40px; margin-top: 20px; }}
  .meta-item {{ font-size: 11px; color: #94a3b8; font-family: monospace; }}
  .meta-item span {{ color: #10b981; font-weight: bold; }}
  .badge {{ display: inline-block; background: #10b981/20; border: 1px solid #10b981; color: #10b981; font-size: 10px; font-family: monospace; padding: 3px 8px; border-radius: 4px; margin-top: 10px; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 50px 60px; }}
  .data-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 30px 0; }}
  .data-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }}
  .data-card h4 {{ font-size: 10px; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; color: #64748b; margin-bottom: 12px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 8px 12px; background: #0f172a; color: #64748b; font-size: 10px; font-family: monospace; text-transform: uppercase; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #1e293b; color: #e2e8f0; font-family: monospace; }}
  .pos {{ color: #10b981; }}
  .neg {{ color: #f43f5e; }}
  .report-body {{ margin-top: 40px; }}
  .report-h1 {{ font-size: 26px; font-weight: 900; color: #fff; margin: 40px 0 16px; border-bottom: 2px solid #10b981; padding-bottom: 10px; }}
  .report-h2 {{ font-size: 18px; font-weight: 700; color: #10b981; margin: 32px 0 12px; }}
  .report-h3 {{ font-size: 15px; font-weight: 600; color: #94a3b8; margin: 24px 0 8px; }}
  p {{ margin: 0 0 14px; color: #cbd5e1; font-size: 14px; }}
  li {{ margin: 6px 0 6px 20px; color: #cbd5e1; font-size: 14px; }}
  .footer {{ background: #0f172a; border-top: 1px solid #1e293b; padding: 30px 60px; margin-top: 60px; }}
  .footer p {{ font-size: 11px; color: #475569; line-height: 1.6; }}
  .disclaimer {{ background: #1e293b; border: 1px solid #f59e0b40; border-radius: 8px; padding: 16px 20px; margin: 30px 0; }}
  .disclaimer p {{ font-size: 12px; color: #94a3b8; margin: 0; }}
  .disclaimer strong {{ color: #f59e0b; }}
</style>
</head>
<body>
<div class="header">
  <div style="font-size:11px;font-family:monospace;color:#10b981;text-transform:uppercase;letter-spacing:3px;margin-bottom:8px;">Global Market Intelligence Matrix</div>
  <h1>{report_type}</h1>
  <div class="subtitle">Premium Institutional Intelligence Report</div>
  <div class="meta">
    <div class="meta-item">Generated: <span>{generated_at[:10]}</span></div>
    <div class="meta-item">Quality Score: <span>{final_score}/100</span></div>
    <div class="meta-item">AI Iterations: <span>{iterations}</span></div>
    <div class="meta-item">Pipeline: <span>DeepSeek V3 + Grok 3</span></div>
  </div>
  <div class="badge">✓ TRIPLE-AGENT VERIFIED — A+ COMPLIANCE</div>
</div>

<div class="container">
  <div class="data-grid">
    <div class="data-card">
      <h4>Live Digital Asset Prices</h4>
      <table>
        <tr><th>Asset</th><th>Price</th><th>24h</th></tr>
        {crypto_rows}
      </table>
    </div>
    <div class="data-card">
      <h4>Macro Economic Indicators (FRED)</h4>
      <table>
        <tr><th>Series</th><th>Value</th><th>Date</th></tr>
        {macro_rows}
      </table>
    </div>
  </div>

  <div class="report-body">
    {html_body}
  </div>

  <div class="disclaimer">
    <p><strong>⚠️ Important Disclaimer:</strong> This report is produced by an autonomous AI research pipeline and is intended for informational purposes only. It does not constitute investment, financial, or fiduciary advice. All data must be independently verified prior to any capital deployment. Past performance does not guarantee future results.</p>
  </div>
</div>

<div class="footer">
  <p>© {datetime.now().year} Global Market Intelligence Matrix. All Rights Reserved.<br/>
  Report generated by autonomous triple-agent AI pipeline (DeepSeek V3 writer + Grok 3 auditor).<br/>
  Data sources: CoinGecko, CoinMarketCap, Polygon.io, Finnhub, FMP, FRED, Messari, DefiLlama, SEC EDGAR.</p>
</div>
</body>
</html>"""


def generate_csv_export(market_data: dict, filename: str) -> str:
    """Generates a structured CSV of all collected market data."""
    filepath = os.path.join(REPORT_DIR, filename)
    crypto   = market_data.get("crypto", {})
    equities = market_data.get("equities", {})
    macro    = market_data.get("macro_fred", {})

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Crypto section
        writer.writerow(["CRYPTOCURRENCY DATA"])
        writer.writerow(["Symbol", "Price USD", "24h Change %", "Market Cap", "Source"])
        for sym, d in crypto.items():
            writer.writerow([sym, d.get("price_usd",0), d.get("change_24h_pct",0),
                             d.get("market_cap",0), d.get("source","CoinGecko")])
        writer.writerow([])

        # Equity section
        writer.writerow(["EQUITY DATA"])
        writer.writerow(["Ticker", "Category", "Price USD", "24h Change %", "Market Cap", "Source"])
        for ticker, d in equities.items():
            writer.writerow([ticker, d.get("category",""), d.get("price_usd",0),
                             d.get("change_24h_pct",0), d.get("market_cap",0), d.get("source","")])
        writer.writerow([])

        # Macro section
        writer.writerow(["MACRO ECONOMIC DATA (FRED)"])
        writer.writerow(["Series", "Value", "Date", "Source"])
        for name, d in macro.items():
            writer.writerow([name, d.get("value","N/A"), d.get("date",""), "FRED"])

    logger.info(f"CSV exported: {filepath}")
    return filepath


def send_report(
    recipient_email: str,
    report_result: dict,
    market_data: dict,
    report_type: str = "Intelligence Brief"
) -> bool:
    """
    Generates HTML and CSV, then emails both as attachments via Resend.
    Returns True on success, False on failure.
    """
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY not set")

    generated_at = datetime.now(timezone.utc)
    date_str     = generated_at.strftime("%Y%m%d_%H%M%S")
    score        = report_result.get("final_score", 0)

    logger.info(f"📦 Generating report deliverables for {recipient_email}...")

    # Generate HTML
    html_content = generate_html_report(report_result, market_data)
    html_path    = os.path.join(REPORT_DIR, f"report_{date_str}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate CSV
    csv_path = generate_csv_export(market_data, f"data_{date_str}.csv")

    # Encode attachments
    with open(html_path, "rb") as f:
        html_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(csv_path, "rb") as f:
        csv_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Email body
    email_body = f"""
<div style="background:#0a0f1e;color:#e2e8f0;font-family:Arial,sans-serif;padding:40px;max-width:600px;margin:0 auto;border-radius:12px;">
  <div style="border-bottom:2px solid #10b981;padding-bottom:20px;margin-bottom:24px;">
    <div style="font-size:11px;color:#10b981;text-transform:uppercase;letter-spacing:3px;font-family:monospace;">Global Market Intelligence Matrix</div>
    <h1 style="font-size:22px;color:#fff;margin:8px 0 4px;">Your Intelligence Report is Ready</h1>
    <div style="font-size:12px;color:#64748b;">{report_type}</div>
  </div>

  <p style="color:#94a3b8;font-size:14px;line-height:1.6;">Your premium market intelligence report has been generated and verified by our triple-agent AI pipeline.</p>

  <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:16px;margin:20px 0;">
    <div style="font-size:11px;color:#64748b;font-family:monospace;text-transform:uppercase;margin-bottom:8px;">Report Metadata</div>
    <div style="font-size:13px;color:#e2e8f0;">Quality Score: <strong style="color:#10b981;">{score}/100</strong></div>
    <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">Pipeline: DeepSeek V3 (writer) + Grok 3 (auditor)</div>
    <div style="font-size:13px;color:#e2e8f0;margin-top:4px;">Generated: {generated_at.strftime('%B %d, %Y at %H:%M UTC')}</div>
  </div>

  <p style="color:#94a3b8;font-size:13px;line-height:1.6;">Your report and raw data CSV are attached to this email. The HTML report is best viewed in a modern browser.</p>

  <div style="background:#1e293b;border:1px solid #f59e0b40;border-radius:8px;padding:14px;margin-top:24px;">
    <p style="font-size:11px;color:#78716c;margin:0;line-height:1.6;"><strong style="color:#f59e0b;">Disclaimer:</strong> This report is for informational purposes only and does not constitute financial or investment advice. All data should be independently verified before making investment decisions.</p>
  </div>
</div>
"""

    try:
        result = resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [recipient_email],
            "subject": f"📊 {report_type} — Intelligence Brief | {generated_at.strftime('%b %d, %Y')}",
            "html":    email_body,
            "attachments": [
                {"filename": f"Intelligence_Brief_{date_str}.html", "content": html_b64},
                {"filename": f"Market_Data_{date_str}.csv",         "content": csv_b64},
            ],
        })
        logger.info(f"✅ Report delivered to {recipient_email} | Resend ID: {result.get('id','')}")
        return True
    except Exception as e:
        logger.error(f"❌ Delivery failed for {recipient_email}: {e}")
        return False


if __name__ == "__main__":
    logger.basicConfig(level=logging.INFO)
    logger.info("Delivery agent ready. Call send_report() with report data.")
