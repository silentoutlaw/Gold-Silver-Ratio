"""
Backtesting engine for GSR swap strategies.
Simulates historical trading based on GSR signals.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.models import DerivedMetric, MetricValue

logger = logging.getLogger(__name__)


class BacktestConfig:
    """Backtest configuration."""

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        initial_gold_oz: float = 100.0,
        gsr_high_threshold: float = 85.0,
        gsr_low_threshold: float = 65.0,
        position_size_pct: float = 15.0,
        transaction_cost_pct: float = 0.02,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_gold_oz = initial_gold_oz
        self.gsr_high_threshold = gsr_high_threshold
        self.gsr_low_threshold = gsr_low_threshold
        self.position_size_pct = position_size_pct
        self.transaction_cost_pct = transaction_cost_pct


class Trade:
    """Represents a single trade."""

    def __init__(
        self,
        date: datetime,
        action: str,
        gsr: float,
        gold_oz_before: float,
        silver_oz_before: float,
        gold_oz_after: float,
        silver_oz_after: float,
        cost: float,
    ):
        self.date = date
        self.action = action
        self.gsr = gsr
        self.gold_oz_before = gold_oz_before
        self.silver_oz_before = silver_oz_before
        self.gold_oz_after = gold_oz_after
        self.silver_oz_after = silver_oz_after
        self.cost = cost


class BacktestResult:
    """Backtest results."""

    def __init__(
        self,
        config: BacktestConfig,
        final_gold_oz: float,
        trades: List[Trade],
        equity_curve: pd.DataFrame,
    ):
        self.config = config
        self.final_gold_oz = final_gold_oz
        self.trades = trades
        self.equity_curve = equity_curve

        # Calculate metrics
        self.gold_oz_gain = final_gold_oz - config.initial_gold_oz
        self.gold_oz_gain_pct = (
            (final_gold_oz / config.initial_gold_oz - 1) * 100
        )
        self.total_swaps = len(trades)
        self.winning_swaps = sum(
            1 for t in trades if self._is_winning_trade(t)
        )
        self.win_rate = (
            self.winning_swaps / self.total_swaps if self.total_swaps > 0 else 0.0
        )

        # Calculate max drawdown
        self.max_drawdown = self._calculate_max_drawdown(equity_curve)

        # Calculate Sharpe ratio
        self.sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)

    def _is_winning_trade(self, trade: Trade) -> bool:
        """Check if a trade was profitable."""
        # Simplified: check if gold oz increased after round-trip
        return trade.gold_oz_after > trade.gold_oz_before

    def _calculate_max_drawdown(self, equity_curve: pd.DataFrame) -> float:
        """Calculate maximum drawdown."""
        if equity_curve.empty:
            return 0.0

        cummax = equity_curve["total_gold_oz"].cummax()
        drawdown = (equity_curve["total_gold_oz"] - cummax) / cummax
        return float(drawdown.min())

    def _calculate_sharpe_ratio(self, equity_curve: pd.DataFrame) -> float:
        """Calculate Sharpe ratio (simplified daily returns)."""
        if len(equity_curve) < 2:
            return 0.0

        returns = equity_curve["total_gold_oz"].pct_change().dropna()
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        return float(returns.mean() / returns.std() * np.sqrt(252))  # Annualized

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "config": {
                "start_date": self.config.start_date,
                "end_date": self.config.end_date,
                "initial_gold_oz": self.config.initial_gold_oz,
                "gsr_high_threshold": self.config.gsr_high_threshold,
                "gsr_low_threshold": self.config.gsr_low_threshold,
                "position_size_pct": self.config.position_size_pct,
                "transaction_cost_pct": self.config.transaction_cost_pct,
            },
            "final_gold_oz": self.final_gold_oz,
            "gold_oz_gain": self.gold_oz_gain,
            "gold_oz_gain_pct": self.gold_oz_gain_pct,
            "total_swaps": self.total_swaps,
            "winning_swaps": self.winning_swaps,
            "win_rate": self.win_rate,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "trades": [
                {
                    "date": t.date,
                    "action": t.action,
                    "gsr": t.gsr,
                    "gold_oz_before": t.gold_oz_before,
                    "silver_oz_before": t.silver_oz_before,
                    "gold_oz_after": t.gold_oz_after,
                    "silver_oz_after": t.silver_oz_after,
                    "cost": t.cost,
                }
                for t in self.trades
            ],
            "equity_curve": self.equity_curve.to_dict(orient="records"),
        }


async def run_backtest(
    db: AsyncSession, config: BacktestConfig
) -> BacktestResult:
    """
    Run backtest simulation.

    Args:
        db: Database session
        config: Backtest configuration

    Returns:
        BacktestResult object
    """
    logger.info(f"Running backtest from {config.start_date} to {config.end_date}")

    # Get GSR data
    gsr_metric = await db.execute(
        select(DerivedMetric).where(DerivedMetric.name == "GSR")
    )
    gsr_metric = gsr_metric.scalar_one_or_none()

    if not gsr_metric:
        raise ValueError("GSR metric not found")

    # Get GSR values
    gsr_values = await db.execute(
        select(MetricValue)
        .where(
            and_(
                MetricValue.metric_id == gsr_metric.id,
                MetricValue.timestamp >= config.start_date,
                MetricValue.timestamp <= config.end_date,
            )
        )
        .order_by(MetricValue.timestamp)
    )
    gsr_values = gsr_values.scalars().all()

    if not gsr_values:
        raise ValueError("No GSR data found for backtest period")

    # Create DataFrame
    df = pd.DataFrame(
        [
            {
                "date": v.timestamp,
                "gsr": v.value,
                "gold_price": v.metadata.get("gold_price", 0)
                if v.metadata
                else 0,
                "silver_price": v.metadata.get("silver_price", 0)
                if v.metadata
                else 0,
            }
            for v in gsr_values
        ]
    )
    df.set_index("date", inplace=True)

    # Initialize positions
    gold_oz = config.initial_gold_oz
    silver_oz = 0.0
    trades = []
    equity_curve = []

    # Track state
    last_action = None

    # Simulate trading
    for date, row in df.iterrows():
        gsr = row["gsr"]
        gold_price = row["gold_price"]
        silver_price = row["silver_price"]

        # Calculate total gold equivalent
        total_gold_oz = gold_oz + (silver_oz * silver_price / gold_price)

        # Record equity
        equity_curve.append(
            {
                "date": date,
                "gold_oz": gold_oz,
                "silver_oz": silver_oz,
                "total_gold_oz": total_gold_oz,
                "gsr": gsr,
            }
        )

        # Check for signals
        if gsr >= config.gsr_high_threshold and last_action != "gold_to_silver":
            # Swap gold -> silver
            swap_amount_gold = gold_oz * (config.position_size_pct / 100.0)

            if swap_amount_gold > 0:
                # Apply transaction cost
                net_amount_gold = swap_amount_gold * (1 - config.transaction_cost_pct)
                silver_received = (net_amount_gold * gold_price) / silver_price

                gold_oz_before = gold_oz
                silver_oz_before = silver_oz

                gold_oz -= swap_amount_gold
                silver_oz += silver_received

                trades.append(
                    Trade(
                        date=date,
                        action="gold_to_silver",
                        gsr=gsr,
                        gold_oz_before=gold_oz_before,
                        silver_oz_before=silver_oz_before,
                        gold_oz_after=gold_oz,
                        silver_oz_after=silver_oz,
                        cost=swap_amount_gold * config.transaction_cost_pct,
                    )
                )

                last_action = "gold_to_silver"
                logger.debug(
                    f"{date}: Swapped {swap_amount_gold:.2f} oz gold -> {silver_received:.2f} oz silver at GSR {gsr:.1f}"
                )

        elif gsr <= config.gsr_low_threshold and last_action != "silver_to_gold":
            # Swap silver -> gold
            swap_amount_silver = silver_oz * (config.position_size_pct / 100.0)

            if swap_amount_silver > 0:
                # Apply transaction cost
                net_amount_silver = swap_amount_silver * (1 - config.transaction_cost_pct)
                gold_received = (net_amount_silver * silver_price) / gold_price

                gold_oz_before = gold_oz
                silver_oz_before = silver_oz

                silver_oz -= swap_amount_silver
                gold_oz += gold_received

                trades.append(
                    Trade(
                        date=date,
                        action="silver_to_gold",
                        gsr=gsr,
                        gold_oz_before=gold_oz_before,
                        silver_oz_before=silver_oz_before,
                        gold_oz_after=gold_oz,
                        silver_oz_after=silver_oz,
                        cost=swap_amount_silver
                        * silver_price
                        / gold_price
                        * config.transaction_cost_pct,
                    )
                )

                last_action = "silver_to_gold"
                logger.debug(
                    f"{date}: Swapped {swap_amount_silver:.2f} oz silver -> {gold_received:.2f} oz gold at GSR {gsr:.1f}"
                )

    # Calculate final gold equivalent
    final_gold_oz = gold_oz + (silver_oz * df.iloc[-1]["silver_price"] / df.iloc[-1]["gold_price"])

    # Create equity curve DataFrame
    equity_df = pd.DataFrame(equity_curve)

    result = BacktestResult(
        config=config,
        final_gold_oz=final_gold_oz,
        trades=trades,
        equity_curve=equity_df,
    )

    logger.info(
        f"Backtest complete: {result.gold_oz_gain_pct:.2f}% gain, "
        f"{result.total_swaps} trades, {result.win_rate:.2%} win rate"
    )

    return result


async def optimize_parameters(
    db: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    param_ranges: Dict[str, List[float]],
) -> Dict[str, Any]:
    """
    Optimize strategy parameters using grid search.

    Args:
        db: Database session
        start_date: Backtest start date
        end_date: Backtest end date
        param_ranges: Dictionary of parameter ranges to test

    Returns:
        Dictionary with optimal parameters and results
    """
    logger.info("Starting parameter optimization")

    best_result = None
    best_params = None
    all_results = []

    # Grid search
    for high_threshold in param_ranges.get("gsr_high", [85.0]):
        for low_threshold in param_ranges.get("gsr_low", [65.0]):
            for position_size in param_ranges.get("position_size", [15.0]):
                for tx_cost in param_ranges.get("transaction_cost", [0.02]):
                    config = BacktestConfig(
                        start_date=start_date,
                        end_date=end_date,
                        gsr_high_threshold=high_threshold,
                        gsr_low_threshold=low_threshold,
                        position_size_pct=position_size,
                        transaction_cost_pct=tx_cost,
                    )

                    try:
                        result = await run_backtest(db, config)

                        all_results.append(
                            {
                                "params": {
                                    "gsr_high": high_threshold,
                                    "gsr_low": low_threshold,
                                    "position_size": position_size,
                                    "transaction_cost": tx_cost,
                                },
                                "gold_oz_gain_pct": result.gold_oz_gain_pct,
                                "sharpe_ratio": result.sharpe_ratio,
                                "win_rate": result.win_rate,
                                "total_swaps": result.total_swaps,
                            }
                        )

                        # Track best (by gold oz gain)
                        if (
                            best_result is None
                            or result.gold_oz_gain_pct > best_result.gold_oz_gain_pct
                        ):
                            best_result = result
                            best_params = {
                                "gsr_high": high_threshold,
                                "gsr_low": low_threshold,
                                "position_size": position_size,
                                "transaction_cost": tx_cost,
                            }

                    except Exception as e:
                        logger.error(f"Backtest failed for params {config}: {e}")
                        continue

    return {
        "best_params": best_params,
        "best_result": best_result.to_dict() if best_result else None,
        "all_results": all_results,
    }
