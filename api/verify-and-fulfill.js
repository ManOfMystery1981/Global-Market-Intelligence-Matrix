export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const email = req.body?.data?.customer?.email || req.body?.customerEmail;
        console.log(`📧 Email: ${email}`);
        
        if (email) {
            const { exec } = require('child_process');
            exec(`python delivery_bot.py ${email}`, (error, stdout, stderr) => {
                if (error) console.error(`❌ Error: ${error}`);
                console.log(`✅ stdout: ${stdout}`);
                if (stderr) console.error(`⚠️ stderr: ${stderr}`);
            });
        }
        
        res.status(200).json({ success: true, email: email || 'none' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
}
