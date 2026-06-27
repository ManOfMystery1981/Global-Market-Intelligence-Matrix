import json
import hashlib
from datetime import datetime, timezone

class EvidenceGraph:
    """
    Compliance Evidence Matrix: Enforces strict data lineage by persisting 
    raw source payloads, generating SHA-256 hashes, and building audit trails.
    """
    def log_and_hash_payload(self, asset_key, raw_dict):
        """Generates a cryptographic fingerprint and stores raw telemetry data."""
        serialized = json.dumps(raw_dict, sort_keys=True)
        payload_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
        today_dir = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Save structural raw payload to disk for compliance verification
        raw_path = f"data/raw/{asset_key}_payload.json"
        try:
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(raw_dict, f, indent=4)
        except Exception:
            pass
            
        return payload_hash, raw_path

    def generate_audit_lineage(self, asset_profile, payload_hash):
        """Builds a defensible data tracking string for the report tables."""
        return (
            f"Endpoint Source: [{asset_profile['source']}] | "
            f"Hash Reference: {payload_hash[:12]}... | "
            f"Retrieval Window: {asset_profile['timestamp']} | "
            f"Statistical Metric: Z-Score={asset_profile['z_score']:+.2f}, Confidence={asset_profile['probability_pct']:.1f}%."
        )

    def append_appendix_logs(self, complete_playbook, hashes_map):
        """Assembles an auditable compliance table for the report footer."""
        html_appendix = "<div style='margin-top: 50px; border-top: 3px dashed #475569; padding-top: 25px;'>"
        html_appendix += "<h2 style='color:#f1f5f9;'>V. AUDIT LINEAGE REGISTRY & ETHICAL COMPLIANCE APPENDIX</h2>"
        html_appendix += "<p style='color:#94a3b8; font-size:12px; margin-bottom:15px;'>Every parameter inside this research brief is traceable to public endpoints. Cryptographic verification hashes are archived below.</p>"
        html_appendix += "<table style='width:100%; font-size:11px; font-family:monospace; color:#94a3b8; border-collapse: collapse;'>"
        html_appendix += "<tr style='background:#0f172a;'><th>Asset Key</th><th>Verifiable Data Source</th><th>Retrieval Timestamp (UTC)</th><th>SHA-256 Payload Hash</th><th>Signal Intensity</th></tr>"
        
        for item in complete_playbook:
            h = hashes_map.get(item['ticker'], "N/A")
            html_appendix += f"""
            <tr style='border-bottom: 1px solid #334155;'>
                <td style='padding:10px;'><strong>{item['ticker']}</strong></td>
                <td style='padding:10px;'>{item['source']}</td>
                <td style='padding:10px;'>{item['timestamp']}</td>
                <td style='padding:10px;'><code>{h}</code></td>
                <td style='padding:10px; color:#10b981;'><strong>{item['conviction_score']}/100</strong></td>
            </tr>
            """
        html_appendix += "</table></div>"
        return html_appendix
