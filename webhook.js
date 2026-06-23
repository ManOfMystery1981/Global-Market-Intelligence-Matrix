// /api/webhook.js
export default async function handler(req, res) {
    // Only accept POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const payload = req.body;
        console.log('📨 Webhook received:', JSON.stringify(payload, null, 2));

        // --- Verify the webhook signature (recommended) ---
        // const signature = req.headers['moonpay-signature-v2'];
        // const isValid = verifySignature(signature, JSON.stringify(payload), process.env.WEBHOOK_SECRET);
        // if (!isValid) return res.status(401).json({ message: 'Invalid signature' });

        // --- Handle payment_intent (user started checkout) ---
        if (payload.event === 'payment_intent') {
            console.log(`📝 Payment intent registered for: ${payload.email}`);
            // Store this email in a database or cache, keyed by a reference
            // You'll use this to match the incoming payment
            return res.status(200).json({ message: 'Intent stored' });
        }

        // --- Handle completed payment from MoonPay ---
        const status = payload.status || payload.event;
        const amount = payload.amount?.amount || payload.quote?.crypto_amount;
        const currency = payload.amount?.currency || payload.quote?.crypto_currency;
        const email = payload.metadata?.email || payload.memo;

        if (status === 'completed' && parseFloat(amount) >= 0.01 && currency === 'SOL') {
            console.log(`✅ Payment confirmed for: ${email}`);

            // --- Trigger your pipeline ---
            // Option 1: Call your deployed Python API (recommended)
            // await triggerPipeline(email);

            // Option 2: Use Vercel Workflows or a queue system
            // Option 3: Directly invoke a serverless function

            return res.status(200).json({
                message: 'Payment confirmed, pipeline triggered',
                email: email
            });
        }

        // Acknowledge receipt even if we ignore the event
        return res.status(200).json({ message: 'Webhook received' });

    } catch (error) {
        console.error('❌ Webhook error:', error);
        return res.status(500).json({ message: 'Internal error' });
    }
}
