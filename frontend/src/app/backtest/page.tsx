'use client';

import { useState } from 'react';
import { backtestApi, BacktestConfig, BacktestResult } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function BacktestPage() {
  const [config, setConfig] = useState<BacktestConfig>({
    start_date: '2020-01-01',
    end_date: new Date().toISOString().split('T')[0],
    initial_gold_oz: 10,
    gsr_high_threshold: 85,
    gsr_low_threshold: 65,
    position_size_pct: 15,
    transaction_cost_pct: 2,
  });

  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig((prev) => ({
      ...prev,
      [name]: name.includes('date') ? value : parseFloat(value),
    }));
  };

  const runBacktest = async () => {
    try {
      setLoading(true);
      setError(null);
      const backtestResult = await backtestApi.runBacktest(config);
      setResult(backtestResult);
    } catch (err: any) {
      console.error('Backtest error:', err);
      setError(err.response?.data?.detail || 'Failed to run backtest. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-gold-500 to-silver-500 bg-clip-text text-transparent">
            Strategy Backtesting
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Test your GSR trading strategy against historical data
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 sticky top-20">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-6">
                Backtest Parameters
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Start Date
                  </label>
                  <input
                    type="date"
                    name="start_date"
                    value={config.start_date}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    End Date
                  </label>
                  <input
                    type="date"
                    name="end_date"
                    value={config.end_date}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Initial Gold (oz): {config.initial_gold_oz}
                  </label>
                  <input
                    type="range"
                    name="initial_gold_oz"
                    min="1"
                    max="100"
                    step="1"
                    value={config.initial_gold_oz}
                    onChange={handleChange}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    GSR High Threshold: {config.gsr_high_threshold}
                  </label>
                  <input
                    type="range"
                    name="gsr_high_threshold"
                    min="70"
                    max="100"
                    step="1"
                    value={config.gsr_high_threshold}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Swap gold → silver when GSR exceeds this
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    GSR Low Threshold: {config.gsr_low_threshold}
                  </label>
                  <input
                    type="range"
                    name="gsr_low_threshold"
                    min="50"
                    max="80"
                    step="1"
                    value={config.gsr_low_threshold}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Swap silver → gold when GSR falls below this
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Position Size: {config.position_size_pct}%
                  </label>
                  <input
                    type="range"
                    name="position_size_pct"
                    min="5"
                    max="50"
                    step="5"
                    value={config.position_size_pct}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Percentage of holdings to swap per signal
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Transaction Cost: {config.transaction_cost_pct}%
                  </label>
                  <input
                    type="range"
                    name="transaction_cost_pct"
                    min="0"
                    max="5"
                    step="0.5"
                    value={config.transaction_cost_pct}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Fees and spread per transaction
                  </p>
                </div>

                <button
                  onClick={runBacktest}
                  disabled={loading}
                  className="w-full mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition shadow-lg hover:shadow-xl"
                >
                  {loading ? 'Running...' : 'Run Backtest'}
                </button>
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 mb-6">
                <h3 className="text-red-800 dark:text-red-200 font-bold mb-2">Error</h3>
                <p className="text-red-600 dark:text-red-300">{error}</p>
              </div>
            )}

            {loading && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                <div className="animate-spin w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-300">Running backtest...</p>
              </div>
            )}

            {!loading && !result && !error && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                <div className="text-gray-400 dark:text-gray-500">
                  <svg className="w-24 h-24 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <h3 className="text-xl font-bold text-gray-700 dark:text-gray-300 mb-2">
                    Ready to Backtest
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Configure parameters and click "Run Backtest" to see results
                  </p>
                </div>
              </div>
            )}

            {result && !loading && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Final Gold (oz)</p>
                    <p className="text-2xl font-bold text-gold-600 dark:text-gold-400">
                      {result.final_gold_oz.toFixed(3)}
                    </p>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Gain</p>
                    <p className={`text-2xl font-bold ${result.gold_oz_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {result.gold_oz_gain >= 0 ? '+' : ''}{result.gold_oz_gain.toFixed(3)}oz
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      ({result.gold_oz_gain_pct.toFixed(1)}%)
                    </p>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Total Swaps</p>
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {result.total_swaps}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Win rate: {result.win_rate.toFixed(1)}%
                    </p>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                    <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Sharpe Ratio</p>
                    <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {result.sharpe_ratio.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Max DD: {result.max_drawdown.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Detailed Results */}
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
                  <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
                    Performance Summary
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Returns</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Initial Gold:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {config.initial_gold_oz.toFixed(3)} oz
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Final Gold:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.final_gold_oz.toFixed(3)} oz
                          </span>
                        </div>
                        <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                          <span className="text-gray-600 dark:text-gray-400">Total Gain:</span>
                          <span className={`font-bold ${result.gold_oz_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {result.gold_oz_gain >= 0 ? '+' : ''}{result.gold_oz_gain.toFixed(3)} oz
                            ({result.gold_oz_gain_pct >= 0 ? '+' : ''}{result.gold_oz_gain_pct.toFixed(2)}%)
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Trade Statistics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Total Swaps:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.total_swaps}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Winning Swaps:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.winning_swaps}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Win Rate:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.win_rate.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Risk Metrics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Sharpe Ratio:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.sharpe_ratio.toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Max Drawdown:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {result.max_drawdown.toFixed(2)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Strategy Parameters</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">GSR High:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {config.gsr_high_threshold}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">GSR Low:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {config.gsr_low_threshold}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Position Size:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {config.position_size_pct}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Transaction Cost:</span>
                          <span className="font-medium text-gray-800 dark:text-white">
                            {config.transaction_cost_pct}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      <strong>Interpretation:</strong> This strategy would have{' '}
                      {result.gold_oz_gain_pct >= 0 ? 'increased' : 'decreased'} your gold holdings by{' '}
                      <strong>{Math.abs(result.gold_oz_gain_pct).toFixed(2)}%</strong> over the tested period using{' '}
                      {result.total_swaps} swaps between gold and silver based on GSR extremes.
                    </p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>
            GSR Analytics v1.0 | Past performance does not guarantee future results. For educational purposes only.
          </p>
        </footer>
      </div>
    </main>
  );
}
