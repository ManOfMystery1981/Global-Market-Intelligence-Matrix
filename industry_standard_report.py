import csv
import math

class IndustryStandardReport:
    """
    Institutional Engine: Compiles dense tabular datasets alongside 
    mathematical predictive models and dynamic vector SVG charts.
    """
    def generate_report(self, playbook, expert_narrative):
        # 1. Output the raw CSV data for backtesting
        csv_filename = "macro_alpha_dataset.csv"
        csv_fields = ["ticker", "category", "price", "trend", "narrative", "z_score", "probability_pct", "kelly_fraction_pct"]
        
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()
                for p in playbook:
                    # Filter matching output parameters
                    row_data = {k: p.get(k, "0") for k in csv_fields[:5]}
                    row_data["z_score"] = f"{p.get('z_score', 0.0):.2f}"
                    row_data["probability_pct"] = f"{p.get('probability_pct', 50.0):.1f}%"
                    row_data["kelly_fraction_pct"] = f"{p.get('kelly_fraction_pct', 0.0):.1f}%"
                    writer.writerow(row_data)
            print(f"✅ Quantitative CSV Dataset Exported: {csv_filename}")
        except Exception as e:
            print(f"Error generating CSV: {e}")

        # 2. Build High-Density Visual Table Rows with Predictive Math Metrics
        rows = ""
        for p in playbook:
            badge_class = "breakout" if p['trend'] == "BREAKOUT" else "stable"
            rows += f"""
            <tr class='{badge_class}'>
                <td><strong>{p['ticker']}</strong></td>
                <td>{p['category'].replace('_',' ')}</td>
                <td>${p['price']:,.2f}</td>
                <td><span class='badge badge-{badge_class}'>{p['trend']}</span></td>
                <td><code>Z = {p['z_score']:+.2f}</code></td>
                <td><strong>{p['probability_pct']:.1f}%</strong></td>
                <td style='color: #10b981;'>{p['kelly_fraction_pct']:.1f}%</td>
                <td class='narrative'>{p['narrative']}</td>
            </tr>
            """

        # 3. Compile Programmatic SVG Volatility Charts
        svg_charts = self._compile_vector_visuals(playbook[:8])

        # 4. Inject Assembly HTML Template Core
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Institutional Multi-Asset Playbook</title>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; margin: 0; }}
                .container {{ max-width: 1300px; margin: auto; background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }}
                h1 {{ font-size: 24px; color: #f1f5f9; border-bottom: 2px solid #334155; padding-bottom: 20px; letter-spacing: 1px; }}
                h2 {{ font-size: 18px; color: #94a3b8; margin-top: 30px; text-transform: uppercase; letter-spacing: 0.5px; }}
                .economist-brief {{ background: #0f172a; padding: 30px; border-left: 4px solid #10b981; margin: 20px 0; border-radius: 0 8px 8px 0; line-height: 1.7; font-size: 15px; color: #cbd5e1; }}
                .visual-matrix {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 25px 0; }}
                .chart-card {{ background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155; text-align: center; }}
                .chart-card h4 {{ margin: 0 0 15px 0; color: #f1f5f9; font-size: 14px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
                th {{ text-align: left; padding: 15px; background: #334155; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
                td {{ padding: 15px; border-bottom: 1px solid #334155; color: #e2e8f0; }}
                .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
                .badge-breakout {{ background: #10b981; color: #0f172a; }}
                .badge-stable {{ background: #475569; color: #cbd5e1; }}
                code {{ font-family: 'Courier New', Courier, monospace; color: #38bdf8; background: #0f172a; padding: 2px 6px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏛️ GLOBAL MARKET INTELLIGENCE MATRIX</h1>
                <h2>Strategic Predictive Narrative</h2>
                <div class="economist-brief">{expert_narrative}</div>
                
                <h2>📊 Predictive Volatility Matrix (Cross-Asset Divergences)</h2>
                <div class="visual-matrix">
                    {svg_charts}
                </div>

                <h2>📋 Quant Arbitrage Data Ledger</h2>
                <table>
                    <tr>
                        <th>Asset</th><th>Sector Class</th><th>Spot Price</th><th>Signal</th>
                        <th>Z-Divergence</th><th>Implied Prob</th><th>Kelly Size</th><th>Tactical Narrative</th>
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
        """Compiles clean programmatic SVG spark-graphs dynamically."""
        svg_blocks = ""
        for a in target_assets:
            # Scale mathematical variance lines into safe visualization pixels
            z = abs(a.get('z_score', 1.0))
            height_factor = min(int(z * 25), 80)
            color = "#10b981" if a['trend'] == "BREAKOUT" else "#64748b"
            
            svg_blocks += f"""
            <div class="chart-card">
                <h4>{a['ticker']} Divergence Profile</h4>
                <svg width="220" height="90" style="background: #0b1329; border-radius: 4px;">
                    <!-- Probability distribution area fill mapping -->
                    <path d="M10 80 Q 60 {100 - height_factor}, 110 {90 - height_factor} T 210 80" fill="none" stroke="{color}" stroke-width="3"/>
                    <line x1="10" y1="80" x2="210" y2="80" stroke="#334155" stroke-dasharray="4"/>
                    <circle cx="110" cy="{90 - height_factor}" r="5" fill="#f43f5e"/>
                    <text x="15" y="25" fill="#94a3b8" font-size="10" font-family="sans-serif">P(Alpha) = {a['probability_pct']:.1f}%</text>
                </svg>
            </div>
            """
        return svg_blocks
