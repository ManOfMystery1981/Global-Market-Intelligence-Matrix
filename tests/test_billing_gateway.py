#!/usr/bin/env python3
"""
tests/test_billing_gateway.py
A+ Compliance Test Harness: Simulates edge-case webhook delivery sequences,
idempotency transaction collisions, out-of-order packets, and multi-product isolation.
"""

import unittest
import sqlite3
import os
from datetime import datetime, timezone
from stripe_webhook_server import process_webhook_transaction, DB_FILE

class TestStripeWebhookEntitlements(unittest.TestCase):
    """Rigorous Billing Verification Layer: Enforces isolation and sequence safety."""
    
    def setUp(self) -> None:
        """Clears prior transaction database contexts before executing fresh logic passes."""
        if os.path.exists(DB_FILE):
            try:
                os.remove(DB_FILE)
            except OSError:
                pass
        
        # Re-import and initialize normalized database tables fresh for the test loop
        from stripe_webhook_server import initialize_database
        initialize_database()

    def test_yearly_subscription_lifecycle_and_stale_event_ordering(self):
        """Validates normal creation, renewal extension, and ensures stale network packets are rejected."""
        sub_payload = {
            "id": "sub_test_yearly_999",
            "customer": "cus_investor_alpha",
            "status": "active",
            "current_period_end": 1811808000,  # Far future epoch timestamp
            "items": {"data": {"price": {"id": "price_1MmockAI_YearlyInstitutional"}}}
        }
        
        # 1. Test Initial Creation Pass
        status, code = process_webhook_transaction("evt_sub_created_101", "customer.subscription.created", 1000, sub_payload)
        self.assertEqual(status, "success")
        self.assertEqual(code, 200)
        
        # Verify permissions cached accurately
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT yearly_access_active, yearly_access_until FROM user_entitlements WHERE customer_id = ?", ("cus_investor_alpha",))
            row = cursor.fetchone()
            self.assertEqual(row[0], 1)
            self.assertEqual(row[1], 1811808000)

        # 2. Test Monotonic Sequence Check: Simulating a stale retry packet arriving out-of-order
        stale_payload = copy_dict = sub_payload.copy()
        stale_payload["current_period_end"] = 1500000000  # Stale, shorter date
        
        status, code = process_webhook_transaction("evt_sub_stale_retry_102", "customer.subscription.updated", 500, stale_payload)
        self.assertEqual(status, "stale_event_ignored")
        self.assertEqual(code, 200)

    def test_duplicate_webhook_replay_protection_lock(self):
        """Enforces that a duplicate Stripe event ID triggers immediate transaction rollback."""
        payload = {
            "id": "sub_test_dup_888",
            "customer": "cus_investor_beta",
            "status": "active",
            "current_period_end": 1811808000,
            "items": {"data": {"price": {"id": "price_1MmockAI_YearlyInstitutional"}}}
        }
        
        # First execution must commit cleanly
        status_1, code_1 = process_webhook_transaction("evt_unique_hash_555", "customer.subscription.created", 2000, payload)
        self.assertEqual(status_1, "success")
        
        # Second execution with exact same event ID must block via single-transaction lock
        status_2, code_2 = process_webhook_transaction("evt_unique_hash_555", "customer.subscription.created", 2001, payload)
        self.assertEqual(status_2, "duplicate")
        self.assertEqual(code_2, 200)

    def test_one_off_report_purchase_isolation(self):
        """Asserts that a singular, one-off payment records permanent access without impacting subscription ledgers."""
        session_payload = {
            "id": "cs_test_oneoff_777",
            "customer": "cus_buyer_gamma",
            "payment_status": "paid",
            "mode": "payment",
            "metadata": {"stripe_price_id": "price_1MmockAI_HardwareReport"}
        }
        
        status, code = process_webhook_transaction("evt_checkout_completed_301", "checkout.session.completed", 3000, session_payload)
        self.assertEqual(status, "success")
        self.assertEqual(code, 200)
        
        # Verify permanent ledger records purchase, while yearly cached entitlement stays unimpacted
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT report_product_id FROM report_purchases WHERE customer_id = ?", ("cus_buyer_gamma",))
            self.assertEqual(cursor.fetchone()[0], "report_hardware_infrastructure")
            
            cursor.execute("SELECT yearly_access_active FROM user_entitlements WHERE customer_id = ?", ("cus_buyer_gamma",))
            row = cursor.fetchone()
            self.assertTrue(row is None or row[0] == 0)

    def test_unmapped_invalid_price_id_gate(self):
        """Guarantees that unmapped price IDs abort immediately with an internal compliance error."""
        rogue_payload = {
            "id": "sub_rogue_444",
            "customer": "cus_attacker",
            "status": "active",
            "current_period_end": 1811808000,
            "items": {"data": {"price": {"id": "price_invalid_hacked_tier"}}}
        }
        
        with self.assertRaises(ValueError):
            process_webhook_transaction("evt_rogue_999", "customer.subscription.created", 4000, rogue_payload)

if __name__ == "__main__":
    unittest.main()
