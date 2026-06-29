// api/verify-and-fulfill.js
import { exec } from 'child_process';

export default async function handler(req, res) {
    // Allow only POST requests
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Extract email from the request body
        const email = req.body?.data?.customer?.email || req.body?.customerEmail;

        if (!email) {
            return res.status(400).json({ error: 'Email not found in payload' });
        }

        console.log(`📧 Email received: ${email}`);

        // Trigger the delivery bot using `exec` from 'child_process'
        // Using a relative path. Vercel's environment should have `python` available.
        const command = `python delivery_bot.py ${email}`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ Execution error: ${error.message}`);
                return;
            }
            if (stderr) {
                console.error(`⚠️ stderr: ${stderr}`);
            }
            console.log(`✅ stdout: ${stdout}`);
        });

        // Respond immediately to acknowledge the webhook
        res.status(200).json({ success: true, email: email });

    } catch (error) {
        console.error('❌ Webhook error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}
