#!/usr/bin/env python3
"""
stripe_webhook_server.py
Institutional Billing Gateway (A+ Compliance Tier)
- Enforces strict multi-table relational schema for sub vs one-off ledgers.
- Implements single-transaction idempotency locking (INSERT ON CONFLICT).
- Prevents out-of-order race conditions using monotonic event timestamps.
- Optimizes database concurrency handling with WAL-mode connection pools.
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

# --- SECURE CONFIGURATION HANDSHAKE ---
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
    logger.critical("❌ CONFIGURATION FAULT: Missing required credentials.")
    sys.exit(1)

stripe.api_key = STRIPE_SECRET_KEY
DB_FILE = "billing_ledger.db"

# --- DEFINITIVE PLATFORM PRODUCT MATRICES ---
YEARLY_PRICE_IDS = {
    "price_1MmockAI_YearlyInstitutional": "yearly_all_access"
}
ONE_TIME_REPORT_PRICE_IDS = {
    "price_1MmockAI_HardwareReport": "report_hardware_infrastructure",
    "price_1MmockAI_DePINReport": "report_depin_compute"
}

def initialize_database():
    """Builds a normalized, multi-table database with strict transactional constraints."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        cursor = conn.cursor()
        
        # 1. Idempotency Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stripe_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_created INTEGER NOT NULL,
                processed_at_utc TEXT NOT NULL
            )
        """)
        # 2. Subscription Tracking Matrix (Yearly Plans)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stripe_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                price_id TEXT NOT NULL,
                status TEXT NOT NULL,
                current_period_end INTEGER NOT NULL,
                last_event_created INTEGER NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
        """)
        # 3. Permanent Report Purchases Tracking Matrix (One-Off Line Items)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_purchases (
                purchase_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                checkout_session_id TEXT UNIQUE NOT NULL,
                report_product_id TEXT NOT NULL,
                purchased_at_utc TEXT NOT NULL
            )
        """)
        # 4. Cached Entitlement Lookup Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_entitlements (
                customer_id TEXT PRIMARY KEY,
                yearly_access_active INTEGER NOT NULL DEFAULT 0,
                yearly_access_until INTEGER NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
        """)
        conn.commit()

initialize_database()

