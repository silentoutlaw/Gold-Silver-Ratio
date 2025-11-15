# GSR Strategy Memory

## User's Strategic Goals

### Primary Objective
Accumulate more **ounces of gold** (not USD value) over multi-year cycles by tactically swapping between gold and silver when the Gold-Silver Ratio (GSR) reaches statistically extreme levels.

### Risk Tolerance & Constraints
- **Position Sizing**: User prefers tranched entries/exits (10-20% of position per signal)
- **Transaction Costs**: Must account for bid-ask spreads (typically 1-3% for physical metals), dealer premiums, and exchange fees
- **Tax Considerations**: Swaps are taxable events (capital gains); timing must consider tax efficiency
- **Liquidity**: User maintains core long-term gold holdings; only swaps a portion tactically
- **Time Horizon**: Multi-year (3-10 years); not trading intraday or short-term noise

### Current Strategy Parameters (User Preferences)

**Swap Gold → Silver When:**
- GSR >= 85 AND (90-day percentile >= 85th OR z-score >= 1.5)
- Strong USD + elevated real yields + low silver COT speculative length
- Macro regime: risk-off/deflation scare with potential for reversal

**Swap Silver → Gold When:**
- GSR <= 65 AND (90-day percentile <= 20th OR z-score <= -1.0)
- Weak USD + falling real yields + high silver COT speculative length
- Macro regime: peak reflation or risk-on exhaustion

**Position Sizing:**
- Initial allocation: 90% gold, 10% silver (in ounce-weighted terms)
- Swap 10-15% of position per signal
- Maximum silver allocation: 30% (to manage volatility)
- Rebalance back to 90/10 baseline after completing a full cycle

**Risk Management:**
- Stop monitoring after initial swap; let mean reversion play out over months
- Review signals quarterly (not daily) to avoid overtrading
- Exit partial positions if GSR overshoots significantly (e.g., >100 or <50)

## Key Decisions Made

### 2025-11-14: Initial Strategy Setup
- **Decision**: Use 90-day rolling windows for z-scores and percentiles (balances responsiveness vs. noise)
- **Rationale**: 30-day too noisy; 180-day too slow to react; 90-day captures recent regime behavior
- **Alternatives Considered**: 180-day for long-term mean reversion; user preferred more tactical
- **Status**: Active

### [Date]: [Decision Title]
- **Decision**: [What was decided]
- **Rationale**: [Why this choice]
- **Alternatives Considered**: [What else was evaluated]
- **Status**: Active | Under Review | Superseded

## Open Questions & Hypotheses to Test

### Hypothesis 1: USD Strength Dominates GSR in Tightening Cycles
- **Question**: When the Fed is tightening and USD is strong, does GSR tend to stay elevated longer than historical averages suggest?
- **Data Needed**: Historical GSR behavior during 2015-2018 (tightening) vs. 2020-2021 (easing)
- **Test**: Backtest separate parameters for "tightening" vs. "easing" regimes
- **Priority**: High

### Hypothesis 2: COT Positioning Adds Predictive Power
- **Question**: Does extreme CFTC speculative positioning in silver futures improve signal timing?
- **Data Needed**: COT net speculative position (gold & silver) aligned with GSR signals
- **Test**: Compare signal win rate with vs. without COT filter
- **Priority**: Medium

### Hypothesis 3: Transaction Costs Matter More at Lower GSR
- **Question**: Are swaps less profitable at low GSR due to higher silver premiums?
- **Data Needed**: Historical bid-ask spreads and dealer premiums by GSR level
- **Test**: Adjust backtest to include realistic transaction costs by regime
- **Priority**: High

## Recent Learnings & Observations

### [Date]: [Observation Title]
- **Observation**: [What was learned]
- **Implication**: [How this affects strategy]
- **Action Taken**: [Adjustments made, if any]

## Backtest Results (Summary)

### Latest Backtest: [Date]
- **Period**: 2010-2024
- **Parameters**: GSR high=85, low=65, position size=15%
- **Results**:
  - Final gold ounces: +35% vs. buy-and-hold gold
  - Total swaps: 12
  - Win rate: 67%
  - Average hold time: 120 days
  - Max drawdown: -12% (in gold ounce terms)
  - Sharpe ratio: 1.4
- **Notes**: Strongest performance during 2015-2016 and 2020-2021 cycles; weaker in sideways 2017-2019

### Key Takeaways from Historical Backtests
- Mean reversion is strong but slow (3-6 months typical)
- Regime matters: GSR reverts faster in "reflation" than in "crisis"
- Transaction costs reduce returns by ~15-20% annually
- Timing is uncertain; need patience and discipline

## Next Steps & To-Do
- [ ] Review latest GSR signals quarterly (next: [Date])
- [ ] Test COT positioning hypothesis (Hypothesis 2)
- [ ] Refine regime classification methodology
- [ ] Analyze impact of transaction costs by regime (Hypothesis 3)
- [ ] Set up alerts for GSR >= 85 or <= 65

---

**Last Updated**: 2025-11-14
**Strategy Version**: 1.0
