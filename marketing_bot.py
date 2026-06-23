import os

def get_market_intelligence_teaser():
    """Surgically extracts only the primary repository titles from your data product."""
    try:
        with open('market_intelligence.md', 'r') as file:
            lines = file.readlines()
        
        # Look ONLY for main h2 elements (not h3 description blocks)
        project_names = []
        for line in lines:
            if line.startswith('## ') and "📦" not in line:
                name = line.replace('##', '').strip()
                if name:
                    project_names.append(name)
                    
        if project_names:
            return ' | '.join(project_names[:3])
        return "Latest Open-Source Global Trends Matrix"
    except FileNotFoundError:
        return "System Analytics Assembly Engine (Compiling...)"

def main():
    teaser = get_market_intelligence_teaser()
    
    PAY_URL = "solana:3rLapKiA4SfTQMMMFfkZSfkT12iFXQPiKv7w9mzqKZqh?amount=0.01&label=Global%20Market%20Intelligence%20Report&memo=Enter_Your_Email_In_Wallet_Memo"

    print("\n📣 --- NEW AUTOMATED CONTENT BROADCAST --- 📣")
    print(f"📈 Top 3 trending open-source projects this session:\n👉 {teaser}\n")
    print("💎 Want the full, deep-dive Technical Metrics Report mailed straight to your inbox?")
    print(f"🔗 Scan or click our secure Solana Pay Link to unlock instant delivery:\n👉 {PAY_URL}\n")
    print("⚠️ IMPORTANT: Type your destination email address directly into your wallet's 'MEMO' field before confirming the transfer so our delivery agent knows where to ship your report!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    main()
