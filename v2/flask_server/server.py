#!/usr/bin/env python3
"""
server.py
Flask Webhook Server & API Backend

Routes:
  POST /api/checkout          → Creates Stripe checkout session
  POST /webhooks/stripe       → Handles Stripe payment confirmation
  POST /webhooks/crypto       → Handles crypto payment confirmation (Hel.io/MoonPay)
  GET  /api/health            → Health check
  GET  /api/status            → Pipeline status
"""

import os
import json
import logging
import hashlib
import hmac
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify

# Import pipeline modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
from bots.data_collector     import collect_all_data
from bots.collaborative_writer import generate_report
from bots.delivery_agent     import send_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FlaskServer")

app = Flask(__name__)

# ── Environment Config ────────────────────────────────────────────────────────
STRIPE_SECRET_KEY      = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID        = os.getenv("STRIPE_PRICE_ID", "")
HELIO_WEBHOOK_SECRET   = os.getenv("HELIO_WEBHOOK_SECRET", "")
FLASK_SECRET           = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-in-production")

app.secret_key = FLASK_SECRET

# ── Pipeline Runner (runs in background thread) ───────────────────────────────
def run_pipeline_for_customer(email: str, report_type: str):
    """
    Full pipeline execution triggered after confirmed payment.
    Runs in a background thread so webhook returns immediately.
    """
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{run_id}] 🚀 Pipeline triggered for {email} — {report_type}")

    try:
        # Step 1: Collect all market data
        logger.info(f"[{run_id}] 📡 Collecting market data...")
        market_data = collect_all_data()
        logger.info(f"[{run_id}] ✅ Data collected from {market_data.get('source_count', 0)} sources")

        # Step 2: Generate report via DeepSeek + Grok loop
        logger.info(f"[{run_id}] ✍️  Starting collaborative report generation...")
        report_result = generate_report(market_data, report_type)
        logger.info(f"[{run_id}] ✅ Report approved: score {report_result['final_score']}/100 in {report_result['iterations_used']} iterations")

        # Step 3: Deliver to customer
        logger.info(f"[{run_id}] 📧 Delivering report to {email}...")
        delivered = send_report(email, report_result, market_data, report_type)

        if delivered:
            logger.info(f"[{run_id}] 🏁 Pipeline complete. Report delivered to {email}")
        else:
            logger.error(f"[{run_id}] ❌ Delivery failed for {email}")

    except Exception as e:
        logger.error(f"[{run_id}] 💥 Pipeline failed: {e}", exc_info=True)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.route("/api/equity-snapshot", methods=["GET"])
def equity_snapshot():
    """Real-time equity prices from Finnhub for the analytics chart feed."""
    import urllib.request as ur
    FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "")
    TICKERS = ["NVDA", "SPY", "QQQ", "GLD", "TLT", "USO"]
    if not FINNHUB_KEY:
        return jsonify({"error": "FINNHUB_API_KEY not set"}), 503
    result = {}
    for ticker in TICKERS:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
            req = ur.Request(url, headers={"User-Agent": "GMIM/2.0"})
            with ur.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
            price  = data.get("c", 0)
            prev   = data.get("pc", price) or price
            change = round(((price - prev) / prev * 100), 2) if prev else 0
            result[ticker] = {
                "price":      round(price, 2),
                "change_pct": change,
                "high":       data.get("h", 0),
                "low":        data.get("l", 0),
                "open":       data.get("o", 0),
                "source":     "Finnhub",
            }
        except Exception as e:
            print(f"Finnhub fetch failed for {ticker}: {e}")
    result["_timestamp"] = datetime.now(timezone.utc).isoformat()
    result["_source"]    = "Finnhub"
    return jsonify(result)


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "service":    "Global Market Intelligence Matrix",
        "version":    "2.0",
        "pipeline":   "DeepSeek V3 + Grok 3",
        "status":     "operational",
        "timestamp":  datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/checkout", methods=["POST"])
def create_checkout():
    """Creates a Stripe checkout session and returns the URL."""
    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        data         = request.get_json()
        email        = data.get("email", "").strip()
        report_type  = data.get("report_type", "Arbitrage Opportunity Matrix")
        payment_method = data.get("payment_method", "stripe")

        if not email or "@" not in email:
            return jsonify({"error": "Valid email required"}), 400

        if payment_method == "crypto":
            # Redirect to Hel.io payment page
            helio_url = os.getenv("HELIO_PAYMENT_URL", "https://hel.io/pay/YOUR_HELIO_LINK")
            return jsonify({"checkout_url": helio_url})

        # Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price":    STRIPE_PRICE_ID,
                "quantity": 1,
            }],
            mode="payment",
            customer_email=email,
            metadata={
                "report_type": report_type,
                "email":       email,
            },
            success_url=os.getenv("SUCCESS_URL", "https://your-domain.com/success"),
            cancel_url=os.getenv("CANCEL_URL",  "https://your-domain.com/cancel"),
        )

        return jsonify({"checkout_url": session.url})

    except ImportError:
        return jsonify({"error": "Stripe not installed. Run: pip install stripe"}), 500
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhooks/stripe", methods=["POST"])
def stripe_webhook():
    """Handles Stripe payment confirmation webhooks."""
    payload    = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        logger.error(f"Stripe webhook verification failed: {e}")
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session     = event["data"]["object"]
        email       = session.get("customer_email") or session.get("metadata", {}).get("email", "")
        report_type = session.get("metadata", {}).get("report_type", "Arbitrage Opportunity Matrix")

        logger.info(f"💳 Stripe payment confirmed: {email} — {report_type}")

        # Trigger pipeline in background thread
        thread = threading.Thread(
            target=run_pipeline_for_customer,
            args=(email, report_type),
            daemon=True
        )
        thread.start()

    return jsonify({"received": True})


@app.route("/webhooks/crypto", methods=["POST"])
def crypto_webhook():
    """Handles Hel.io/MoonPay crypto payment confirmation webhooks."""
    payload = request.get_json()

    # Verify Hel.io webhook signature if secret is set
    if HELIO_WEBHOOK_SECRET:
        sig = request.headers.get("Helio-Signature", "")
        expected = hmac.new(
            HELIO_WEBHOOK_SECRET.encode(),
            request.get_data(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return jsonify({"error": "Invalid signature"}), 400

    # Extract customer data from payload
    # Hel.io payload structure varies — adjust field names to match your Hel.io setup
    email       = payload.get("customerDetails", {}).get("email", "")
    report_type = payload.get("metadata", {}).get("report_type", "Arbitrage Opportunity Matrix")
    status      = payload.get("transactionStatus", "")

    if status.lower() in ("completed", "success", "paid") and email:
        logger.info(f"🪙 Crypto payment confirmed: {email} — {report_type}")
        thread = threading.Thread(
            target=run_pipeline_for_customer,
            args=(email, report_type),
            daemon=True
        )
        thread.start()

    return jsonify({"received": True})


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"🚀 Flask server starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
