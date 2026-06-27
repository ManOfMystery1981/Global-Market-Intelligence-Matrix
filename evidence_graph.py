#!/usr/bin/env python3

class EvidenceGraph:
    """
    Compliance Evidence Layer: Enforces structural tracking paths and 
    source data lineages to back up AI generation parameters.
    """
    def generate_audit_lineage(self, asset_profile):
        """Builds an audit line explaining exactly where a value came from."""
        return (
            f"Endpoint: [{asset_profile['source']}] | "
            f"Timestamp: {asset_profile['timestamp']} | "
            f"Raw Spot: ${asset_profile['price']:,.2f} | "
            f"Math Trace: Z-Score={asset_profile['z_score']:+.2f}, "
            f"Kelly Fraction Allocation Size={asset_profile['kelly_fraction_pct']:.1f}%."
        )

    def append_appendix_logs(self, complete_playbook):
        """Assembles a compliance-ready data audit table for the report footer."""
        html_appendix = "<div style='margin-top: 50px; border-top: 3px dashed #475569; padding-top: 25px;'>"
        html_appendix += "<h2 style='color:#f1f5f9;'>V. EVIDENCE APPENDIX & DATA LINEAGE LOGS</h2>"
        html_appendix += "<p style='color:#94a3b8; font-size:12px; margin-bottom:15px;'>Every claim inside this brief is traceable to public endpoints. Run verification scripts against the hashes below.</p>"
        html_appendix += "<table style='width:100%; font-size:11px; font-family:monospace; color:#94a3b8; border-collapse: collapse;'>"
        html_appendix += "<tr style='background:#0f172a;'><th>Asset Key</th><th>Verifiable Source Reference</th><th>Retrieval Timestamp</th><th>Z-Score Trace</th><th>Composite Conviction</th></tr>"
        
        for item in complete_playbook:
            html_appendix += f"""
            <tr style='border-bottom: 1px solid #334155;'>
                <td style='padding:10px;'><strong>{item['ticker']}</strong></td>
                <td style='padding:10px;'>{item['source']}</td>
                <td style='padding:10px;'>{item['timestamp']}</td>
                <td style='padding:10px;'><code>Z = {item['z_score']:+.2f}</code></td>
                <td style='padding:10px; color:#10b981;'><strong>{item['conviction_score']}/100</strong></td>
            </tr>
            """
        html_appendix += "</table></div>"
        return html_appendix
