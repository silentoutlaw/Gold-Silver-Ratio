# Macro Regime Analysis Memory

## Current Regime Assessment (As of Latest Data)

### Regime Classification: [To Be Determined by System]
**Start Date**: [Auto-populated]
**Duration**: [Auto-calculated]

**Characteristics:**
- **Real Yields**: [Rising/Falling/Stable] - [Current level]
- **USD Strength (DXY)**: [Strong/Neutral/Weak] - [Current level]
- **Inflation Trend**: [Accelerating/Stable/Decelerating] - [Latest CPI/PCE]
- **Fed Policy Stance**: [Tightening/Neutral/Easing] - [Fed Funds Rate]
- **Risk Sentiment (VIX)**: [Elevated/Normal/Low] - [Current VIX]
- **Growth Indicators**: [Expanding/Stable/Contracting] - [Unemployment, PMI]

**Typical GSR Behavior in This Regime:**
- **Historical Range**: [Min-Max GSR]
- **Mean GSR**: [Average]
- **Volatility**: [Std Dev]
- **Reversion Tendency**: [Strong/Moderate/Weak]

## Historical Regime Library

### Regime 1: COVID Crisis (Mar 2020 - May 2020)
**Type**: Crisis / Panic
**Duration**: ~2 months

**Characteristics:**
- Real yields: Plunging (negative)
- USD: Initially strong (safe haven), then weakened
- Fed policy: Emergency easing (rates to zero, QE)
- Risk sentiment: Extreme fear (VIX 80+)
- Growth: Sharp contraction

**GSR Behavior:**
- **Peak GSR**: ~125 (March 2020 peak panic)
- **Mean GSR**: 110
- **Reversion**: Extremely fast (2-3 months back to 95)
- **Silver Performance**: Massively outperformed gold after panic subsided

**Lessons:**
- Extreme GSR spikes in crisis are excellent swap opportunities (if you can act)
- Silver underperforms initially but rebounds violently in reflation
- Liquidity matters: physical premiums spiked during crisis

---

### Regime 2: Reflation Era (Jun 2020 - Dec 2021)
**Type**: Risk-On Reflation with Weak USD
**Duration**: ~18 months

**Characteristics:**
- Real yields: Negative/low
- USD: Weak (DXY 89-93)
- Fed policy: Extremely accommodative (zero rates, massive QE)
- Risk sentiment: Improving (VIX 15-25)
- Growth: Strong recovery, stimulus-driven

**GSR Behavior:**
- **Range**: 95 → 65 (trending lower)
- **Mean GSR**: 75
- **Volatility**: Moderate
- **Silver Performance**: Outperformed gold significantly

**Lessons:**
- Low real yields + weak USD = ideal for silver
- GSR mean reverted from COVID highs over 12-18 months
- Best period for gold→silver swaps in decade

---

### Regime 3: Tightening Cycle (2022 - Mid 2023)
**Type**: Aggressive Fed Tightening + Strong USD
**Duration**: ~18 months

**Characteristics:**
- Real yields: Surging (negative → +2%)
- USD: Very strong (DXY 95-115)
- Fed policy: Fastest tightening in 40 years (rates 0% → 5.25%)
- Risk sentiment: Volatile (inflation fears → recession fears)
- Growth: Slowing

**GSR Behavior:**
- **Range**: 75 → 90
- **Mean GSR**: 83
- **Trend**: Rising (gold held up better than silver)
- **Volatility**: High

**Lessons:**
- Strong USD + rising real yields pressure silver more than gold
- GSR tends to rise and stay elevated in tightening cycles
- Be patient: mean reversion takes longer in this regime
- Silver→gold swaps worked well in this environment

---

### Regime 4: [Current/Next Regime - To Be Classified]
**Type**: [TBD]
**Duration**: [TBD]

**Characteristics:**
- [To be filled in by system based on latest data]

**GSR Behavior:**
- [To be analyzed as data accumulates]

## Regime Transition Signals

### Indicators to Watch for Regime Shifts

**From Tightening → Easing:**
- Fed pivots (pauses hikes, signals cuts)
- Real yields peak and start declining
- USD weakens (DXY breaks down)
- Credit spreads widen (recession fears)
- **Expected GSR Impact**: Initial spike (crisis), then sharp decline (reflation)

**From Reflation → Tightening:**
- Inflation accelerates beyond Fed comfort zone
- Fed turns hawkish (forward guidance shifts)
- Real yields start rising
- USD strengthens
- **Expected GSR Impact**: Gradual rise, silver underperforms

**From Normal → Crisis:**
- VIX spikes >40
- Credit markets seize up (HY spreads blow out)
- Equity drawdown >15% in short period
- Flight to quality (Treasuries rally hard)
- **Expected GSR Impact**: Sharp spike to 100-130+

## Correlation Insights

### Key Macro Correlations with GSR (Typical)

| Variable | 90-Day Correlation | Interpretation |
|----------|-------------------|----------------|
| DXY (USD Index) | +0.50 to +0.70 | Strong USD → higher GSR |
| 10Y Real Yield | +0.40 to +0.60 | Higher real yields → higher GSR |
| CPI YoY | -0.20 to +0.20 | Weak/variable; depends on context |
| WTI Oil | -0.30 to -0.50 | Higher oil → lower GSR (reflation) |
| S&P 500 | -0.40 to -0.60 | Risk-on → lower GSR |
| VIX | +0.50 to +0.70 | Fear → higher GSR |

**Note**: Correlations are not stable; they shift with regimes. Always check current rolling correlations via system tools.

### Regime-Dependent Correlation Changes
- **During Crisis**: VIX/GSR correlation strengthens (to +0.8)
- **During Reflation**: Oil/GSR correlation strengthens (to -0.7)
- **During Tightening**: DXY/GSR and RealYield/GSR strengthen

## Decision Rules for Regime-Aware Signals

### Enhanced Signal Logic (Regime-Adjusted)

**Swap Gold → Silver (High GSR):**
- **Base Condition**: GSR >= 85 AND percentile >= 85th
- **Regime Boost**:
  - +10 confidence if: VIX spiking (crisis nearing end)
  - +10 confidence if: Real yields peaking (Fed pivot soon)
  - +10 confidence if: USD overbought (DXY >105)
- **Regime Warning**:
  - -10 confidence if: Still in early tightening cycle
  - -10 confidence if: Inflation accelerating (Fed more aggressive ahead)

**Swap Silver → Gold (Low GSR):**
- **Base Condition**: GSR <= 65 AND percentile <= 20th
- **Regime Boost**:
  - +10 confidence if: Fed turning hawkish
  - +10 confidence if: Real yields starting to rise
  - +10 confidence if: Risk-off beginning (VIX rising)
- **Regime Warning**:
  - -10 confidence if: Still early in reflation (more upside for silver)
  - -10 confidence if: USD extremely weak (further to fall)

## To-Do & Research Questions

- [ ] Classify current regime (quarterly review)
- [ ] Update correlation matrix with latest 90-day data
- [ ] Compare current regime to historical analogs
- [ ] Identify early warning signals for next regime transition
- [ ] Test: Do regime-adjusted signals improve backtest win rate?

---

**Last Updated**: 2025-11-14
**Regime Methodology Version**: 1.0
