'use client';

import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';

interface ChartData {
  date: string;
  value: number;
  label?: string;
}

interface MultiLineData {
  date: string;
  [key: string]: any;
}

export function GSRHistoryChart({ data }: { data: ChartData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Gold-Silver Ratio History
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorGSR" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <ReferenceLine y={80} label="Current" stroke="red" strokeDasharray="3 3" />
          <Area type="monotone" dataKey="value" stroke="#8884d8" fillOpacity={1} fill="url(#colorGSR)" name="GSR" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function GoldPriceChart({ data }: { data: ChartData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Gold Price (USD/oz)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#FFD700" strokeWidth={2} name="Gold Price" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SilverPriceChart({ data }: { data: ChartData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Silver Price (USD/oz)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#C0C0C0" strokeWidth={2} name="Silver Price" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function DollarToMetalsChart({ data }: { data: MultiLineData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Dollar to Metals Ratios
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        How many ounces per $1000
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="goldOzPer1000" stroke="#FFD700" strokeWidth={2} name="Gold oz/$1000" dot={false} />
          <Line type="monotone" dataKey="silverOzPer1000" stroke="#C0C0C0" strokeWidth={2} name="Silver oz/$1000" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function MetalsPurchasingPowerChart({ data }: { data: MultiLineData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Purchasing Power Comparison
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Value of $1000 if invested in each metal
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorGold" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#FFD700" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#FFD700" stopOpacity={0.2}/>
            </linearGradient>
            <linearGradient id="colorSilver" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#C0C0C0" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#C0C0C0" stopOpacity={0.2}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area type="monotone" dataKey="goldValue" stroke="#FFD700" fillOpacity={1} fill="url(#colorGold)" name="Gold Value" />
          <Area type="monotone" dataKey="silverValue" stroke="#C0C0C0" fillOpacity={1} fill="url(#colorSilver)" name="Silver Value" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function GSRPercentileChart({ data }: { data: ChartData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        GSR Percentile Rank
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Where is GSR relative to historical range?
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <ReferenceLine y={85} label="Very High" stroke="red" strokeDasharray="3 3" />
          <ReferenceLine y={50} label="Median" stroke="gray" strokeDasharray="3 3" />
          <ReferenceLine y={15} label="Very Low" stroke="green" strokeDasharray="3 3" />
          <Bar dataKey="value" fill="#8884d8" name="Percentile" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function VolatilityChart({ data }: { data: MultiLineData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        Price Volatility (30-day)
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="goldVolatility" stroke="#FFD700" strokeWidth={2} name="Gold Vol" dot={false} />
          <Line type="monotone" dataKey="silverVolatility" stroke="#C0C0C0" strokeWidth={2} name="Silver Vol" dot={false} />
          <Line type="monotone" dataKey="gsrVolatility" stroke="#8884d8" strokeWidth={2} name="GSR Vol" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PremiumDiscountChart({ data }: { data: ChartData[] }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-bold text-gray-800 dark:text-white mb-4">
        GSR Premium/Discount from Historical Mean
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <ReferenceLine y={0} stroke="#000" />
          <Bar dataKey="value" fill="#8884d8" name="Premium/Discount %" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
