#!/usr/bin/env python3
"""
data_collector.py
Multi-Source Financial Data Aggregator
Sources: CoinGecko, CoinMarketCap, Polygon.io, Finnhub, FMP, SEC EDGAR,
         FRED, Messari, DefiLlama, yfinance
Cross-validates prices between independent sources to catch discrepancies.
"""

import os
import json
import logging
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DataCollector")

# ── API Keys (loaded from environment) ────────────────────────────────────────
COINGECKO_KEY   = os.getenv("COINGECKO_API_KEY", "")
CMC_KEY         = os.getenv("COINMARKETCAP_API_KEY", "")
POLYGON_KEY     = os.getenv("POLYGON_API_KEY", "")
FINNHUB_KEY     = os.getenv("FINNHUB_API_KEY", "")
FMP_KEY         = os.getenv("FMP_API_KEY", "")
FRED_KEY        = os.getenv("FRED_API_KEY", "")
MESSARI_KEY     = os.getenv("MESSARI_API_KEY", "")
ALPHA_VANTAGE   = os.getenv("ALPHA_VANTAGE_API_KEY", "")

# ── Target Assets ─────────────────────────────────────────────────────────────
CRYPTO_ASSETS = {
    "bitcoin":  "BTC",
    "ethereum": "ETH",
    "solana":   "SOL",
    "binancecoin": "BNB",
}

EQUITY_TICKERS = {
    "AI_Hardware":        ["NVDA", "AMD", "TSM", "AVGO", "INTC"],
    "Data_Centers":       ["DLR", "EQIX", "MSFT", "AMZN", "GOOGL"],
    "Semiconductors":     ["SMH", "ASML", "AMAT", "LRCX", "KLAC"],
    "Uranium_Energy":     ["URA", "CCJ", "NXE", "URG"],
    "Grid_Power":         ["NEE", "XLU", "AES", "PCG"],
    "Macro_Liquidity":    ["TLT", "UUP", "GLD", "SHY"],
    "DePIN_Compute":      ["HUT", "CLSK", "CORZ"],
    "Cloud_SaaS":         ["CRM", "NOW", "SNOW", "DDOG"],
}

FRED_SERIES = {
    "fed_funds_rate":     "FEDFUNDS",
    "cpi_inflation":      "CPIAUCSL",
    "unemployment":       "UNRATE",
    "10y_treasury":       "DGS10",
    "2y_treasury":        "DGS2",
    "m2_money_supply":    "M2SL",
    "gdp_growth":         "A191RL1Q225SBEA",
}


def _fetch(url: str, headers: dict = None, timeout: int = 10) -> Optional[dict]:
    """Generic JSON fetcher with error handling."""
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        logger.warning(f"Fetch failed [{url[:60]}...]: {e}")
        return None


# ── Source 1: CoinGecko ───────────────────────────────────────────────────────
def fetch_coingecko() -> dict:
    ids = ",".join(CRYPTO_ASSETS.keys())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
    if COINGECKO_KEY:
        url += f"&x_cg_demo_api_key={COINGECKO_KEY}"
    data = _fetch(url)
    if not data:
        return {}
    result = {}
    for coin_id, symbol in CRYPTO_ASSETS.items():
        if coin_id in data:
            result[symbol] = {
                "price_usd":        data[coin_id].get("usd", 0),
                "change_24h_pct":   data[coin_id].get("usd_24h_change", 0),
                "market_cap":       data[coin_id].get("usd_market_cap", 0),
                "source":           "CoinGecko",
            }
    logger.info(f"CoinGecko: fetched {len(result)} assets")
    return result


# ── Source 2: CoinMarketCap ───────────────────────────────────────────────────
def fetch_coinmarketcap() -> dict:
    if not CMC_KEY:
        logger.warning("CoinMarketCap: no API key, skipping")
        return {}
    symbols = ",".join(CRYPTO_ASSETS.values())
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbols}&convert=USD"
    data = _fetch(url, headers={"X-CMC_PRO_API_KEY": CMC_KEY, "Accept": "application/json"})
    if not data or "data" not in data:
        return {}
    result = {}
    for symbol in CRYPTO_ASSETS.values():
        if symbol in data["data"]:
            quote = data["data"][symbol]["quote"]["USD"]
            result[symbol] = {
                "price_usd":      quote.get("price", 0),
                "change_24h_pct": quote.get("percent_change_24h", 0),
                "market_cap":     quote.get("market_cap", 0),
                "volume_24h":     quote.get("volume_24h", 0),
                "source":         "CoinMarketCap",
            }
    logger.info(f"CoinMarketCap: fetched {len(result)} assets")
    return result


# ── Source 3: Polygon.io (equities) ──────────────────────────────────────────
def fetch_polygon(ticker: str) -> Optional[dict]:
    if not POLYGON_KEY:
        return None
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={POLYGON_KEY}"
    data = _fetch(url)
    if not data or data.get("resultsCount", 0) == 0:
        return None
    r = data["results"][0]
    return {
        "price_usd":      r.get("c", 0),
        "open":           r.get("o", 0),
        "high":           r.get("h", 0),
        "low":            r.get("l", 0),
        "volume_24h":     r.get("v", 0),
        "change_24h_pct": round(((r.get("c",0) - r.get("o",0)) / r.get("o",1)) * 100, 2),
        "source":         "Polygon.io",
    }


