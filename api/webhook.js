// /api/webhook.js
export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ message: 'Method not allowed' });
    }

    try {
        const payload = req.body;
        const email = payload.metadata?.customerEmail || payload.metadata?.email || payload.memo;
        const status = payload.status || payload.event;
        const amount = payload.amount?.amount || payload.quote?.crypto_amount;
        const currency = payload.amount?.currency || payload.quote?.crypto_currency;

        if ((status === 'completed' || status === 'confirmed') && 
            parseFloat(amount) >= 0.01 && 
            currency === 'SOL' && 
            email) {
            
            console.log(`✅ Payment confirmed for: ${email}`);
            // Trigger your Python pipeline (via external service, GitHub Action, etc.)
            // For now, we log and acknowledge
            return res.status(200).json({ message: 'Payment confirmed', email });
        }

        return res.status(200).json({ message: 'Webhook received' });

    } catch (error) {
        console.error('❌ Webhook error:', error);
        return res.status(500).json({ message: 'Internal error' });
    }
}
