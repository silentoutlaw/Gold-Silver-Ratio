'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { metricsApi, GSRMetric } from '@/lib/api';
import { AdvancedGSRChart, PriceChart } from '@/components/AdvancedCharts';

export default function AnalyticsPage() {
  const [gsr, setGSR] = useState<GSRMetric | null>(null);
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [autoRefreshAttempted, setAutoRefreshAttempted] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        // Fetch current GSR
        const gsrData = await metricsApi.getCurrentGSR();
        setGSR(gsrData);

        // Fetch real historical data from backend (Yahoo scraped data or API data)
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const startDate = thirtyDaysAgo.toISOString(); // Full datetime format required by backend

        try {
          // Fetch metric data from backend using direct fetch (new working endpoint)
          let gsrValues: any[] = [];
          let goldValues: any[] = [];
          let silverValues: any[] = [];

          try {
            const gsrResponse = await fetch(`http://192.168.99.124:8000/api/v1/metrics/gsr/values?start_date=${startDate}`);
            if (gsrResponse.ok) {
              const gsrData = await gsrResponse.json();
              gsrValues = gsrData?.values || [];
            }
          } catch (e) {
            console.warn('Failed to fetch GSR data', e);
          }

          try {
            const goldResponse = await fetch(`http://192.168.99.124:8000/api/v1/metrics/gold_price/values?start_date=${startDate}`);
            if (goldResponse.ok) {
              const goldData = await goldResponse.json();
              goldValues = goldData?.values || [];
            }
          } catch (e) {
            console.warn('Failed to fetch gold price data', e);
          }

          try {
            const silverResponse = await fetch(`http://192.168.99.124:8000/api/v1/metrics/silver_price/values?start_date=${startDate}`);
            if (silverResponse.ok) {
              const silverData = await silverResponse.json();
              silverValues = silverData?.values || [];
            }
          } catch (e) {
            console.warn('Failed to fetch silver price data', e);
          }

          // Format GSR data for charts
          const gsrData_formatted = gsrValues.map((item: any) => ({
            date: item.timestamp ? item.timestamp.split('T')[0] : item.date,
            value: parseFloat(item.value?.toFixed(2) || item.gsr?.toFixed(2) || 0),
          }));

          // Format gold price data for charts
          const goldData_formatted = goldValues.map((item: any) => ({
            date: item.timestamp ? item.timestamp.split('T')[0] : item.date,
            value: parseFloat(item.value?.toFixed(2) || 0),
          }));

          // Format silver price data for charts
          const silverData_formatted = silverValues.map((item: any) => ({
            date: item.timestamp ? item.timestamp.split('T')[0] : item.date,
            value: parseFloat(item.value?.toFixed(2) || 0),
          }));

          // Use real data if available, otherwise create minimal demo data to show charts
          if (gsrData_formatted.length > 0 || goldData_formatted.length > 0 || silverData_formatted.length > 0) {
            setChartData({
              gsrData: gsrData_formatted,
              goldData: goldData_formatted,
              silverData: silverData_formatted,
            });
            setError(null);
          } else if (gsrData) {
            // Create minimal demo data based on current values to show charts are functional
            const today = new Date().toISOString().split('T')[0];
            const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

            setChartData({
              gsrData: [
                { date: yesterday, value: gsrData.gsr * 0.98 },
                { date: today, value: gsrData.gsr }
              ],
              goldData: [
                { date: yesterday, value: (gsrData.gold_price || 0) * 0.99 },
                { date: today, value: gsrData.gold_price || 0 }
              ],
              silverData: [
                { date: yesterday, value: (gsrData.silver_price || 0) * 1.01 },
                { date: today, value: gsrData.silver_price || 0 }
              ],
            });
            setError('Loading historical data from market sources. Showing recent values.');
          } else {
            // No data - try auto-refresh if we haven't already
            if (!autoRefreshAttempted) {
              console.log('No historical data found. Attempting auto-refresh from data sources...');
              setAutoRefreshAttempted(true);

              try {
                // Auto-trigger data refresh from all enabled sources
                const response = await fetch('http://192.168.99.124:8000/api/v1/config/ingest-data', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ days_back: 30 }),
                });

                if (response.ok) {
                  // Compute metrics after ingestion
                  await fetch('http://192.168.99.124:8000/api/v1/config/compute-metrics', {
                    method: 'POST',
                  });

                  // Retry fetching data after refresh
                  setTimeout(() => fetchData(), 2000);
                  return;
                }
              } catch (refreshErr) {
                console.error('Auto-refresh failed:', refreshErr);
              }
            }

            setError('No historical data available. Make sure at least one data source (Yahoo Finance or API) is enabled in Settings and refreshing will start automatically.');
          }
        } catch (apiErr) {
          console.error('Error fetching historical data from API:', apiErr);

          if (!autoRefreshAttempted) {
            setAutoRefreshAttempted(true);
            console.log('Attempting auto-refresh due to API error...');

            try {
              await fetch('http://192.168.99.124:8000/api/v1/config/ingest-data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ days_back: 30 }),
              });

              await fetch('http://192.168.99.124:8000/api/v1/config/compute-metrics', {
                method: 'POST',
              });

              setTimeout(() => fetchData(), 2000);
              return;
            } catch (e) {
              console.error('Auto-refresh failed:', e);
            }
          }

          setError('Unable to load data. Please check that data sources are enabled in Settings.');
        }
      } catch (err) {
        console.error('Error fetching analytics data:', err);
        setError('Failed to load analytics. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [autoRefreshAttempted]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-300 dark:bg-gray-700 rounded w-64 mx-auto mb-4"></div>
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-96 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                {autoRefreshAttempted ? 'Loading real market data...' : 'Fetching analytics data...'}
              </p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-gold-500 to-silver-400 bg-clip-text text-transparent">
                Analytics Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                Interactive charts with multiple views and date range selection
              </p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
            >
              ← Back to Overview
            </Link>
          </div>
        </header>

        {/* Current Metrics Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-gold-50 to-gold-100 dark:from-gold-900/20 dark:to-gold-800/20 rounded-xl p-4 border border-gold-200 dark:border-gold-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Gold Price</p>
            <p className="text-2xl font-bold text-gold-700 dark:text-gold-400">
              ${gsr?.gold_price?.toFixed(2) || '—'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-silver-50 to-silver-100 dark:from-silver-900/20 dark:to-silver-800/20 rounded-xl p-4 border border-silver-200 dark:border-silver-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Silver Price</p>
            <p className="text-2xl font-bold text-silver-700 dark:text-silver-400">
              ${gsr?.silver_price?.toFixed(2) || '—'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-4 border border-blue-200 dark:border-blue-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Current GSR</p>
            <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">
              {gsr?.gsr?.toFixed(2) || '—'}
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl p-4 border border-purple-200 dark:border-purple-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Decision Signal</p>
            <p className="text-2xl font-bold text-purple-700 dark:text-purple-400">
              {gsr && gsr.gsr > 85 ? 'HIGH' : gsr && gsr.gsr < 65 ? 'LOW' : 'NORMAL'}
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
            <p className="text-amber-800 dark:text-amber-200 font-medium mb-2">Data Loading Status</p>
            <p className="text-amber-700 dark:text-amber-300 text-sm mb-3">{error}</p>
            <p className="text-amber-600 dark:text-amber-400 text-xs mb-3">
              The system is attempting to load real market data. This may take a few moments.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="text-amber-600 dark:text-amber-400 hover:underline text-sm font-semibold"
            >
              ↻ Refresh Page
            </button>
          </div>
        )}

        {/* Advanced Charts - Only show if we have real data */}
        {chartData && !error && (
          <div className="space-y-8">
            {/* Main GSR Chart */}
            <AdvancedGSRChart data={chartData.gsrData} title="Gold-Silver Ratio (GSR) - Real Data" />

            {/* Price Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PriceChart
                title="Gold Price (USD/oz) - Real Data"
                data={chartData.goldData}
                dataKey="value"
              />
              <PriceChart
                title="Silver Price (USD/oz) - Real Data"
                data={chartData.silverData}
                dataKey="value"
              />
            </div>

            {/* Insights Panel */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
                💡 Key Insights
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Dollar to Gold Ratio
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      With $1,000 you can buy approximately <span className="font-bold text-gold-600">
                        {gsr?.gold_price ? (1000 / gsr.gold_price).toFixed(4) : '—'}
                      </span> troy ounces of gold.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Dollar to Silver Ratio
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      With $1,000 you can buy approximately <span className="font-bold text-silver-600">
                        {gsr?.silver_price ? (1000 / gsr.silver_price).toFixed(2) : '—'}
                      </span> troy ounces of silver.
                    </p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Relative Value
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                      1 oz of gold is worth <span className="font-bold text-blue-600">
                        {gsr?.gsr?.toFixed(2) || '—'}
                      </span> oz of silver.
                      {gsr && gsr.gsr > 80 && (
                        <span className="text-orange-600 font-semibold"> Silver is relatively cheap!</span>
                      )}
                      {gsr && gsr.gsr < 70 && (
                        <span className="text-green-600 font-semibold"> Ratio is balanced.</span>
                      )}
                    </p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">
                      📊 Chart Controls
                    </h3>
                    <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-2">
                      <li>• <strong>Chart Type:</strong> Switch between Line, Area, Bar, and Candlestick views</li>
                      <li>• <strong>Date Range:</strong> Quick presets (1D, 1W, 1M, 3M, 6M, 1Y, All)</li>
                      <li>• <strong>Custom Range:</strong> Select "Custom Range" to pick specific dates</li>
                      <li>• <strong>Hover:</strong> Hover over the chart to see exact values</li>
                    </ul>
                  </div>

                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                    <h3 className="font-semibold text-purple-800 dark:text-purple-300 mb-2">
                      🎯 Current Recommendation
                    </h3>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {gsr && gsr.gsr > 85 && (
                        <span>GSR is <strong>very high</strong>. Silver is relatively undervalued. Consider gradually building silver positions.</span>
                      )}
                      {gsr && gsr.gsr >= 75 && gsr.gsr <= 85 && (
                        <span>GSR is <strong>elevated</strong>. Watch for further increases to consider silver.</span>
                      )}
                      {gsr && gsr.gsr < 75 && (
                        <span>GSR is <strong>normal to low</strong>. Current positioning is reasonable.</span>
                      )}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>
            GSR Analytics v1.1 | Charts display real market data from Yahoo Finance or configured API sources.
            {!chartData && !error && ' Loading data...'}
            {error && ' Refresh data from Settings to display real data.'}
            For educational purposes only.
          </p>
        </footer>
      </div>
    </main>
  );
}
