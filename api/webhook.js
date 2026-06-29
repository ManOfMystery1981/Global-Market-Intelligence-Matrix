import { Octokit } from "@octokit/rest";

const octokit = new Octokit({ auth: process.env.GITHUB_ACCESS_TOKEN });
const OWNER = "manofmystery1981";
const REPO = "Global-Market-Intelligence-Matrix";
const FILE_PATH = "subscribers.json";

// Helper function to read the raw request buffer stream from Vercel
async function getRequestBody(req) {
    const buffers = [];
    for await (const chunk of req) {
        buffers.push(chunk);
    }
    const rawBuffer = Buffer.concat(buffers).toString();
    return rawBuffer ? JSON.parse(rawBuffer) : {};
}

export default async function handler(req, res) {
    // Enforce strict method isolation
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Safely stream and parse the incoming JSON request body
        const payload = await getRequestBody(req);
        const { customer_email, payment_status } = payload;

        // Structural guard validation checks
        if (!customer_email) {
            return res.status(400).json({ error: 'Missing customer email parameter' });
        }
        if (payment_status !== 'paid') {
            return res.status(400).json({ error: 'Transaction status incomplete' });
        }

        // Fetch the target file data tracking layer from GitHub
        const { data: fileData } = await octokit.repos.getContent({ owner: OWNER, repo: REPO, path: FILE_PATH });
        const currentContent = Buffer.from(fileData.content, 'base64').toString('utf-8');
        let emailList = JSON.parse(currentContent);

        // Update list and commit changes back if email is unique
        if (!emailList.includes(customer_email)) {
            emailList.push(customer_email);
            const updatedContent = JSON.stringify(emailList, null, 2);
            await octokit.repos.createOrUpdateFileContents({
                owner: OWNER, repo: REPO, path: FILE_PATH,
                message: `system: add subscriber ${customer_email}`,
                content: Buffer.from(updatedContent).toString('base64'),
                sha: fileData.sha,
            });
        }
        return res.status(200).json({ status: 'success' });
    } catch (error) {
        console.error("❌ Pipeline Crash Exception:", error.message);
        return res.status(500).json({ error: 'Internal pipeline failure' });
    }
}
