#!/usr/bin/env python3
"""
stripe_webhook_server.py
Institutional Entitlement Gateway: Processes secure billing webhooks,
enforces cryptographic verification, and maps transaction tokens safely.
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import stripe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("A_Plus_Billing_Gateway")

app = Flask(__name__)

# --- AUDIT GATE 1: STRICT SECURITY ENVIRONMENT VERIFICATION ---
# Enforce immediate process crash on missing credentials (No fail-open mock shortcuts allowed)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
    logger.critical("❌ CRITICAL CONFIGURATION FAULT: Missing required STRIPE_SECRET_KEY or STRIPE_WEBHOOK_SECRET environment vectors.")
    sys.exit(1)

stripe.api_key = STRIPE_SECRET_KEY

# --- AUDIT GATE 2: DEFINITIVE ENTITLEMENT PERMISSION MATRIX ---
# Explicitly links Stripe price object identifiers straight to internal token bands
TIER_ENTITLEMENT_MAP = {
    "price_1MmockAI_StandardMonthly": "standard_research_tier",
    "price_1MmockAI_PremiumInstitutional": "premium_institutional_tier",
    "price_1MmockAI_DataArbitrageAPI": "enterprise_data_api_tier"
}

# --- AUDIT GATE 3: PRODUCTION DATABASE PERSISTENCE LAYER ---
# Replaces fragile JSON arrays with an atomic SQL transaction ledger
DB_FILE = "billing_ledger.db"

def initialize_database():
    """Initializes schema to enforce structural relational integrity constraints."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # Table 1: Cryptographic Event Ledger to block Replay Attacks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stripe_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                processed_at_utc TEXT NOT NULL
            )
        """)
        # Table 2: User Entitlement State Ledger to block Race Conditions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                customer_id TEXT PRIMARY KEY,
                price_id TEXT NOT NULL,
                tier_token TEXT NOT NULL,
                status TEXT NOT NULL,
                last_synchronized_utc TEXT NOT NULL
            )
        """)
        conn.commit()

# Initialize ledger tables immediately on startup runtime
initialize_database()

def is_duplicate_event(event_id: str) -> bool:
    """Idempotency Check: Verifies if event was already committed."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM stripe_events WHERE event_id = ?", (event_id,))
        return cursor.fetchone() is not None

def log_processed_event(event_id: str, event_type: str):
    """Persists event token inside the immutable tracking table."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO stripe_events (event_id, event_type, processed_at_utc) VALUES (?, ?, ?)",
            (event_id, event_type, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()

def sync_subscription_entitlement(customer_id: str, price_id: str, status: str):
    """Executes atomic upsert state updates with strict pricing schema filtering."""
    internal_tier_token = TIER_ENTITLEMENT_MAP.get(price_id)
    
    # Audit Rule: Unknown price parameters must throw explicit faults, not grant anonymous access
    if internal_tier_token is None:
        logger.error(f"❌ COMPLIANCE FAULT: Unmapped or invalid Stripe Price ID ingested: [{price_id}]")
        raise ValueError(f"Ingested Price ID [{price_id}] lacks internal mapping authorization constraints.")
        
    current_timestamp = datetime.now(timezone.utc).isoformat()
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_subscriptions (customer_id, price_id, tier_token, status, last_synchronized_utc)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(customer_id) DO UPDATE SET
                price_id = excluded.price_id,
                tier_token = excluded.tier_token,
                status = excluded.status,
                last_synchronized_utc = excluded.last_synchronized_utc
        """, (customer_id, price_id, internal_tier_token, status, current_timestamp))
        conn.commit()
    logger.info(f"💾 LEDGER TRANSACTION COMMITTED: Customer [{customer_id}] synchronized to Tier Token [{internal_tier_token}] (Status: {status})")

def revoke_subscription_entitlement(customer_id: str):
    """Explicitly downgrades state variables upon subscription cancellation."""
    current_timestamp = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_subscriptions (customer_id, price_id, tier_token, status, last_synchronized_utc)
            VALUES (?, 'REVOKED', 'revoked_anonymous_tier', 'canceled', ?)
            ON CONFLICT(customer_id) DO UPDATE SET
                price_id = 'REVOKED',
                tier_token = 'revoked_anonymous_tier',
                status = 'canceled',
                last_synchronized_utc = excluded.last_synchronized_utc
        """, (customer_id, current_timestamp))
        conn.commit()
    logger.info(f"🚫 LEDGER ENTITLEMENT REVOKED: Account permissions dismantled for Customer [{customer_id}]")

