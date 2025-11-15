'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { metricsApi, signalsApi, GSRMetric, Signal } from '@/lib/api';

export default function Home() {
  const [gsr, setGSR] = useState<GSRMetric | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [gsrData, signalsData] = await Promise.all([
        metricsApi.getCurrentGSR(),
        signalsApi.getCurrentSignals(),
      ]);

      setGSR(gsrData);
      setSignals(signalsData);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data. Go to Settings → Add API keys → Click "Refresh Data Now"');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-300 dark:bg-gray-700 rounded w-64 mx-auto mb-4"></div>
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-96 mx-auto"></div>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-8 text-center">
            <div className="text-6xl mb-4">⚠️</div>
            <h2 className="text-yellow-800 dark:text-yellow-200 text-2xl font-bold mb-4">No Data Available</h2>
            <p className="text-yellow-700 dark:text-yellow-300 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/settings"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
              >
                Go to Settings
              </Link>
              <button
                onClick={handleRefresh}
                className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </main>
    );
  }

  const getGSRStatus = () => {
    if (!gsr || !gsr.percentile) return { color: 'gray', text: 'Unknown' };

    if (gsr.percentile >= 85) {
      return { color: 'gold', text: 'Very High (Consider Gold → Silver)' };
    } else if (gsr.percentile <= 20) {
      return { color: 'silver', text: 'Very Low (Consider Silver → Gold)' };
    } else if (gsr.percentile >= 70) {
      return { color: 'yellow', text: 'High' };
    } else if (gsr.percentile <= 30) {
      return { color: 'blue', text: 'Low' };
    } else {
      return { color: 'green', text: 'Normal' };
    }
  };

  const status = getGSRStatus();

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header with Actions */}
        <header className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-gold-500 to-silver-400 bg-clip-text text-transparent">
                Gold-Silver Ratio Analytics
              </h1>
              <p className="text-gray-600 dark:text-gray-300 text-sm md:text-base">
                AI-Powered Precious Metals Tracking & Trading Insights
              </p>
            </div>
            <div className="flex gap-2 md:gap-3">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="px-3 md:px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition flex items-center gap-2 text-sm md:text-base"
                title="Refresh data from server"
              >
                <svg className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="hidden md:inline">{refreshing ? 'Refreshing...' : 'Refresh'}</span>
              </button>
              <Link
                href="/ai"
                className="px-3 md:px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-medium transition flex items-center gap-2 text-sm md:text-base"
              >
                <span>🤖</span>
                <span className="hidden md:inline">Ask AI Advisor</span>
              </Link>
            </div>
          </div>
        </header>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-8">
          <Link
            href="/analytics"
            className="p-4 md:p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition text-center group"
          >
            <div className="text-3xl md:text-4xl mb-2 group-hover:scale-110 transition">📊</div>
            <div className="font-semibold text-gray-800 dark:text-white text-sm md:text-base">Analytics</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Interactive Charts</div>
          </Link>
          <Link
            href="/backtest"
            className="p-4 md:p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition text-center group"
          >
            <div className="text-3xl md:text-4xl mb-2 group-hover:scale-110 transition">⏮️</div>
            <div className="font-semibold text-gray-800 dark:text-white text-sm md:text-base">Backtest</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Test Strategies</div>
          </Link>
          <Link
            href="/ai"
            className="p-4 md:p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition text-center group"
          >
            <div className="text-3xl md:text-4xl mb-2 group-hover:scale-110 transition">🤖</div>
            <div className="font-semibold text-gray-800 dark:text-white text-sm md:text-base">AI Advisor</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Get Insights</div>
          </Link>
          <Link
            href="/settings"
            className="p-4 md:p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition text-center group"
          >
            <div className="text-3xl md:text-4xl mb-2 group-hover:scale-110 transition">⚙️</div>
            <div className="font-semibold text-gray-800 dark:text-white text-sm md:text-base">Settings</div>
            <div className="text-xs text-gray-500 dark:text-gray-400">API Keys & Data</div>
          </Link>
        </div>

        {/* Current GSR Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 md:p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl md:text-2xl font-bold text-gray-800 dark:text-white">Current GSR</h2>
            <span className={`px-4 py-2 rounded-full text-xs md:text-sm font-semibold bg-${status.color}-100 dark:bg-${status.color}-900/30 text-${status.color}-800 dark:text-${status.color}-200`}>
              {status.text}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
            {/* GSR Value */}
            <div className="text-center p-4 md:p-6 bg-gradient-to-br from-gold-50 to-silver-50 dark:from-gold-900/10 dark:to-silver-900/10 rounded-xl">
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-2">GSR</p>
              <p className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gold-600 to-silver-500 bg-clip-text text-transparent">
                {gsr?.gsr.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {gsr?.gold_price && gsr?.silver_price && (
                  <>Gold ${gsr.gold_price.toFixed(0)} / Silver ${gsr.silver_price.toFixed(2)}</>
                )}
              </p>
            </div>

            {/* Percentile */}
            <div className="text-center p-4 md:p-6 bg-blue-50 dark:bg-blue-900/10 rounded-xl">
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-2">90-Day Percentile</p>
              <p className="text-4xl md:text-5xl font-bold text-blue-600 dark:text-blue-400">
                {gsr?.percentile?.toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Historical Rank
              </p>
            </div>

            {/* Z-Score */}
            <div className="text-center p-4 md:p-6 bg-purple-50 dark:bg-purple-900/10 rounded-xl">
              <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 mb-2">Z-Score</p>
              <p className="text-4xl md:text-5xl font-bold text-purple-600 dark:text-purple-400">
                {gsr?.z_score?.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Std Dev from Mean
              </p>
            </div>
          </div>
        </div>

        {/* Active Signals */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 md:p-8 mb-8">
          <h2 className="text-xl md:text-2xl font-bold text-gray-800 dark:text-white mb-6">Active Signals</h2>

          {signals.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 text-lg">
                <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>No active signals at this time</p>
                <p className="text-sm mt-2">Signals are generated when GSR reaches extreme levels</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {signals.map((signal, idx) => (
                <div
                  key={idx}
                  className={`p-4 md:p-6 rounded-xl border-2 ${
                    signal.signal_type === 'swap_gold_to_silver'
                      ? 'border-silver-300 bg-silver-50 dark:border-silver-700 dark:bg-silver-900/10'
                      : 'border-gold-300 bg-gold-50 dark:border-gold-700 dark:bg-gold-900/10'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4 flex-wrap gap-4">
                    <div>
                      <h3 className="text-lg md:text-xl font-bold text-gray-800 dark:text-white mb-1">
                        {signal.signal_type === 'swap_gold_to_silver' ? '📈 Gold → Silver' : '📉 Silver → Gold'}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Strength: <span className="font-semibold">{signal.strength.toFixed(1)}/100</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="px-4 py-2 rounded-lg bg-white dark:bg-gray-700">
                        <p className="text-xs text-gray-500 dark:text-gray-400">Position Size</p>
                        <p className="text-xl md:text-2xl font-bold text-gray-800 dark:text-white">
                          {signal.position_size.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-gray-700 dark:text-gray-300 font-medium mb-2">
                      {signal.recommendation}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {signal.reasoning}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 md:gap-4 text-xs md:text-sm text-gray-500 dark:text-gray-400 flex-wrap">
                    <span>GSR: {signal.gsr_value.toFixed(2)}</span>
                    <span>•</span>
                    <span>Percentile: {signal.gsr_percentile.toFixed(1)}%</span>
                    <span>•</span>
                    <span>Z-Score: {signal.gsr_z_score.toFixed(2)}</span>
                    <span>•</span>
                    <span>Regime: {signal.macro_regime}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-2">Gold Price</h3>
            <p className="text-2xl md:text-3xl font-bold text-gold-600 dark:text-gold-400">
              ${gsr?.gold_price?.toFixed(2) || '—'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">per troy oz</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-2">Silver Price</h3>
            <p className="text-2xl md:text-3xl font-bold text-silver-600 dark:text-silver-400">
              ${gsr?.silver_price?.toFixed(2) || '—'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">per troy oz</p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h3 className="text-sm text-gray-600 dark:text-gray-400 mb-2">Last Updated</h3>
            <p className="text-2xl md:text-3xl font-bold text-blue-600 dark:text-blue-400">
              {gsr?.timestamp ? new Date(gsr.timestamp).toLocaleDateString() : '—'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {gsr?.timestamp ? new Date(gsr.timestamp).toLocaleTimeString() : ''}
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 dark:text-gray-400 text-xs md:text-sm">
          <p>
            GSR Analytics v1.0 | For educational purposes only. Not investment advice.
          </p>
        </footer>
      </div>
    </main>
  );
}
