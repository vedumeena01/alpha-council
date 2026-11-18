# 📘 Training Episode 1: Best Charting Software & Candlestick Mechanics
> **Source:** Mission Har Ghar GTF Trader 2.0 / Trading in the Zone (Lead Trainer: Arun Singh Tanwar)  
> **Topic:** Charting Platforms, Workspace Setup, NSE Market Day Partitioning, Candlestick Anatomy & Psychological Discipline  
> **Status:** Ingested & Codified into Memory

---

## 1. Core Psychological Ground Rules & Discipline

1. **Noise Elimination Protocol:**
   - Uninstall speculative tip, social media, and advisory trading apps.
   - Stop watching financial TV channels (CNBC, Zee Business). Price discounts all public information immediately; media narratives induce hesitation and FOMO.
2. **20-Day Complete Trading Freeze:**
   - Stop taking active swing, intraday, and F&O trades during the learning phase.
   - Closes open speculative positions to clear mental baggage.
3. **The Trading Disparity (Psychology & Sizing):**
   - The same technical setup yields completely different results depending on capital size and sizing.
   - Undercapitalized accounts suffer emotional distress and take early ₹500 exits; institutional accounts execute methodically without emotional attachment.
4. **Boredom as a Hallmark of Profitability:**
   - Real, authentic trading is repetitive, disciplined, and mechanical—not a dopamine-driven adrenaline rush.

---

## 2. Institutional Charting & Platform Mechanics

### A. The 375-Minute NSE Session Partitioning (75m & 125m Charts)
* **The Problem with Standard 60-Minute Charts:**
  - NSE Trading Hours: `09:15 AM to 03:30 PM` = 6 hours 15 minutes = **375 minutes**.
  - If you use 60-minute candles: $375 \div 60 = 6$ full candles + **1 orphan 15-minute candle** (15:15 to 15:30). This distorts indicators, ATR, and candle comparisons.
* **The Solution (GTF Timeframes):**
  - **75-Minute Timeframe:** $375 \div 75 = \mathbf{5 \text{ equal bars per day}}$ (9:15-10:30, 10:30-11:45, 11:45-13:00, 13:00-14:15, 14:15-15:30).
  - **125-Minute Timeframe:** $375 \div 125 = \mathbf{3 \text{ equal bars per day}}$ (9:15-11:20, 11:20-13:25, 13:25-15:30).
* **Platform Support:** Trade Tiger & Dhan provide custom 75m and 125m intervals for free; TradingView requires a paid tier.

### B. Custom Fibonacci / Zone Division
* Delete traditional standard Fibonacci levels (`23.6%`, `38.2%`, `50%`, `61.8%`, `161.8%`).
* Keep only:
  - `0.00`
  - `33.33` (One-third zone boundary)
  - `66.66` (Two-thirds zone boundary)
  - `100.00`
* **Purpose:** Divides price ranges into exact structural thirds (Origin / Base / Leg-out or Deep vs Shallow Zone penetration).

### C. Clean Workspace Setup
* Background: White, Foreground/Crosshair: Black.
* Disable clutter: Remove volume panel, peak average, previous open/high/low/close lines.
* Standardized execution markings:
  - **Entry Line:** Black (Thickness 3)
  - **Stop-Loss Line:** Red (Thickness 3)
  - **Target Line:** Green (Thickness 3)

---

## 3. Candlestick Anatomy & Price Mechanics

* **OHLC Points:**
  - **High:** Extreme upper tip of the upper wick.
  - **Low:** Extreme lower tip of the lower wick.
  - **Green (Bullish):** Close > Open (Lower boundary = Open, Upper boundary = Close).
  - **Red (Bearish):** Close < Open (Upper boundary = Open, Lower boundary = Close).
* **Wickless Candles (Directional Aggression):**
  - **No Lower Wick:** $\text{Open} = \text{Low} \implies$ Buyers were aggressive right from the opening tick; price never traded below open.
  - **No Upper Wick:** $\text{Open} = \text{High} \implies$ Sellers took complete control immediately from open; price never ticked above open.
* **Wick (Rejection / Absorption) Mechanics:**
  - **Long Lower Wick:** Price was pushed down aggressively by bears, but institutional demand absorbed all sell orders and forced price back up before the close.
  - **Long Upper Wick:** Bulls tried to rally, but overhead supply knocked price back down.

---

## 4. Alignment with AlphaCouncil Quantitative Architecture

| GTF Episode 1 Principle | AlphaCouncil Codified Mechanism | System File |
| :--- | :--- | :--- |
| **No-News / Pure Price Focus** | Strict completed-bar $t$ evaluation; execution at $t+1$ Open. Zero news sentiment contamination. | `alphacouncil/alpha/sweep_detector.py` |
| **Clean Entry / SL / Target lines** | Idempotent OMS with deterministic GTT Bracket orders (linked SL-M and Target legs). | `alphacouncil/execution/oms.py` |
| **Equal Time Partitioning** | 375-min NSE session awareness; prevents synthetic bar mismatch. | `alphacouncil/data/feed.py` |
| **Capital Disparity & Sizing Emotion** | Volatility-Targeted fractional Kelly sizing; calculates exact integer shares to decouple emotion from risk. | `alphacouncil/risk/sizing.py` |
| **Wick Absorption Logic** | Sweep detector identifies stops swept below prior swing low with close returning inside range. | `alphacouncil/alpha/sweep_detector.py` |
