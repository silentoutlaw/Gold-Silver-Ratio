'use client';

import { useState, useEffect } from 'react';

interface APIKeys {
  fred_api_key: string;
  metals_api_key: string;
  alpha_vantage_api_key: string;
  openai_api_key: string;
  anthropic_api_key: string;
  google_api_key: string;
}

interface DataSource {
  id: string;
  name: string;
  description: string;
  type: 'api' | 'scraper';
  requires_key: boolean;
  enabled: boolean;
  data_types?: string[];
}

export default function SettingsPage() {
  const [apiKeys, setAPIKeys] = useState<APIKeys>({
    fred_api_key: '',
    metals_api_key: '',
    alpha_vantage_api_key: '',
    openai_api_key: '',
    anthropic_api_key: '',
    google_api_key: '',
  });

  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataRefreshing, setDataRefreshing] = useState(false);

  useEffect(() => {
    // Load current API keys from backend (masked)
    const fetchKeys = async () => {
      try {
        const response = await fetch('http://192.168.99.124:8000/api/v1/config/api-keys');
        if (response.ok) {
          const data = await response.json();
          console.log('Current API keys:', data);
        }
      } catch (e) {
        console.error('Failed to fetch API keys');
      }
    };

    // Load available data sources
    const fetchSources = async () => {
      try {
        const response = await fetch('http://192.168.99.124:8000/api/v1/config/data-sources');
        if (response.ok) {
          const data = await response.json();
          // Initialize with all sources enabled by default
          setDataSources(
            data.available_sources.map((source: any) => ({
              ...source,
              enabled: true,
            }))
          );
        }
      } catch (e) {
        console.error('Failed to fetch data sources');
      }
    };

    fetchKeys();
    fetchSources();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setAPIKeys((prev) => ({ ...prev, [name]: value }));
    setSaved(false);
  };

  const handleSourceToggle = (sourceId: string) => {
    setDataSources((prev) =>
      prev.map((source) =>
        source.id === sourceId ? { ...source, enabled: !source.enabled } : source
      )
    );
    setSaved(false);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      // Send API keys to backend
      const response = await fetch('http://192.168.99.124:8000/api/v1/config/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fred_api_key: apiKeys.fred_api_key || undefined,
          metals_api_key: apiKeys.metals_api_key || undefined,
          alpha_vantage_api_key: apiKeys.alpha_vantage_api_key || undefined,
          openai_api_key: apiKeys.openai_api_key || undefined,
          anthropic_api_key: apiKeys.anthropic_api_key || undefined,
          google_api_key: apiKeys.google_api_key || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save API keys');
      }

      setSaved(true);
      setTimeout(() => setSaved(false), 5000);

    } catch (e: any) {
      setError(e.message || 'Failed to save API keys');
    } finally {
      setSaving(false);
    }
  };

  const handleRefreshData = async () => {
    try {
      setDataRefreshing(true);
      setError(null);

      // Get enabled sources
      const enabledSources = dataSources
        .filter((s) => s.enabled)
        .map((s) => s.id);

      // Trigger manual data ingestion
      const response = await fetch('http://192.168.99.124:8000/api/v1/config/ingest-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          days_back: 30,
          sources: enabledSources.length > 0 ? enabledSources : undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to refresh data');
      }

      // Also compute metrics
      await fetch('http://192.168.99.124:8000/api/v1/config/compute-metrics', {
        method: 'POST',
      });

      setSaved(true);
      setTimeout(() => setSaved(false), 5000);

    } catch (e: any) {
      setError(e.message || 'Failed to refresh data');
    } finally {
      setDataRefreshing(false);
    }
  };

  const handleClear = (key: keyof APIKeys) => {
    setAPIKeys((prev) => ({ ...prev, [key]: '' }));
    setSaved(false);
  };

  const apiKeyFields = [
    {
      key: 'fred_api_key' as keyof APIKeys,
      label: 'FRED API Key',
      description: 'For economic data from Federal Reserve Economic Data',
      link: 'https://fred.stlouisfed.org/docs/api/api_key.html',
    },
    {
      key: 'metals_api_key' as keyof APIKeys,
      label: 'Metals-API Key',
      description: 'For precious metals spot prices',
      link: 'https://metals-api.com/',
    },
    {
      key: 'alpha_vantage_api_key' as keyof APIKeys,
      label: 'Alpha Vantage API Key',
      description: 'For ETF and stock market data',
      link: 'https://www.alphavantage.co/support/#api-key',
    },
    {
      key: 'openai_api_key' as keyof APIKeys,
      label: 'OpenAI API Key',
      description: 'For AI advisor using GPT models',
      link: 'https://platform.openai.com/api-keys',
    },
    {
      key: 'anthropic_api_key' as keyof APIKeys,
      label: 'Anthropic API Key',
      description: 'For AI advisor using Claude models',
      link: 'https://console.anthropic.com/settings/keys',
    },
    {
      key: 'google_api_key' as keyof APIKeys,
      label: 'Google AI API Key',
      description: 'For AI advisor using Gemini models',
      link: 'https://aistudio.google.com/app/apikey',
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-gold-500 to-silver-500 bg-clip-text text-transparent">
            Settings
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Configure API keys, data sources, and refresh data
          </p>
        </header>

        {/* Status Messages */}
        {saved && (
          <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <p className="text-green-800 dark:text-green-200 font-medium">
              ✓ Settings saved successfully!
            </p>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
            <p className="text-red-800 dark:text-red-200 font-medium">{error}</p>
          </div>
        )}

        {/* Data Sources Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
            Data Sources
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Choose which data sources to enable. Free sources don't require API keys.
          </p>

          <div className="space-y-4">
            {dataSources.map((source) => (
              <div
                key={source.id}
                className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        id={`source-${source.id}`}
                        checked={source.enabled}
                        onChange={() => handleSourceToggle(source.id)}
                        className="w-5 h-5 rounded cursor-pointer"
                      />
                      <label
                        htmlFor={`source-${source.id}`}
                        className="flex-1 cursor-pointer"
                      >
                        <h3 className="font-bold text-gray-800 dark:text-white">
                          {source.name}
                          <span
                            className={`ml-3 text-xs px-2 py-1 rounded ${
                              source.type === 'api'
                                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200'
                                : 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                            }`}
                          >
                            {source.type === 'api' ? 'API (Requires Key)' : 'Scraper (Free)'}
                          </span>
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {source.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Data types: {source.data_types?.join(', ') || 'Various'}
                        </p>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>💡 Tip:</strong> You can use free sources (Yahoo, CFTC) without any API keys.
              Add paid keys for more data types.
            </p>
          </div>
        </div>

        {/* API Keys Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
            API Keys
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Configure API keys for enabled data sources (optional if using only free sources)
          </p>

          <div className="space-y-6">
            {apiKeyFields.map((field) => (
              <div key={field.key} className="border-b border-gray-200 dark:border-gray-700 pb-6 last:border-b-0">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <label
                      htmlFor={field.key}
                      className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1"
                    >
                      {field.label}
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                      {field.description}
                    </p>
                  </div>
                  <a
                    href={field.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 text-xs text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Get Key →
                  </a>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="password"
                    id={field.key}
                    name={field.key}
                    value={apiKeys[field.key]}
                    onChange={handleChange}
                    placeholder={`Enter your ${field.label}`}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  {apiKeys[field.key] && (
                    <button
                      onClick={() => handleClear(field.key)}
                      className="px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex items-center justify-between flex-wrap gap-4">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              <p>🔒 API keys are stored securely on the backend server</p>
              <p className="mt-1">
                Keys are encrypted and never exposed in responses
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleRefreshData}
                disabled={dataRefreshing}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition shadow-lg hover:shadow-xl"
              >
                {dataRefreshing ? 'Refreshing...' : 'Refresh Data Now'}
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition shadow-lg hover:shadow-xl"
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>

        {/* Information */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">
            How It Works
          </h2>

          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                1. Choose Data Sources
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Enable the data sources you want to use. Free sources (Yahoo Finance, CFTC)
                don't require API keys. Paid sources give you more data types.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                2. Add API Keys (if needed)
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Get free API keys from the links provided. Paste them in the fields above.
                Click "Save Settings" to store them securely.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                3. Refresh Data
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Click "Refresh Data Now" to load the latest data from your selected sources.
                The system will fetch the last 30 days of data and compute metrics.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-2">
                4. View Results
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Go back to the home page to see your GSR data, charts, and trading signals.
                All calculations are based on real market data.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
          <p>
            GSR Analytics v1.1 | All configuration is optional. Use free sources or add API keys for more data.
          </p>
        </footer>
      </div>
    </main>
  );
}