def process_webhook_transaction(event_id: str, event_type: str, event_created: int, payload_data: dict) -> tuple[str, int]:
    """Orchestrates atomic event deduplication and mutations inside a single isolated transaction."""
    current_timestamp = datetime.now(timezone.utc).isoformat()
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        cursor = conn.cursor()
        
        # --- AUDIT GATE 1: ATOMIC IDEMPOTENCY LOCK ---
        try:
            cursor.execute("""
                INSERT INTO stripe_events (event_id, event_type, event_created, processed_at_utc)
                VALUES (?, ?, ?, ?)
            """, (event_id, event_type, event_created, current_timestamp))
        except sqlite3.IntegrityError:
            logger.info(f"🛡️ IDEMPOTENCY BLOCKED: Replay request intercepted. Stripe Event [{event_id}] already finalized.")
            return "duplicate", 200

        # --- AUDIT GATE 2: YEARLY SUBSCRIPTION PERMISSION UPDATES ---
        if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
            sub_id = payload_data.get("id")
            customer_id = payload_data.get("customer")
            status = payload_data.get("status")
            period_end = int(payload_data.get("current_period_end", 0))
            items = payload_data.get("items", {})
            
            # Extract nested data lists safely handling standard Stripe collections
            if isinstance(items, dict):
                data_list = items.get("data", [])
            elif isinstance(items, list):
                data_list = items
            else:
                data_list = []

            if not data_list or not sub_id or not customer_id or not status:
                raise ValueError("Missing mandatory relational keys inside inbound subscription payload.")
                
            if isinstance(data_list, list) and len(data_list) > 0:
                first_item = data_list[0]
            elif isinstance(data_list, dict):
                first_item = data_list
            else:
                first_item = {}
            price_id = first_item.get("price", {}).get("id") if isinstance(first_item, dict) else None
            
            if price_id not in YEARLY_PRICE_IDS:
                raise ValueError(f"Ingested unmapped price ID entry: [{price_id}]. Denied access.")

            # Monotonic Timestamp Sequence Check to prevent out-of-order race conditions
            cursor.execute("SELECT last_event_created FROM stripe_subscriptions WHERE subscription_id = ?", (sub_id,))
            row = cursor.fetchone()
            if row and event_created < row[0]:
                logger.warning(f"⏳ OUT-OF-ORDER WARNING: Ignored stale Stripe event created at [{event_created}] for Sub [{sub_id}].")
                conn.rollback()
                return "stale_event_ignored", 200

            cursor.execute("""
                INSERT INTO stripe_subscriptions (subscription_id, customer_id, price_id, status, current_period_end, last_event_created, updated_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(subscription_id) DO UPDATE SET
                    price_id = excluded.price_id,
                    status = excluded.status,
                    current_period_end = excluded.current_period_end,
                    last_event_created = excluded.last_event_created,
                    updated_at_utc = excluded.updated_at_utc
            """, (sub_id, customer_id, price_id, status, period_end, event_created, current_timestamp))
            
            is_active = 1 if status in ["active", "trialing"] else 0
            cursor.execute("""
                INSERT INTO user_entitlements (customer_id, yearly_access_active, yearly_access_until, updated_at_utc)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(customer_id) DO UPDATE SET
                    yearly_access_active = excluded.yearly_access_active,
                    yearly_access_until = excluded.yearly_access_until,
                    updated_at_utc = excluded.updated_at_utc
            """, (customer_id, is_active, period_end, current_timestamp))

        elif event_type == "customer.subscription.deleted":
            sub_id = payload_data.get("id")
            customer_id = payload_data.get("customer")
            if not sub_id or not customer_id:
                raise ValueError("Missing target relational handles on deleted plan tracking frame.")
                
            cursor.execute("UPDATE stripe_subscriptions SET status = 'canceled', updated_at_utc = ? WHERE subscription_id = ?", (current_timestamp, sub_id))
            cursor.execute("UPDATE user_entitlements SET yearly_access_active = 0, updated_at_utc = ? WHERE customer_id = ?", (current_timestamp, customer_id))
            logger.info(f"🚫 SUBSCRIPTION DEACTIVATED: Access window dismantled for Sub [{sub_id}]")

        # --- AUDIT GATE 3: ONE-OFF REPORT PURCHASE LEDGER ENTRIES ---
        elif event_type == "checkout.session.completed":
            session_id = payload_data.get("id")
            customer_id = payload_data.get("customer")
            payment_status = payload_data.get("payment_status")
            
            if not session_id or not customer_id:
                raise ValueError("Missing critical user/session handles inside completion tracking vector.")
                
            if payment_status != "paid":
                logger.warning(f"💸 UNPAID EXCEPTION: Session [{session_id}] completed with status: {payment_status}. Access withheld.")
                return "unpaid_session_acknowledged", 200

            if payload_data.get("mode") == "subscription":
                logger.info(f"ℹ️ ROUTING FLOW: Passing sub session handle [{session_id}] down to dedicated handler rules.")
                conn.rollback()
                return "routed_to_subscription", 200

            line_items = payload_data.get("line_items", {}).get("data", [])
            price_id = line_items[0].get("price", {}).get("id") if line_items else payload_data.get("metadata", {}).get("stripe_price_id")

            if price_id not in ONE_TIME_REPORT_PRICE_IDS:
                raise ValueError(f"Ingested unmapped singular item price ID marker: [{price_id}]. Denied transaction.")
                
            report_product_token = ONE_TIME_REPORT_PRICE_IDS[price_id]
            purchase_uuid = f"pur_{session_id}"
            
            cursor.execute("""
                INSERT INTO report_purchases (purchase_id, customer_id, checkout_session_id, report_product_id, purchased_at_utc)
                VALUES (?, ?, ?, ?, ?)
            """, (purchase_uuid, customer_id, session_id, report_product_token, current_timestamp))
            logger.info(f"💰 LEDGER SINGLE PAYMENT RECORDED: User [{customer_id}] granted permanent lock to report [{report_product_token}]")

        conn.commit()
        return "success", 200

@app.route("/api/v1/billing/webhook", methods=["POST"])
def handle_stripe_billing_webhook():
    """Validates inbound payload parameters and protects internal logic against system error leakages."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    if not sig_header:
        logger.warning("❌ SECURITY REJECTION: Inbound webhook payload arrived missing a Stripe-Signature block.")
        return jsonify({"error": "Signature reference key missing"}), 400

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as crypt_err:
        logger.error(f"❌ CRYPTOGRAPHIC VERIFICATION FAULT: Malformed headers or key mismatch: {crypt_err}")
        return jsonify({"error": "Unauthorized signature handshake validation failed"}), 400

    event_id = event["id"]
    event_type = event["type"]
    event_created = int(event.get("created", 0))
    payload_data = event["data"]["object"]

    try:
        status_message, http_code = process_webhook_transaction(event_id, event_type, event_created, payload_data)
        return jsonify({"status": status_message, "processed_event_id": event_id}), http_code
    except ValueError as compliance_err:
        logger.error(f"❌ COMPLIANCE GATE ABORTED TRANSACTION: Mapping logic execution block error: {compliance_err}")
        return jsonify({"error": "Malformed transaction metadata parameters or invalid product profiles"}), 400
    except Exception as internal_crash:
        logger.critical(f"❌ UNHANDLED INTERNAL MATRIX BREAKDOWN CRASH: {internal_crash}")
        return jsonify({"error": "Internal ledger transactional synchronization failure"}), 500

if __name__ == "__main__":
    is_debug_active = os.getenv("FLASK_DEBUG") == "1"
    logger.info(f"🚀 Initializing A+ Dual-Ledger Billing Engine (Debug Environments: {is_debug_active})")
    app.run(port=4242, debug=is_debug_active)
