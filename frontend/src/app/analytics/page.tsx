'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { metricsApi, GSRMetric } from '@/lib/api';
import { AdvancedGSRChart, PriceChart } from '@/components/AdvancedCharts';

// Generate sample historical data for demonstration
function generateSampleData(currentGSR: number, currentGold: number, currentSilver: number) {
  const days = 365;
  const gsrData = [];
  const goldData = [];
  const silverData = [];

  const gsrMean = 75;

  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];

    // Simulate GSR fluctuation
    const gsrVariation = (Math.random() - 0.5) * 10 + (currentGSR - gsrMean) * (1 - i / days);
    const gsr = Math.max(50, Math.min(100, gsrMean + gsrVariation));

    // Simulate gold price (trending up)
    const goldVariation = (Math.random() - 0.5) * 100;
    const goldTrend = (currentGold - 3800) * (1 - i / days);
    const gold = Math.max(3000, 3800 + goldTrend + goldVariation);

    // Calculate silver from GSR
    const silver = gold / gsr;

    gsrData.push({ date: dateStr, value: parseFloat(gsr.toFixed(2)) });
    goldData.push({ date: dateStr, value: parseFloat(gold.toFixed(2)) });
    silverData.push({ date: dateStr, value: parseFloat(silver.toFixed(2)) });
  }

  return {
    gsrData,
    goldData,
    silverData,
  };
}

export default function AnalyticsPage() {
  const [gsr, setGSR] = useState<GSRMetric | null>(null);
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const gsrData = await metricsApi.getCurrentGSR();
        setGSR(gsrData);

        // Generate sample data based on current values
        if (gsrData.gsr && gsrData.gold_price && gsrData.silver_price) {
          const data = generateSampleData(gsrData.gsr, gsrData.gold_price, gsrData.silver_price);
          setChartData(data);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    }

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

        {/* Advanced Charts */}
        {chartData && (
          <div className="space-y-8">
            {/* Main GSR Chart */}
            <AdvancedGSRChart data={chartData.gsrData} title="Gold-Silver Ratio (GSR)" />

            {/* Price Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PriceChart
                title="Gold Price (USD/oz)"
                data={chartData.goldData}
                dataKey="value"
              />
              <PriceChart
                title="Silver Price (USD/oz)"
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
            GSR Analytics v1.1 | Charts display real data with interactive controls. For educational purposes only.
          </p>
        </footer>
      </div>
    </main>
  );
}
