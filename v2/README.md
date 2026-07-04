# Global Market Intelligence Matrix — v2

**Autonomous institutional-grade financial intelligence pipeline powered by DeepSeek V3 (writer) + Grok 3 (auditor).**

## Architecture

```
Customer → index2.html → Flask Server → Data Collector → DeepSeek → Grok → DeepSeek (loop) → Delivery Agent → Email
```

### Triple-Agent Pipeline
1. **Data Collection Agent** — aggregates from 15+ financial APIs simultaneously with cross-source price validation
2. **Analysis Agent (DeepSeek V3)** — writes dense 2,500+ word institutional research reports
3. **Audit Agent (Grok 3)** — verifies every claim against source data, scores quality 0-100, rejects until ≥95

## File Structure

```
v2/
├── index2.html                          # Frontend (self-contained, no build step)
├── Dockerfile                           # Container definition
├── docker-compose.yml                   # Multi-container orchestration
├── requirements.txt                     # Python dependencies
├── .env.example                         # API key template
├── backend/
│   └── bots/
│       ├── data_collector.py            # 15+ API data aggregation
│       ├── collaborative_writer.py      # DeepSeek + Grok iterative loop
│       └── delivery_agent.py           # PDF/HTML/CSV generation + Resend email
├── flask_server/
│   └── server.py                       # Stripe + crypto webhooks, checkout
└── .github/workflows/
    ├── report_generation_v2.yml         # Scheduled report pipeline
    └── cron_tracker_v2.yml             # Health monitoring
```

## Data Sources

| Source | Data Type | Free Tier |
|--------|-----------|-----------|
| CoinGecko | Crypto prices | ✅ Yes |
| CoinMarketCap | Crypto prices (cross-validation) | ✅ Yes |
| Polygon.io | Equity prices | ✅ Delayed |
| Finnhub | Equity prices + sentiment | ✅ Yes |
| Financial Modeling Prep | Fundamentals | ✅ Limited |
| FRED | Macro economic data | ✅ Free |
| Messari | Crypto research | ✅ Limited |
| DefiLlama | DeFi TVL | ✅ Free |
| SEC EDGAR | Company filings | ✅ Free |
| Alpha Vantage | Equities + forex | ✅ Limited |
| yfinance | Equities (backup) | ✅ Free |

## Setup

### 1. Clone and navigate to v2
```bash
cd Global-Market-Intelligence-Matrix/v2
```

### 2. Copy environment template
```bash
cp .env.example .env
# Edit .env with your real API keys
```

### 3. Add all API keys to GitHub Secrets
Go to: Settings → Secrets and variables → Actions → New repository secret

Required secrets:
- `COINGECKO_API_KEY`
- `COINMARKETCAP_API_KEY`
- `POLYGON_API_KEY`
- `FINNHUB_API_KEY`
- `FMP_API_KEY`
- `FRED_API_KEY`
- `MESSARI_API_KEY`
- `ALPHA_VANTAGE_API_KEY`
- `DEEPSEEK_API_KEY`
- `GROK_API_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_ID`
- `HELIO_WEBHOOK_SECRET`
- `HELIO_PAYMENT_URL`
- `RESEND_API_KEY`
- `FROM_EMAIL`
- `FLASK_SECRET_KEY`
- `SUCCESS_URL`
- `CANCEL_URL`

### 4. Run locally
```bash
pip install -r requirements.txt
python flask_server/server.py
```
Open `index2.html` in your browser.

### 5. Deploy to Docker
```bash
docker compose up -d
```

## Pricing

- **Single Report:** $2,500
- **Annual Subscription:** $27,000 (monthly delivery)

## Report Types

- Arbitrage Opportunity Matrix
- Predictive Correlation Analytics
- Quantitative Risk Assessment
- Market Manipulation Detection
- Weekly Market Intelligence Brief

## Migrating to Oracle Cloud

When your Oracle Cloud free-tier instance is ready:

```bash
# On Oracle instance
git clone https://github.com/ManOfMystery1981/Global-Market-Intelligence-Matrix.git
cd Global-Market-Intelligence-Matrix/v2
cp .env.example .env
# Add your keys to .env
docker compose up -d
```

Point your domain DNS to the Oracle instance IP and update `SUCCESS_URL` / `CANCEL_URL` accordingly.

## Disclaimer

This system produces AI-generated financial research for informational purposes only. It does not constitute investment advice. All reports are clearly disclosed as AI-generated and cross-validated by autonomous audit agents.
