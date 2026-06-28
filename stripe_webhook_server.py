#!/usr/bin/env python3
"""
stripe_webhook_server.py
Institutional Entitlement Gateway: Processes secure billing webhooks,
enforces signature verification, and maps subscription tokens safely.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
import stripe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Institutional_Billing_Gateway")

app = Flask(__name__)

# Enforce secure configuration mapping out of protected environment caches
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_placeholder")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_placeholder")

# DEFINITIVE BRAND ENTITLEMENT MAPPING MATRIX
# Explicitly links external Stripe Price object IDs to internal permission tokens
TIER_ENTITLEMENT_MAP = {
    "price_1MmockAI_StandardMonthly": "standard_research_tier",
    "price_1MmockAI_PremiumInstitutional": "premium_institutional_tier",
    "price_1MmockAI_DataArbitrageAPI": "enterprise_data_api_tier"
}

def update_user_subscription_status(customer_id: str, price_id: str, status: str):
    """
    State Synchronization Loop: Maps price parameters straight to token
    entitlements, enforcing explicit database record preservation.
    """
    internal_tier_token = TIER_ENTITLEMENT_MAP.get(price_id, "free_anonymous_tier")
    
    logger.info(f"💾 STATE UPDATE: Customer [{customer_id}] mapped to Tier Token [{internal_tier_token}] (Status: {status})")
    
    # LOAD/UPDATE USER REGISTRY SUBSCRIBERS MATRIX FILE
    ledger_path = "subscribers.json"
    try:
        if os.path.exists(ledger_path):
            with open(ledger_path, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        else:
            ledger = {}
            
        # Synchronize structural tier permissions
        ledger[customer_id] = {
            "tier_token": internal_tier_token,
            "stripe_price_id": price_id,
            "subscription_status": status,
            "last_synchronized_utc": stripe.Util.utc_now() if hasattr(stripe, 'Util') else "CURRENT_TIMESTAMP"
        }
        
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4)
        logger.info(f"✅ LEDGER SYNCHRONIZED: Saved status for Customer [{customer_id}]")
    except Exception as e:
        logger.error(f"❌ DATABASE LOCK FAULT: Failed to update local subscription matrix: {e}")

@app.route("/api/v1/billing/webhook", methods=["POST"])
def handle_stripe_billing_webhook():
    """
    Ingestion Endpoint: Validates cryptographic signature payloads
    and orchestrates serverless entitlement updates safely.
    """
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    # GATE 1: Cryptographic Signature Enforcement Check
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        logger.error("❌ SECURITY ALERT: Invalid payload body structure parsed.")
        return jsonify({"error": "Invalid payload format"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ SECURITY ALERT: Cryptographic signature mismatch verification failed: {e}")
        return jsonify({"error": "Signature mismatch verification failed"}), 400

    event_type = event["type"]
    event_id = event["id"]
    logger.info(f"📦 INGESTED WEBHOOK: Processing event {event_id} [Type: {event_type}]")

    # GATE 2: Route Context Entitlements Based on Stripe Event Types
    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        status = subscription.get("status")
        
        # Pull the primary price identifier safely out of the nested array lines object
        items = subscription.get("items", {}).get("data", [])
        if items:
            price_id = items[0].get("price", {}).get("id")
            update_user_subscription_status(customer_id, price_id, status)
        else:
            logger.warning(f"⚠️ METADATA MISSING: No pricing item metadata arrays found on Subscription {subscription.get('id')}")

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        # Revoke or downgrade user status immediately upon plan termination
        update_user_subscription_status(customer_id, "plan_terminated", "canceled")

    return jsonify({"status": "success", "processed_event_id": event_id}), 200

if __name__ == "__main__":
    # Internal dev-server initialization route parameters
    app.run(port=4242, debug=True)
EOF
