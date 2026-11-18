# 📘 Training Episode 3: Demand & Supply Zone Marking (Proximal & Distal Lines)
> **Source:** Mission Har Ghar GTF Trader 2.0 / Trading in the Zone (Arun Singh Tanwar)  
> **Topic:** 4 Structural Patterns, Leg-in/Base/Leg-out Rules, Exact Zone Marking (Proximal & Distal Lines), Freshness vs Tested Logic  
> **Status:** Ingested & Codified into Trading Assistant Engine

---

## 1. The 4 Structural Patterns of Demand & Supply

Every institutional zone on any timeframe falls into one of four patterns:

| Pattern | Type | Category | Structure | Leg-in Color | Leg-out Color | Nature |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DBR** | Demand | Reversal | Drop $\rightarrow$ Base $\rightarrow$ Rally | Any (Usually Red) | **Always Green Exciting** | Fights prior downtrend; high strength |
| **RBR** | Demand | Continuation | Rally $\rightarrow$ Base $\rightarrow$ Rally | Any (Usually Green) | **Always Green Exciting** | Trend continuation |
| **RBD** | Supply | Reversal | Rally $\rightarrow$ Base $\rightarrow$ Drop | Any (Usually Green) | **Always Red Exciting** | Fights prior uptrend; high strength |
| **DBD** | Supply | Continuation | Drop $\rightarrow$ Base $\rightarrow$ Drop | Any (Usually Red) | **Always Red Exciting** | Trend continuation |

---

## 2. The Three Structural Elements (1:1:1 Rule)

Every valid zone requires:
```text
[Leg-in Candle]  --->  [Base Candle(s)]  --->  [Leg-out Candle]
  (Exciting)         (1 to 6 Candles)            (Exciting)
```

1. **Leg-in:** Must be an **Exciting Candle** (Body $> 50\%$ of range). Can be red or green.
2. **Base:** $1 \text{ to } 6$ **Base Candles** (Body $< 50\%$ of range).
3. **Leg-out:** Must be an **Exciting Candle** (Body $> 50\%$ of range).
   - Demand: **Must be GREEN.**
   - Supply: **Must be RED.**
   - Must show strong departure velocity away from the basing area.

---

## 3. Mathematical Zone Marking Formulas

### A. Demand Zone (Look Left & Down below CMP)
* **Proximal Line (PL / Entry Reference):**  
  $$\mathbf{PL = \max(\text{Open}, \text{Close}) \text{ across all Base Candles}}$$
  *(Placed at the **Highest Body** of all base candles).*
* **Distal Line (DL / Stop-Loss Reference):**  
  $$\mathbf{DL = \min(\text{Low}) \text{ across all Base Candles}}$$
  *(Placed at the **Lowest Wick** of all base candles).*
* **Risk (Zone Width):**  
  $$\text{Zone Risk} = \text{PL} - \text{DL}$$

### B. Supply Zone (Look Left & Up above CMP)
* **Proximal Line (PL / Short Entry Reference):**  
  $$\mathbf{PL = \min(\text{Open}, \text{Close}) \text{ across all Base Candles}}$$
  *(Placed at the **Lowest Body** of all base candles).*
* **Distal Line (DL / Stop-Loss Reference):**  
  $$\mathbf{DL = \max(\text{High}) \text{ across all Base Candles}}$$
  *(Placed at the **Highest Wick** of all base candles).*
* **Risk (Zone Width):**  
  $$\text{Zone Risk} = \text{DL} - \text{PL}$$

---

## 4. Freshness vs. Tested Zones (The Golden Filter)

An institutional zone is only tradeable if pending orders remain untouched:

* **Fresh Zone (Valid):**
  - Starting immediately after the first leg-out candle, price has **NEVER** returned to touch or enter the proximal line.
* **Tested Zone (Invalid / Discarded):**
  - If any subsequent candle's wick touches or pierces the Proximal Line ($\text{Low} \le \text{PL}$ for Demand, or $\text{High} \ge \text{PL}$ for Supply), pending orders have been absorbed.
  - The zone is marked **TESTED** and removed from active pending order consideration.
