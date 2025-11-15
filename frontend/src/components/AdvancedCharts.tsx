'use client';

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface ChartDataPoint {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  value?: number;
  [key: string]: any;
}

interface AdvancedChartProps {
  title: string;
  data: ChartDataPoint[];
  dataKey?: string;
  height?: number;
}

type ChartType = 'line' | 'area' | 'bar' | 'candlestick';
type DateRange = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | 'all' | 'custom';

export function AdvancedGSRChart({ data, title = 'Gold-Silver Ratio' }: AdvancedChartProps) {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [dateRange, setDateRange] = useState<DateRange>('1m');
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  const getFilteredData = () => {
    if (!data || data.length === 0) return data;

    if (dateRange === 'custom' && customStart && customEnd) {
      return data.filter(
        (item) => item.date >= customStart && item.date <= customEnd
      );
    }

    const now = new Date();
    let startDate = new Date();

    switch (dateRange) {
      case '1d':
        startDate.setDate(now.getDate() - 1);
        break;
      case '1w':
        startDate.setDate(now.getDate() - 7);
        break;
      case '1m':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case '3m':
        startDate.setMonth(now.getMonth() - 3);
        break;
      case '6m':
        startDate.setMonth(now.getMonth() - 6);
        break;
      case '1y':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      case 'all':
        return data;
    }

    const startStr = startDate.toISOString().split('T')[0];
    return data.filter((item) => item.date >= startStr);
  };

  const filteredData = getFilteredData();

  const renderChart = () => {
    switch (chartType) {
      case 'area':
        return (
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#f59e0b"
              fillOpacity={1}
              fill="url(#colorValue)"
            />
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        );

      case 'candlestick':
        return (
          <ComposedChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="left" />
            <Tooltip />
            <Bar yAxisId="left" dataKey="high" fill="none" />
            <Bar
              yAxisId="left"
              dataKey="low"
              shape={<CustomCandlestick />}
              fill="#8884d8"
            />
          </ComposedChart>
        );

      default:
        return (
          <LineChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#f59e0b"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">{title}</h3>

        <div className="flex gap-2 flex-wrap">
          {/* Chart Type Selector */}
          <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
            {(['line', 'area', 'bar', 'candlestick'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setChartType(type)}
                className={`px-3 py-1 rounded text-xs font-medium transition ${
                  chartType === type
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Date Range Selector */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as DateRange)}
            className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-xs font-medium text-gray-700 dark:text-gray-300"
          >
            <option value="1d">1 Day</option>
            <option value="1w">1 Week</option>
            <option value="1m">1 Month</option>
            <option value="3m">3 Months</option>
            <option value="6m">6 Months</option>
            <option value="1y">1 Year</option>
            <option value="all">All Time</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
      </div>

      {/* Custom Date Range */}
      {dateRange === 'custom' && (
        <div className="mb-4 flex gap-2 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div>
            <label className="text-xs text-gray-600 dark:text-gray-400">Start</label>
            <input
              type="date"
              value={customStart}
              onChange={(e) => setCustomStart(e.target.value)}
              className="px-2 py-1 text-xs border rounded bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600 dark:text-gray-400">End</label>
            <input
              type="date"
              value={customEnd}
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-2 py-1 text-xs border rounded bg-white dark:bg-gray-600 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      )}

      {/* Chart */}
      <ResponsiveContainer width="100%" height={400}>
        {renderChart()}
      </ResponsiveContainer>

      {/* Chart Info */}
      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        <p>
          Showing {filteredData.length} data points
          {dateRange !== 'custom'
            ? ` (${dateRange.toUpperCase()})`
            : ' (Custom Range)'}
        </p>
      </div>
    </div>
  );
}

// Helper component for candlestick rendering
function CustomCandlestick(props: any) {
  const { x, y, width, height, payload } = props;

  if (!payload || payload.low === undefined || payload.high === undefined) {
    return null;
  }

  const yScale = height / (Math.max(...payload.map((d: any) => d.high)) - Math.min(...payload.map((d: any) => d.low)));
  const lowY = y + height - (payload.low - 0) * yScale;
  const highY = y + height - (payload.high - 0) * yScale;

  return (
    <g>
      <line
        x1={x + width / 2}
        y1={highY}
        x2={x + width / 2}
        y2={lowY}
        stroke="#8884d8"
        strokeWidth={1}
      />
      <rect
        x={x + width / 4}
        y={Math.min(highY, lowY)}
        width={width / 2}
        height={Math.abs(highY - lowY)}
        fill="#8884d8"
        stroke="#8884d8"
      />
    </g>
  );
}

export function PriceChart({
  title,
  data,
  dataKey = 'value',
}: AdvancedChartProps) {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [dateRange, setDateRange] = useState<DateRange>('1m');

  const getFilteredData = () => {
    if (!data || data.length === 0) return data;
    if (dateRange === 'all') return data;

    const now = new Date();
    let startDate = new Date();

    switch (dateRange) {
      case '1d':
        startDate.setDate(now.getDate() - 1);
        break;
      case '1w':
        startDate.setDate(now.getDate() - 7);
        break;
      case '1m':
        startDate.setMonth(now.getMonth() - 1);
        break;
      case '3m':
        startDate.setMonth(now.getMonth() - 3);
        break;
      case '6m':
        startDate.setMonth(now.getMonth() - 6);
        break;
      case '1y':
        startDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        return data;
    }

    const startStr = startDate.toISOString().split('T')[0];
    return data.filter((item) => item.date >= startStr);
  };

  const filteredData = getFilteredData();
  const color = title.includes('Gold') ? '#f59e0b' : '#a0aec0';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <h3 className="text-lg font-bold text-gray-800 dark:text-white">{title}</h3>

        <div className="flex gap-2 flex-wrap">
          {/* Chart Type */}
          <div className="flex gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
            {(['line', 'area', 'bar'] as const).map((type) => (
              <button
                key={type}
                onClick={() => setChartType(type)}
                className={`px-3 py-1 rounded text-xs font-medium transition ${
                  chartType === type
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Date Range */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as DateRange)}
            className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg text-xs font-medium text-gray-700 dark:text-gray-300"
          >
            <option value="1d">1D</option>
            <option value="1w">1W</option>
            <option value="1m">1M</option>
            <option value="3m">3M</option>
            <option value="6m">6M</option>
            <option value="1y">1Y</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        {chartType === 'area' ? (
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id={`color${title}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              fillOpacity={1}
              fill={`url(#color${title})`}
            />
          </AreaChart>
        ) : chartType === 'bar' ? (
          <BarChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey={dataKey} fill={color} />
          </BarChart>
        ) : (
          <LineChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        )}
      </ResponsiveContainer>

      <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        <p>Data points: {filteredData.length}</p>
      </div>
    </div>
  );
}
