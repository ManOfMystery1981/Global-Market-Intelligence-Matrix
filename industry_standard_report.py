import csv
import os

class IndustryStandardReport:
    """
    Visualization Core: Compiles dense tabular datasets alongside 
    responsive, dark-mode terminal interfaces embedded with inline vector charts.
    """
    def generate_report(self, playbook, expert_narrative):
        csv_filename = "macro_alpha_dataset.csv"
        csv_fields = ["ticker", "category", "price", "trend", "conviction_score", "z_score", "probability_pct", "kelly_fraction_pct"]
        
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()
                for p in playbook:
                    row_data = {
                        "ticker": p.get("ticker"), "category": p.get("category"),
                        "price": f"{p.get('price'):.2f}", "trend": p.get("trend"),
                        "conviction_score": str(p.get("conviction_score")), "z_score": f"{p.get('z_score', 0.0):.2f}",
                        "probability_pct": f"{p.get('probability_pct', 50.0):.1f}",
                        "kelly_fraction_pct": f"{p.get('kelly_fraction_pct', 0.0):.1f}"
                    }
                    writer.writerow(row_data)
        except Exception as e:
            print(f"Error generating CSV: {e}")

        rows = ""
        for p in playbook:
            badge_style = "background:#10b981; color:#0f172a;" if p['trend'] == "EXTREME_ANOMALY" else "background:#475569; color:#cbd5e1;"
            rows += f"""
            <tr style='border-bottom: 1px solid #334155;'>
                <td style='padding:12px;'><strong>{p['ticker']}</strong></td>
                <td style='padding:12px;'>{p['category'].replace('_',' ')}</td>
                <td style='padding:12px;'>${p['price']:,.2f}</td>
                <td style='padding:12px;'><span style='padding:3px 6px; border-radius:4px; font-weight:bold; font-size:11px; {badge_style}'>{p['trend']}</span></td>
                <td style='padding:12px; color:#38bdf8;'><code>{p['z_score']:+.2f}</code></td>
                <td style='padding:12px;'><strong>{p['conviction_score']}/100</strong></td>
                <td style='padding:12px; color:#10b981;'>{p['probability_pct']:.1f}%</td>
                <td style='padding:12px; font-size:12px; color:#94a3b8;'>{p['source']}</td>
            </tr>
            """

        svg_charts = self._compile_vector_visuals(playbook[:4])

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>AI Infrastructure Market Intelligence Playbook</title>
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
                hr {{ border: 0; height: 1px; background: #334155; margin: 30px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏛️ AI INFRASTRUCTURE MARKET INTELLIGENCE MATRIX</h1>
                
                {expert_narrative}
                
                <h2>📊 Statistical Divergence Distributions</h2>
                <div class="visual-grid">
                    {svg_charts}
                </div>

                <h2>📋 Tactical Multi-Factor Ledger</h2>
                <table>
                    <tr style='background:#0f172a;'>
                        <th>Asset Key</th><th>Niche Category</th><th>Spot Price</th><th>Signal Status</th>
                        <th>Z-Divergence</th><th>Signal Intensity</th><th>Signal Confidence</th><th>Audit Source</th>
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
            z = abs(a.get('z_score', 1.0))
            height = min(int(z * 22), 75)
            color = "#10b981" if a['trend'] == "EXTREME_ANOMALY" else "#38bdf8"
            
            svg_blocks += f"""
            <div class="chart-box">
                <span style='font-size:12px; font-weight:bold; color:#f1f5f9;'>{a['ticker']} Anomaly Curve</span>
                <svg width="220" height="90" style="background:#090d16; border-radius:4px; margin-top:10px;">
                    <path d="M10 80 Q 60 {100 - height}, 110 {90 - height} T 210 80" fill="none" stroke="{color}" stroke-width="3"/>
                    <line x1="10" y1="80" x2="210" y2="80" stroke="#334155" stroke-dasharray="3"/>
                    <circle cx="110" cy="{90 - height}" r="4" fill="#f43f5e"/>
                    <text x="12" y="22" fill="#64748b" font-size="9" font-family="monospace">Intensity: {a['conviction_score']}/100</text>
                </svg>
            </div>
            """
        return svg_blocks
