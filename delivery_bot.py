import os
import json
import base64
import resend

# Authenticate Third-Party APIs from environment
resend.api_key = os.environ.get("RESEND_API_KEY")

def dispatch_secure_fulfillment_package(html_path, csv_path):
    """
    Autonomous Functional Delivery Engine: Reads subscriber records from local JSON storage
    and handles secure, isolated email routing through Resend.
    """
    print("🗄️ Loading subscriber ledger from local storage...")
    try:
        with open("subscribers.json", "r", encoding="utf-8") as f:
            subscribers = json.load(f)
            if isinstance(subscribers, dict):
                print("⚠️ Warning: subscribers.json was structured as a dictionary. Resetting to array format.")
                subscribers = []
    except FileNotFoundError:
        print("⚠️ subscribers.json not detected. Halting compilation.")
        return False
    except Exception as e:
        print(f"❌ Ledger compilation error: {e}")
        return False

    if not subscribers:
        print("⚠️ Zero active accounts identified inside ledger. Halting delivery execution pass.")
        return False

    print(f"📧 Resend active. Preparing secure transmission for {len(subscribers)} accounts...")

    # Process and convert compiled report files into standard base64 formats
    try:
        with open(html_path, "rb") as f:
            html_encoded = base64.b64encode(f.read()).decode("utf-8")

        with open(csv_path, "rb") as f:
            csv_encoded = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Error reading report attachments: {e}")
        return False

    attachments = [
        {"content": html_encoded, "filename": "Institutional_Market_Playbook.html"},
        {"content": csv_encoded, "filename": "macro_alpha_dataset.csv"}
    ]

    all_successful = True
    for client in subscribers:
        email = client.get('email')
        if client.get('status') != 'active':
            continue
            
        try:
            resend.Emails.send({
                "from": "Institutional Research <delivery@global-market-intelligence-matrix.dedyn.io>",
                "to": email,
                "subject": "📊 DATA UPDATE: Institutional Market Playbook & Alpha Dataset",
                "html": """
                    <div style="font-family: Arial, sans-serif; color: #1e293b; padding: 20px; line-height: 1.6;">
                        <h3>Your Monthly Research Deliverables Are Complete</h3>
                        <p>Dear Partner,</p>
                        <p>Our automated market analysis engine has finished its scheduled multi-asset data collection pass for this month's macro cycles.</p>
                        <p><strong>Your secure files are attached:</strong></p>
                        <ul>
                            <li><strong>Playbook Dashboard (.html):</strong> Dark-mode visual terminal interface featuring senior economist narrative commentary blocks.</li>
                            <li><strong>Quantitative Dataset (.csv):</strong> Clean, flat-file structured dataset optimized for portfolio backtesting.</li>
                        </ul>
                        <br>
                        <p style="font-size: 11px; color: #64748b;">Securitized transmission distributed via automated GitHub Agent pipelines.</p>
                    </div>
                """,
                "attachments": attachments
            })
            print(f"✅ Secure payload successfully transmitted to: {email}")
        except Exception as mail_error:
            print(f"❌ Resend delivery failure for {email}: {mail_error}")
            all_successful = False

    return all_successful
