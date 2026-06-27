class IndustryStandardReport:
    """
    Institutional Playbook Renderer: Converts intelligence logic into 
    high-density, professional business intelligence documentation and CSV datasets.
    """
    # FIX: Updated to accept expert_narrative as the third argument
    def generate_report(self, playbook, expert_narrative):
        import csv
        
        # 1. Output the raw CSV data for institutional quant backtesting
        csv_filename = "macro_alpha_dataset.csv"
        csv_fields = ["ticker", "category", "price", "trend", "narrative"]
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields)
                writer.writeheader()
                for p in playbook:
                    writer.writerow({k: p[k] for k in csv_fields})
            print(f"✅ Quantitative CSV Dataset Exported: {csv_filename}")
        except Exception as e:
            print(f"Error generating CSV: {e}")

        # 2. Build the visual dashboard table rows
        rows = "".join([f"""
            <tr class='{p['trend'].lower()}'>
                <td><strong>{p['ticker']}</strong></td>
                <td>{p['category']}</td>
                <td>${p['price']:,.2f}</td>
                <td><span class='badge'>{p['trend']}</span></td>
                <td class='narrative'>{p['narrative']}</td>
            </tr>
        """ for p in playbook])
        
        # 3. Inject Gemini's economist overview
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
                .container {{ max-width: 1100px; margin: auto; background: #1e293b; padding: 40px; border-radius: 12px; }}
                h1 {{ border-bottom: 2px solid #334155; padding-bottom: 20px; }}
                .economist-brief {{ background: #0f172a; padding: 25px; border-left: 4px solid #10b981; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th {{ text-align: left; padding: 15px; border-bottom: 2px solid #334155; }}
                td {{ padding: 15px; border-bottom: 1px solid #334155; }}
                .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; background: #334155; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>INSTITUTIONAL MARKET PLAYBOOK</h1>
                <h2>Macro Strategic Brief</h2>
                <div class="economist-brief">{expert_narrative}</div>
                <h2>Data Ledger Summary</h2>
                <table>
                    <tr><th>Asset</th><th>Class</th><th>Price</th><th>Signal</th><th>Narrative</th></tr>
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