# ── Source 4: Finnhub (equities + news sentiment) ────────────────────────────
def fetch_finnhub(ticker: str) -> Optional[dict]:
    if not FINNHUB_KEY:
        return None
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
    data = _fetch(url)
    if not data or data.get("c", 0) == 0:
        return None
    return {
        "price_usd":      data.get("c", 0),
        "open":           data.get("o", 0),
        "high":           data.get("h", 0),
        "low":            data.get("l", 0),
        "prev_close":     data.get("pc", 0),
        "change_24h_pct": round(((data.get("c",0) - data.get("pc",1)) / data.get("pc",1)) * 100, 2),
        "source":         "Finnhub",
    }


# ── Source 5: Financial Modeling Prep (fundamentals) ─────────────────────────
def fetch_fmp(ticker: str) -> Optional[dict]:
    if not FMP_KEY:
        return None
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_KEY}"
    data = _fetch(url)
    if not data or not isinstance(data, list) or len(data) == 0:
        return None
    d = data[0]
    return {
        "price_usd":        d.get("price", 0),
        "market_cap":       d.get("marketCap", 0),
        "pe_ratio":         d.get("pe", 0),
        "eps":              d.get("eps", 0),
        "change_24h_pct":   d.get("changesPercentage", 0),
        "volume_24h":       d.get("volume", 0),
        "avg_volume":       d.get("avgVolume", 0),
        "52w_high":         d.get("yearHigh", 0),
        "52w_low":          d.get("yearLow", 0),
        "source":           "Financial Modeling Prep",
    }


# ── Source 6: FRED (macro economic data) ─────────────────────────────────────
def fetch_fred() -> dict:
    if not FRED_KEY:
        logger.warning("FRED: no API key, skipping")
        return {}
    result = {}
    for name, series_id in FRED_SERIES.items():
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_KEY}&file_type=json&limit=1&sort_order=desc"
        data = _fetch(url)
        if data and "observations" in data and len(data["observations"]) > 0:
            obs = data["observations"][0]
            try:
                result[name] = {
                    "value":  float(obs["value"]),
                    "date":   obs["date"],
                    "series": series_id,
                    "source": "FRED",
                }
            except (ValueError, KeyError):
                pass
        time.sleep(0.1)
    logger.info(f"FRED: fetched {len(result)} macro series")
    return result


# ── Source 7: Messari (crypto research data) ─────────────────────────────────
def fetch_messari(asset: str) -> Optional[dict]:
    headers = {}
    if MESSARI_KEY:
        headers["x-messari-api-key"] = MESSARI_KEY
    url = f"https://data.messari.io/api/v1/assets/{asset.lower()}/metrics"
    data = _fetch(url, headers=headers)
    if not data or "data" not in data:
        return None
    m = data["data"].get("market_data", {})
    roi = data["data"].get("roi_data", {})
    return {
        "price_usd":        m.get("price_usd", 0),
        "volume_last_24h":  m.get("volume_last_24h", 0),
        "real_volume_last_24h": m.get("real_volume_last_24h", 0),
        "percent_change_usd_last_24h": m.get("percent_change_usd_last_24h", 0),
        "roi_30d":          roi.get("percent_change_last_1_month", 0),
        "roi_1y":           roi.get("percent_change_last_1_year", 0),
        "source":           "Messari",
    }


# ── Source 8: DefiLlama (DeFi TVL) ───────────────────────────────────────────
def fetch_defillama() -> dict:
    url = "https://api.llama.fi/chains"
    data = _fetch(url)
    if not data or not isinstance(data, list):
        return {}
    top_chains = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:10]
    result = {}
    for chain in top_chains:
        name = chain.get("name", "Unknown")
        result[name] = {
            "tvl_usd":     chain.get("tvl", 0),
            "chain":       name,
            "source":      "DefiLlama",
        }
    logger.info(f"DefiLlama: fetched TVL for {len(result)} chains")
    return result


# ── Source 9: SEC EDGAR (recent filings) ─────────────────────────────────────
def fetch_sec_filings(ticker: str) -> Optional[dict]:
    """Pulls recent 10-K/10-Q filing metadata for a ticker."""
    url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2024-01-01&forms=10-K,10-Q"
    data = _fetch(url, headers={"User-Agent": "GlobalMarketIntelligenceMatrix research@gmim.io"})
    if not data:
        return None
    hits = data.get("hits", {}).get("hits", [])
    if not hits:
        return None
    latest = hits[0].get("_source", {})
    return {
        "ticker":       ticker,
        "filing_type":  latest.get("form_type", ""),
        "filed_at":     latest.get("file_date", ""),
        "entity_name":  latest.get("entity_name", ""),
        "source":       "SEC EDGAR",
    }