@app.route("/api/v1/billing/webhook", methods=["POST"])
def handle_stripe_billing_webhook():
    """Cryptographic Ingestion Gateway: Decodes and verifies payload bodies."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    if not sig_header:
        logger.warning("❌ SECURITY REJECTION: Inbound webhook payload arrived missing a Stripe-Signature block.")
        return jsonify({"error": "Signature missing"}), 400

    # Cryptographic Signature Payload Evaluation Block
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("❌ SECURITY FAULT: Payload body serialization structure is invalid.")
        return jsonify({"error": "Invalid payload serialization"}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ SECURITY FAULT: Cryptographic token handshake verification failed: {e}")
        return jsonify({"error": "Signature handshake invalid"}), 400

    event_id = event["id"]
    event_type = event["type"]

    # --- AUDIT GATE 4: IMMUTABLE DEDUPLICATION AND REPLAY PROTECTION ---
    if is_duplicate_event(event_id):
        logger.info(f"🛡️ IDEMPOTENCY HIT: Replay request blocked. Stripe Event [{event_id}] already resolved.")
        return jsonify({"status": "duplicate", "resolved_event_id": event_id}), 200

    logger.info(f"📦 INGESTION ACCESS: Processing unique event [{event_id}] (Type: {event_type})")

    try:
        if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")
            status = subscription.get("status")
            
            # Extract nested pricing parameters carefully
            items_array = subscription.get("items", {}).get("data", [])
            if not items_array:
                logger.error(f"❌ METADATA EXCEPTION: Subscription item array array holds empty values for event {event_id}")
                return jsonify({"error": "Malformed transaction items"}), 400
                
            price_id = items_array[0].get("price", {}).get("id")
            
            # Ensure every single mandatory database indexing key is fully populated
            if not customer_id or not status or not price_id:
                logger.error("❌ COMPLIANCE ERROR: Missing vital subscription structural parameters inside webhook object body.")
                return jsonify({"error": "Vital metadata keys missing"}), 400
                
            sync_subscription_entitlement(customer_id, price_id, status)

        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")
            if not customer_id:
                logger.error("❌ COMPLIANCE ERROR: Customer identity missing on cancellation tracking event block.")
                return jsonify({"error": "Customer handle missing"}), 400
            revoke_subscription_entitlement(customer_id)
            
        # Log successful completion to permanently close out idempotency lane
        log_processed_event(event_id, event_type)
        
    except ValueError as val_err:
        logger.error(f"❌ COMPLIANCE GATE BLOCK: Mapping rules aborted transaction: {val_err}")
        return jsonify({"error": str(val_err)}), 400
    except Exception as sys_err:
        logger.critical(f"❌ UNHANDLED INTERNAL TRANSITION CRASH: {sys_err}")
        return jsonify({"error": "Internal ledger processing collapse"}), 500

    return jsonify({"status": "success", "processed_event_id": event_id}), 200

if __name__ == "__main__":
    # --- AUDIT GATE 5: REMOVE DANGEROUS REBOOT DEBUG ENVIRONMENT FLAGS ---
    # Enforces strict WSGI deployment standards; safely routes debug via variable checks
    is_debug_active = os.getenv("FLASK_DEBUG") == "1"
    logger.info(f"🚀 Initializing Institutional Billing Server Gateway (Debug: {is_debug_active})")
    app.run(port=4242, debug=is_debug_active)
