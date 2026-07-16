// frontend/src/CRMDashboard.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  TrendingUp, 
  CreditCard, 
  HelpCircle, 
  Archive, 
  Sparkles, 
  Calendar, 
  Users,
  Loader2,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

const SEGMENT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export default function CRMDashboard({ API }) {
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCRMData = async (selectedDays) => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API}/api/crm-data?days=${selectedDays}`);
      if (res.data.error) {
        setError(res.data.error);
      } else {
        setData(res.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || "Failed to fetch CRM metrics from the database.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCRMData(days);
  }, [days]);

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-8 pt-6 pb-28 md:pb-6 space-y-8 max-w-6xl w-full mx-auto flex flex-col">
      {/* Header & Date Selection */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#1e1e22] pb-6">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <span>📈</span> Live CRM Dashboard
          </h1>
          <p className="text-[12px] text-zinc-550 mt-1">
            Real-time sales lifecycle, overhead expense metrics, and customer segment insights.
          </p>
        </div>
        
        {/* Date Filter Pills */}
        <div className="flex items-center gap-2 self-start md:self-auto bg-[#111213] border border-[#1e1e22] p-1 rounded-xl">
          {[
            { label: 'Last 7 Days', value: 7 },
            { label: 'Last 30 Days', value: 30 },
            { label: 'Last 90 Days', value: 90 }
          ].map((pill) => (
            <button
              key={pill.value}
              onClick={() => setDays(pill.value)}
              className={`px-3 py-1.5 rounded-lg text-[11px] font-bold transition ${
                days === pill.value 
                  ? 'bg-blue-600 text-white shadow-md' 
                  : 'text-zinc-450 hover:text-zinc-200'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          <span className="text-zinc-500 text-xs uppercase tracking-widest font-semibold">Aggregating CRM Data...</span>
        </div>
      ) : error ? (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-red-950/20 border border-red-900/30 text-red-400 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-bold">Database Fetch Error</h4>
            <p className="text-xs mt-1 text-red-400/80">{error}</p>
          </div>
        </div>
      ) : data ? (
        <div className="space-y-6 animate-fade-in">
          
          {/* Row 1: KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* KPI 1: Revenue */}
            <div className="bg-[#111213] border border-[#1e1e22] p-4.5 rounded-xl flex items-center justify-between hover:border-zinc-700 transition">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Total Revenue</span>
                <span className="text-lg font-bold text-emerald-450 block font-mono">
                  ${data.kpis.revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <span className="text-[9.5px] text-zinc-600 block">Closed-Won Deals</span>
              </div>
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <TrendingUp className="w-5 h-5" />
              </div>
            </div>

            {/* KPI 2: Expenses */}
            <div className="bg-[#111213] border border-[#1e1e22] p-4.5 rounded-xl flex items-center justify-between hover:border-zinc-700 transition">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Net Expenses</span>
                <span className="text-lg font-bold text-rose-450 block font-mono">
                  ${data.kpis.expenses.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <span className="text-[9.5px] text-zinc-600 block">Operating & Admin Costs</span>
              </div>
              <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <CreditCard className="w-5 h-5" />
              </div>
            </div>

            {/* KPI 3: Support Tickets */}
            <div className="bg-[#111213] border border-[#1e1e22] p-4.5 rounded-xl flex items-center justify-between hover:border-zinc-700 transition">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Support Tickets (Avg)</span>
                <span className="text-lg font-bold text-amber-500 block font-mono">
                  {data.kpis.tickets} / day
                </span>
                <span className="text-[9.5px] text-zinc-600 block">New Customer Cases</span>
              </div>
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <HelpCircle className="w-5 h-5" />
              </div>
            </div>

            {/* KPI 4: Inventory Level */}
            <div className="bg-[#111213] border border-[#1e1e22] p-4.5 rounded-xl flex items-center justify-between hover:border-zinc-700 transition">
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Inventory Level</span>
                <span className="text-lg font-bold text-violet-400 block font-mono">
                  {data.kpis.inventory.toLocaleString()} units
                </span>
                <span className="text-[9.5px] text-zinc-600 block">Active Stock on Hand</span>
              </div>
              <div className="w-10 h-10 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
                <Archive className="w-5 h-5" />
              </div>
            </div>
          </div>

          {/* Row 2: Main Revenue vs Expenses Chart */}
          <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4">
            <div>
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Financial Performance Timeline</span>
              <span className="text-[12px] text-zinc-400">Comparing daily closed deals revenue against operations expenditures</span>
            </div>
            <div className="w-full">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.history} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1f" />
                  <XAxis dataKey="date" stroke="#52525b" fontSize={10} />
                  <YAxis stroke="#52525b" fontSize={10} tickFormatter={(v) => `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111213', borderColor: '#1e1e22', borderRadius: '8px' }} 
                    labelStyle={{ color: '#a1a1aa', fontWeight: 'bold' }}
                    itemStyle={{ color: '#e4e4e7' }}
                    formatter={(value) => [`$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, '']}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2.5} name="Daily Revenue" activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="expenses" stroke="#f43f5e" strokeWidth={2} name="Daily Expenses" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Row 3: Support Tickets (60%) & Customer Segments (40%) */}
          <div className="grid grid-cols-1 lg:grid-cols-10 gap-6">
            {/* Support Tickets Bar Chart */}
            <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4 lg:col-span-6">
              <div>
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Daily Customer Support Load</span>
                <span className="text-[12px] text-zinc-400">Incoming tickets generated per day</span>
              </div>
              <div className="w-full">
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={data.history} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1f" />
                    <XAxis dataKey="date" stroke="#52525b" fontSize={10} />
                    <YAxis stroke="#52525b" fontSize={10} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#111213', borderColor: '#1e1e22', borderRadius: '8px' }}
                      labelStyle={{ color: '#a1a1aa', fontWeight: 'bold' }}
                      itemStyle={{ color: '#e4e4e7' }}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Bar dataKey="tickets" fill="#f59e0b" name="Support Tickets" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Segment Breakdown Pie Chart */}
            <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4 lg:col-span-4 flex flex-col">
              <div>
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Customer Segment Breakdown</span>
                <span className="text-[12px] text-zinc-400">Revenue split across client segments</span>
              </div>
              <div className="w-full flex-1 flex items-center justify-center min-h-[260px]">
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={data.segments}
                      cx="50%"
                      cy="45%"
                      innerRadius={55}
                      outerRadius={75}
                      paddingAngle={4}
                      dataKey="value"
                      nameKey="name"
                    >
                      {data.segments.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SEGMENT_COLORS[index % SEGMENT_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#111213', borderColor: '#1e1e22', borderRadius: '8px' }}
                      itemStyle={{ color: '#e4e4e7' }}
                      formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
                    />
                    <Legend verticalAlign="bottom" align="center" layout="horizontal" />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
          
          {/* Footer */}
          <div className="flex items-center justify-center gap-1.5 text-zinc-650 text-[10px] pt-4 uppercase tracking-widest font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping"></span>
            <span>Data refreshes live from internal database</span>
          </div>

        </div>
      ) : null}
    </div>
  );
}
