// api/webhook.js
// Production-ready webhook for MoonPay/Hel.io payments

module.exports = async function handler(req, res) {
    // GET request for manual testing
    if (req.method === 'GET') {
        return res.status(200).json({
            message: 'Webhook is alive. Use POST to send payment data.',
            status: 'ready'
        });
    }

    // HEAD request for decision engine health checks
    if (req.method === 'HEAD') {
        return res.status(200).end();
    }

    // Only POST requests are allowed for payments
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const payload = req.body;
        console.log('📨 Webhook received:', JSON.stringify(payload, null, 2));

        // Extract payment details
        const email = payload.metadata?.email || payload.customerEmail || payload.memo || payload.email;
        const status = payload.status || payload.event;
        const amount = payload.amount?.amount || payload.quote?.crypto_amount || 0;
        const currency = payload.amount?.currency || payload.quote?.crypto_currency || 'SOL';

        // Validate payment
        const isCompleted = status === 'completed' || status === 'confirmed';
        const isValidAmount = parseFloat(amount) >= 0.01;
        const isValidCurrency = currency === 'SOL';

        if (isCompleted && isValidAmount && isValidCurrency && email) {
            console.log(`✅ Payment confirmed for: ${email}`);

            // --- Log the sale to the database ---
            try {
                const sqlite3 = require('sqlite3').verbose();
                const path = require('path');
                const dbPath = path.join(process.cwd(), 'corporate_ledger.db');
                const db = new sqlite3.Database(dbPath);

                db.run(
                    `INSERT INTO marketing_ledger (timestamp, keyword_targeted, output_file, status, source) VALUES (?, ?, ?, ?, ?)`,
                    [Math.floor(Date.now() / 1000), 'webhook_sale', 'payment_confirmed', 'SALE', 'webhook'],
                    function(err) {
                        if (err) {
                            console.error('❌ Failed to log sale:', err.message);
                        } else {
                            console.log('✅ Sale logged to marketing_ledger');
                        }
                        db.close();
                    }
                );
            } catch (dbError) {
                console.error('❌ Database error:', dbError.message);
            }

            // --- Trigger your Python pipeline ---
            // Option 1: Call your Python server (if deployed)
            // Option 2: Trigger via GitHub Actions
            // Option 3: For now, log and acknowledge

            return res.status(200).json({
                message: 'Payment confirmed',
                email: email,
                status: 'success'
            });
        }

        // If payment doesn't match criteria
        console.log('⚠️ Webhook received but not a valid payment:', {
            status,
            amount,
            currency,
            email
        });
        return res.status(200).json({ message: 'Webhook received (not a valid payment)' });

    } catch (error) {
        console.error('❌ Webhook error:', error);
        return res.status(500).json({
            message: 'Internal server error',
            error: error.message
        });
    }
};