# ── Cross-Source Price Validator ──────────────────────────────────────────────
def cross_validate_prices(source_a: dict, source_b: dict, label: str) -> dict:
    """
    Compares prices between two independent sources.
    Flags discrepancies > 1% as warnings — these are meaningful cross-source divergences
    that Grok will be able to reference in the audit step.
    """
    discrepancies = {}
    for asset in source_a:
        if asset in source_b:
            price_a = source_a[asset].get("price_usd", 0)
            price_b = source_b[asset].get("price_usd", 0)
            if price_a > 0 and price_b > 0:
                diff_pct = abs(price_a - price_b) / price_a * 100
                if diff_pct > 1.0:
                    discrepancies[asset] = {
                        "source_a_price": price_a,
                        "source_b_price": price_b,
                        "divergence_pct": round(diff_pct, 3),
                        "flag":           "CROSS_SOURCE_DISCREPANCY",
                        "sources":        label,
                    }
                    logger.warning(f"⚠️  Price discrepancy for {asset}: {label} divergence {diff_pct:.2f}%")
    return discrepancies


# ── Main Collection Function ──────────────────────────────────────────────────
def collect_all_data() -> dict:
    logger.info("🚀 Starting multi-source data collection...")
    collected_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Crypto prices from two independent sources
    coingecko_crypto = fetch_coingecko()
    cmc_crypto = fetch_coinmarketcap()
    crypto_discrepancies = cross_validate_prices(coingecko_crypto, cmc_crypto, "CoinGecko vs CoinMarketCap")

    # Macro data from FRED
    macro_data = fetch_fred()

    # DeFi TVL from DefiLlama
    defi_tvl = fetch_defillama()

    # Messari research data for key assets
    messari_data = {}
    for asset in ["bitcoin", "ethereum", "solana"]:
        result = fetch_messari(asset)
        if result:
            messari_data[asset.upper()] = result
        time.sleep(0.2)

    # Equity data — two sources per ticker for cross-validation
    equity_data = {}
    equity_discrepancies = {}
    for category, tickers in EQUITY_TICKERS.items():
        for ticker in tickers:
            polygon_quote = fetch_polygon(ticker)
            finnhub_quote = fetch_finnhub(ticker)
            fmp_quote = fetch_fmp(ticker)

            # Use best available price, prefer Polygon → Finnhub → FMP
            primary = polygon_quote or finnhub_quote or fmp_quote
            if not primary:
                logger.warning(f"No equity data available for {ticker}, skipping")
                continue

            # Cross-validate if two sources available
            if polygon_quote and finnhub_quote:
                diff = abs(polygon_quote["price_usd"] - finnhub_quote["price_usd"]) / max(polygon_quote["price_usd"], 0.01) * 100
                if diff > 1.0:
                    equity_discrepancies[ticker] = {
                        "polygon_price":    polygon_quote["price_usd"],
                        "finnhub_price":    finnhub_quote["price_usd"],
                        "divergence_pct":   round(diff, 3),
                        "flag":             "CROSS_SOURCE_DISCREPANCY",
                        "sources":          "Polygon vs Finnhub",
                    }

            equity_data[ticker] = {
                **primary,
                "category":     category,
                "fmp_data":     fmp_quote,
                "polygon_data": polygon_quote,
                "finnhub_data": finnhub_quote,
            }
            time.sleep(0.15)  # Rate limit protection

    # SEC filings for major tickers
    sec_data = {}
    for ticker in ["NVDA", "MSFT", "GOOGL", "AMZN"]:
        filing = fetch_sec_filings(ticker)
        if filing:
            sec_data[ticker] = filing
        time.sleep(0.3)

    payload = {
        "collected_at":             collected_at,
        "crypto":                   coingecko_crypto,
        "crypto_cmc":               cmc_crypto,
        "crypto_messari":           messari_data,
        "crypto_discrepancies":     crypto_discrepancies,
        "equities":                 equity_data,
        "equity_discrepancies":     equity_discrepancies,
        "macro_fred":               macro_data,
        "defi_tvl":                 defi_tvl,
        "sec_filings":              sec_data,
        "source_count":             sum([
            bool(coingecko_crypto), bool(cmc_crypto), bool(macro_data),
            bool(defi_tvl), bool(messari_data), bool(equity_data), bool(sec_data)
        ]),
    }

    logger.info(f"✅ Data collection complete. Sources active: {payload['source_count']}/7")
    logger.info(f"   Crypto assets: {len(coingecko_crypto)} | Equities: {len(equity_data)} | Macro series: {len(macro_data)}")
    if crypto_discrepancies:
        logger.warning(f"   ⚠️  Crypto price discrepancies detected: {list(crypto_discrepancies.keys())}")
    if equity_discrepancies:
        logger.warning(f"   ⚠️  Equity price discrepancies detected: {list(equity_discrepancies.keys())}")

    return payload


if __name__ == "__main__":
    data = collect_all_data()
    print(json.dumps({k: v for k, v in data.items() if k != "equities"}, indent=2, default=str))
