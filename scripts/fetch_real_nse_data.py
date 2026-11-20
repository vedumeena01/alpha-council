"""
Real NSE Market Data Ingestion & Cache Engine.
Fetches authentic historical daily OHLCV bars directly for liquid NSE constituents,
computes point-in-time ATR14, ADV20, and circuit limits, and converts them into
AlphaCouncil Bar objects.
"""

import os
import json
import datetime
import requests
import numpy as np
from typing import Dict, List, Optional

from alphacouncil.data.feed import Bar

DEFAULT_REAL_SYMBOLS = [
    "RELIANCE",
    "INFY",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "LT",
    "ITC",
    "TATAMOTORS",
]

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "alphacouncil",
    "data",
    "real_cache"
)


def fetch_nse_symbol_bars(symbol: str, range_str: str = "2y") -> List[Bar]:
    """
    Fetches real historical daily bars for an NSE symbol via Yahoo Finance,
    handling NSE ticker suffix (.NS) and computing rolling indicators.
    """
    ticker = f"{symbol}.NS"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={range_str}&interval=1d"

    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch data for {ticker}: HTTP {resp.status_code}")

    data = resp.json()["chart"]["result"][0]
    timestamps = data["timestamp"]
    quote = data["indicators"]["quote"][0]

    raw_opens = quote.get("open", [])
    raw_highs = quote.get("high", [])
    raw_lows = quote.get("low", [])
    raw_closes = quote.get("close", [])
    raw_volumes = quote.get("volume", [])

    # Filter out null / holiday bars
    valid_indices = [
        i for i in range(len(timestamps))
        if raw_opens[i] is not None
        and raw_highs[i] is not None
        and raw_lows[i] is not None
        and raw_closes[i] is not None
        and raw_volumes[i] is not None
    ]

    dates = [
        datetime.datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
        for i in valid_indices
    ]
    opens = [float(raw_opens[i]) for i in valid_indices]
    highs = [float(raw_highs[i]) for i in valid_indices]
    lows = [float(raw_lows[i]) for i in valid_indices]
    closes = [float(raw_closes[i]) for i in valid_indices]
    volumes = [float(raw_volumes[i]) for i in valid_indices]

    n_bars = len(valid_indices)
    bars: List[Bar] = []

    for i in range(n_bars):
        # Rolling 14-day ATR calculation
        if i >= 14:
            tr_list = [
                max(
                    highs[j] - lows[j],
                    abs(highs[j] - closes[j - 1]),
                    abs(lows[j] - closes[j - 1]),
                )
                for j in range(i - 13, i + 1)
            ]
            atr14 = float(np.mean(tr_list))
        else:
            atr14 = float(highs[i] - lows[i])

        # 20-day Rolling ADV
        start_idx = max(0, i - 19)
        adv20 = float(np.mean(volumes[start_idx : i + 1]))

        # Dynamic Circuit Limits (10% standard NSE F&O daily bands)
        prior_close = closes[i - 1] if i > 0 else opens[i]
        upper_circuit = round(prior_close * 1.10, 2)
        lower_circuit = round(prior_close * 0.90, 2)

        bar = Bar(
            timestamp=dates[i],
            symbol=symbol,
            open=round(opens[i], 2),
            high=round(highs[i], 2),
            low=round(lows[i], 2),
            close=round(closes[i], 2),
            volume=round(volumes[i], 0),
            upper_circuit=upper_circuit,
            lower_circuit=lower_circuit,
            atr14=round(atr14, 2),
            adv20=round(adv20, 0),
        )
        bars.append(bar)

    return bars


def cache_real_nse_universe(
    symbols: Optional[List[str]] = None,
    range_str: str = "2y",
) -> Dict[str, List[Bar]]:
    """
    Downloads and caches real historical market data for the target NSE universe.
    Saves to JSON for local instant re-loading and offline audit.
    """
    if symbols is None:
        symbols = DEFAULT_REAL_SYMBOLS

    os.makedirs(CACHE_DIR, exist_ok=True)
    universe_data: Dict[str, List[Bar]] = {}

    for sym in symbols:
        cache_path = os.path.join(CACHE_DIR, f"{sym}_{range_str}.json")
        try:
            print(f"Fetching real NSE market data for {sym} ({range_str})...")
            bars = fetch_nse_symbol_bars(sym, range_str=range_str)
            universe_data[sym] = bars

            # Serialize to disk
            serializable = [b.__dict__ for b in bars]
            with open(cache_path, "w") as f:
                json.dump(serializable, f, indent=2)
            print(f"  -> Successfully cached {len(bars)} daily bars for {sym} to {cache_path}")
        except Exception as e:
            print(f"  -> Error fetching {sym}: {e}")
            if os.path.exists(cache_path):
                print(f"  -> Falling back to cached data at {cache_path}")
                with open(cache_path) as f:
                    cached = json.load(f)
                universe_data[sym] = [Bar(**item) for item in cached]

    return universe_data


def load_cached_real_nse_universe(
    symbols: Optional[List[str]] = None,
    range_str: str = "2y",
) -> Dict[str, List[Bar]]:
    """Loads previously cached real market data from disk."""
    if symbols is None:
        symbols = DEFAULT_REAL_SYMBOLS

    universe_data: Dict[str, List[Bar]] = {}
    for sym in symbols:
        cache_path = os.path.join(CACHE_DIR, f"{sym}_{range_str}.json")
        if not os.path.exists(cache_path):
            raise FileNotFoundError(f"No cache found at {cache_path}. Run cache_real_nse_universe first.")
        with open(cache_path) as f:
            cached = json.load(f)
        universe_data[sym] = [Bar(**item) for item in cached]

    return universe_data


if __name__ == "__main__":
    data = cache_real_nse_universe(range_str="2y")
    print(f"\nCompleted ingestion of {len(data)} NSE symbols.")
    for sym, bars in data.items():
        print(f"  {sym:12} | Bars: {len(bars):3} | Start: {bars[0].timestamp} (Close ₹{bars[0].close:,.2f}) | End: {bars[-1].timestamp} (Close ₹{bars[-1].close:,.2f})")
