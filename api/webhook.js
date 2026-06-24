// api/webhook.js
export default async function handler(req, res) {
    // --- Handle GET requests (for manual testing) ---
    if (req.method === 'GET') {
        return res.status(200).json({ 
            message: 'Webhook is alive. Use POST to send payment data.',
            status: 'ready'
        });
    }

    // --- Handle HEAD requests (for health checks) ---
    if (req.method === 'HEAD') {
        // Return only headers, no body
        return res.status(200).end();
    }

    // --- Handle POST requests (payment webhooks) ---
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const payload = req.body;
        console.log('📨 Webhook received:', JSON.stringify(payload, null, 2));

        const email = payload.metadata?.email || payload.customerEmail || payload.memo;
        const status = payload.status || payload.event;
        const amount = payload.amount?.amount || payload.quote?.crypto_amount;
        const currency = payload.amount?.currency || payload.quote?.crypto_currency;

        if ((status === 'completed' || status === 'confirmed') && 
            parseFloat(amount) >= 0.01 && 
            currency === 'SOL' && 
            email) {
            
            console.log(`✅ Payment confirmed for: ${email}`);
            // Trigger your Python pipeline here
            
            return res.status(200).json({ message: 'Payment confirmed', email });
        }

        return res.status(200).json({ message: 'Webhook received' });

    } catch (error) {
        console.error('❌ Webhook error:', error);
        return res.status(500).json({ message: 'Internal error' });
    }
}
