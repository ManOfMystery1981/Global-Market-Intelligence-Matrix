#!/usr/bin/env python3
import csv
import os

class IndustryStandardReport:
    """
    Visualization Core: Compiles dense tabular datasets alongside 
    responsive, dark-mode terminal interfaces embedded with inline vector charts.
    """
    def generate_report(self, playbook, expert_narrative):
        csv_filename = "market_anomaly_dataset.csv"
        csv_fields = ["ticker", "category", "price", "trend", "composite_signal_score", "z_score"]
        
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()
                for p in playbook:
                    metrics_block = p.get("metrics", {})
                    
                    row_data = {
                        "ticker": p.get("asset", "UNKNOWN"),
                        "category": metrics_block.get("category", "AI Infrastructure"),
                        "price": f"{metrics_block.get('price', 0.0):.2f}",
                        "trend": p.get("classification", "NOMINAL_VARIANCE"),
                        "composite_signal_score": f"{p.get('composite_score', 0.0):.1f}",
                        "z_score": f"{metrics_block.get('z_score', 0.0):.2f}"
                    }
                    writer.writerow(row_data)
            print(f"✅ Quantitative CSV Dataset Exported: {csv_filename}")
        except Exception as e:
            print(f"Error generating CSV: {e}")

        rows = ""
        for p in playbook:
            metrics_block = p.get("metrics", {})
            ticker = p.get("asset", "UNKNOWN")
            category = metrics_block.get("category", "AI Infrastructure").replace('_', ' ')
            price = metrics_block.get("price", 0.0)
            trend_label = p.get("classification", "NOMINAL_VARIANCE")
            conviction = p.get("composite_score", 0.0)
            z_score = metrics_block.get("z_score", 0.0)
            confidence_band = p.get("confidence_band", "Low")
            source_name = metrics_block.get("source", "Public API Endpoint")
            
            badge_style = "background:#10b981; color:#0f172a;" if "Very Strong" in trend_label or "Strong" in trend_label else "background:#475569; color:#cbd5e1;"
            
            rows += f"""
            <tr style='border-bottom: 1px solid #334155;'>
                <td style='padding:12px;'><strong>{ticker}</strong></td>
                <td style='padding:12px;'>{category}</td>
                <td style='padding:12px;'>${price:,.2f}</td>
                <td style='padding:12px;'><span style='padding:3px 6px; border-radius:4px; font-weight:bold; font-size:11px; {badge_style}'>{trend_label}</span></td>
                <td style='padding:12px; color:#38bdf8;'><code>{z_score:+.2f}</code></td>
                <td style='padding:12px;'><strong>{conviction:.1f}/100</strong></td>
                <td style='padding:12px; color:#10b981;'>{confidence_band}</td>
                <td style='padding:12px; font-size:12px; color:#64748b;'>{source_name}</td>
            </tr>
            """

        svg_charts = self._compile_vector_visuals(playbook[:4])

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Cross-Asset Anomaly Research Brief</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; margin: 0; line-height: 1.6; }}
                .container {{ max-width: 1200px; margin: auto; background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }}
                h1 {{ font-size: 26px; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-top: 0; color: #f1f5f9; }}
                h2 {{ font-size: 16px; color: #38bdf8; text-transform: uppercase; margin-top: 30px; letter-spacing: 1px; }}
                h3 {{ font-size: 15px; color: #e2e8f0; border-left: 3px solid #38bdf8; padding-left: 10px; margin-top: 25px; }}
                .visual-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin: 20px 0; }}
                .chart-box {{ background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left; font-size: 13px; }}
                th {{ padding: 12px; background: #0f172a; color: #94a3b8; font-size: 11px; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏛️ MARKET ANOMALY RESEARCH BRIEF</h1>
                {expert_narrative}
                <h2>📊 Statistical Divergence Distributions</h2>
                <div class="visual-grid">{svg_charts}</div>
                <h2>📋 Anomaly Research Ledger</h2>
                <table>
                    <tr style='background:#0f172a;'>
                        <th>Asset Key</th><th>Niche Category</th><th>Spot Price</th><th>Research Status</th>
                        <th>Z-Divergence</th><th>Signal Intensity</th><th>Confidence Band</th><th>Audit Source</th>
                    </tr>
                    {rows}
                </table>
            </div>
        </body>
        </html>
        """
        
        html_filename = "playbook.html"
        with open(html_filename, "w", encoding='utf-8') as f:
            f.write(html_template)
            
        return html_filename, csv_filename

    def _compile_vector_visuals(self, target_assets):
        svg_blocks = ""
        for a in target_assets:
            metrics_block = a.get("metrics", {})
            ticker = a.get("asset", "UNKNOWN")
            conviction = a.get("composite_score", 0.0)
            z = abs(metrics_block.get('z_score', 1.0))
            height = min(int(z * 22), 75)
            
            svg_blocks += f"""
            <div class="chart-box">
                <span style='font-size:12px; font-weight:bold; color:#f1f5f9;'>{ticker} Anomaly Curve</span>
                <svg width="220" height="90" style="background:#090d16; border-radius:4px; margin-top:10px;">
                    <path d="M10 80 Q 60 {100 - height}, 110 {90 - height} T 210 80" fill="none" stroke="#38bdf8" stroke-width="3"/>
                    <line x1="10" y1="80" x2="210" y2="80" stroke="#334155" stroke-dasharray="3"/>
                    <circle cx="110" cy="{90 - height}" r="4" fill="#f43f5e"/>
                    <text x="12" y="22" fill="#64748b" font-size="9" font-family="monospace">Intensity: {conviction:.1f}/100</text>
                </svg>
            </div>
            """
        return svg_blocks
