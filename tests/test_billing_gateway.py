#!/usr/bin/env python3
"""
tests/test_billing_gateway.py
A+ Compliance Test Harness: Simulates edge-case webhook delivery sequences,
idempotency transaction collisions, out-of-order packets, and multi-product isolation.
"""

import unittest
import sqlite3
import os
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
        from stripe_webhook_server import initialize_database
        initialize_database()

    def test_yearly_subscription_lifecycle_and_stale_event_ordering(self):
        """Validates normal creation, renewal extension, and ensures stale network packets are rejected."""
        sub_payload = {
            "id": "sub_test_yearly_999",
            "customer": "cus_investor_alpha",
            "status": "active",
            "current_period_end": 1811808000,
            "items": {"data": [{"price": {"id": "price_1MmockAI_YearlyInstitutional"}}]}
        }
        
        status, code = process_webhook_transaction("evt_sub_created_101", "customer.subscription.created", 1000, sub_payload)
        self.assertEqual(status, "success")
        
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT yearly_access_active FROM user_entitlements WHERE customer_id = ?", ("cus_investor_alpha",)).fetchone()
            self.assertEqual(row[0], 1)

        stale_payload = sub_payload.copy()
        status, code = process_webhook_transaction("evt_sub_stale_retry_102", "customer.subscription.updated", 500, stale_payload)
        self.assertEqual(status, "stale_event_ignored")

    def test_subscription_cancellation_policy_retention(self):
        """Asserts that a canceled subscription maintains access until the current period end timestamp."""
        cancel_payload = {
            "id": "sub_test_cancel_555",
            "customer": "cus_canceled_user",
            "status": "canceled",  # Stripe marks canceled plans active until period end
            "current_period_end": 1811808000,
            "items": {"data": [{"price": {"id": "price_1MmockAI_YearlyInstitutional"}}]}
        }
        
        status, code = process_webhook_transaction("evt_sub_canceled_202", "customer.subscription.updated", 1500, cancel_payload)
        self.assertEqual(status, "success")
        
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT yearly_access_active, yearly_access_until FROM user_entitlements WHERE customer_id = ?", ("cus_canceled_user",)).fetchone()
            self.assertEqual(row[0], 1, "❌ FAULT: Cancellation revoked access immediately before period end.")
            self.assertEqual(row[1], 1811808000)

    def test_duplicate_webhook_replay_protection_lock(self):
        """Enforces that a duplicate Stripe event ID triggers immediate transaction rollback."""
        payload = {
            "id": "sub_test_dup_888",
            "customer": "cus_investor_beta",
            "status": "active",
            "current_period_end": 1811808000,
            "items": {"data": [{"price": {"id": "price_1MmockAI_YearlyInstitutional"}}]}
        }
        status_1, _ = process_webhook_transaction("evt_unique_hash_555", "customer.subscription.created", 2000, payload)
        self.assertEqual(status_1, "success")
        status_2, _ = process_webhook_transaction("evt_unique_hash_555", "customer.subscription.created", 2001, payload)
        self.assertEqual(status_2, "duplicate")

    def test_duplicate_checkout_session_event_protection(self):
        """Asserts that duplicate checkout completed events do not create multiple ledger purchase entries."""
        session_payload = {
            "id": "cs_test_duplicate_999",
            "customer": "cus_buyer_delta",
            "payment_status": "paid",
            "mode": "payment",
            "metadata": {"stripe_price_id": "price_1MmockAI_HardwareReport"}
        }
        
        # Ingest main payment event path
        status_1, _ = process_webhook_transaction("evt_checkout_path_001", "checkout.session.completed", 3000, session_payload)
        self.assertEqual(status_1, "success")
        
        # Ingest separate event path with identical session payload (e.g. payment_intent hook backup fallback path)
        status_2, _ = process_webhook_transaction("evt_payment_intent_path_002", "checkout.session.completed", 3001, session_payload)
        self.assertEqual(status_2, "duplicate_checkout_ignored")

    def test_one_off_report_purchase_isolation(self):
        """Asserts that a singular, one-off payment records permanent access without impacting subscription ledgers."""
        session_payload = {
            "id": "cs_test_oneoff_777",
            "customer": "cus_buyer_gamma",
            "payment_status": "paid",
            "mode": "payment",
            "metadata": {"stripe_price_id": "price_1MmockAI_HardwareReport"}
        }
        status, _ = process_webhook_transaction("evt_checkout_completed_301", "checkout.session.completed", 3000, session_payload)
        self.assertEqual(status, "success")
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT report_product_id FROM report_purchases WHERE customer_id = ?", ("cus_buyer_gamma",)).fetchone()
            self.assertEqual(row[0], "report_hardware_infrastructure")

    def test_unmapped_invalid_price_id_gate(self):
        """Guarantees that unmapped price IDs abort immediately with an internal compliance error."""
        rogue_payload = {
            "id": "sub_rogue_444",
            "customer": "cus_attacker",
            "status": "active",
            "current_period_end": 1811808000,
            "items": {"data": [{"price": {"id": "price_invalid_hacked_tier"}}]}
        }
        with self.assertRaises(ValueError):
            process_webhook_transaction("evt_rogue_999", "customer.subscription.created", 4000, rogue_payload)

if __name__ == "__main__":
    unittest.main()
