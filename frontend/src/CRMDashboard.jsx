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
  const [activeTab, setActiveTab] = useState('inventory');

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
            { label: 'Last 90 Days', value: 90 },
            { label: 'Last 365 Days', value: 365 }
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
          
          {/* AI Executive Insights Panel */}
          {data.insights && (
            <div className="bg-[#141517] border border-blue-900/30 rounded-xl p-5 space-y-4 shadow-lg shadow-blue-950/10 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-blue-500/10 border-l border-b border-blue-950/30 text-blue-400 px-3 py-1 rounded-bl-lg text-[9px] font-bold uppercase tracking-widest flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-blue-400 animate-pulse" />
                AI Generated
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">AI Business Executive Insights</h3>
                  <p className="text-[10px] text-zinc-550">Uniformed & simplified view of scattered CRM data sources for business decision makers</p>
                </div>
              </div>
              
              <div className="border-t border-[#1e1e22] pt-4 grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Executive Summary Column */}
                <div className="md:col-span-2 space-y-3">
                  <span className="text-[9.5px] font-bold text-zinc-500 uppercase tracking-wider block">Unified Monthly Summary</span>
                  <p className="text-zinc-300 text-xs leading-relaxed font-medium">
                    {data.insights.executive_summary}
                  </p>
                  
                  {/* Explanation sub-cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                    {data.insights.key_metrics?.map((metric, idx) => (
                      <div key={idx} className="bg-[#111213] border border-[#1e1e22] p-3 rounded-lg flex items-start gap-2.5">
                        <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                          metric.status === 'positive' ? 'bg-emerald-500 shadow-[0_0_6px_#10b981]' : 
                          metric.status === 'attention' ? 'bg-amber-500 shadow-[0_0_6px_#f59e0b]' : 'bg-zinc-500'
                        }`} />
                        <div>
                          <span className="text-[10px] font-bold text-zinc-400 block">{metric.label}</span>
                          <span className="text-[11px] text-zinc-500 block mt-0.5 leading-normal">{metric.explanation}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Action Items Column */}
                <div className="bg-[#111213] border border-[#1e1e22] rounded-lg p-4 space-y-3">
                  <span className="text-[9.5px] font-bold text-zinc-500 uppercase tracking-wider block">Recommended Action Items</span>
                  <div className="space-y-3">
                    {data.insights.action_items?.map((item, idx) => (
                      <div key={idx} className="border-b border-[#1e1e22] last:border-0 pb-3 last:pb-0 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] font-bold text-zinc-200">{item.task}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider ${
                            item.priority === 'High' ? 'bg-red-950/40 text-red-400 border border-red-900/30' :
                            item.priority === 'Medium' ? 'bg-amber-950/40 text-amber-400 border border-amber-900/30' :
                            'bg-zinc-800 text-zinc-400 border border-zinc-700'
                          }`}>
                            {item.priority}
                          </span>
                        </div>
                        <p className="text-[10px] text-zinc-550 leading-normal">{item.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
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

          {/* Row 3: Interactive Detail Analytics Section */}
          <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-6">
            {/* Interactive Tab Headers */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#1e1e22] pb-4">
              <div>
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">CRM Secondary Analysis</span>
                <span className="text-[12px] text-zinc-400">Select any option below to dynamically generate a corresponding visual analysis</span>
              </div>
              
              <div className="flex items-center gap-2 bg-[#17181a] border border-[#1e1e22] p-1 rounded-xl self-start sm:self-auto">
                {[
                  { id: 'inventory', label: 'Inventory Stock', icon: '📦' },
                  { id: 'tickets', label: 'Support Tickets', icon: '🎫' },
                  { id: 'segments', label: 'Client Segments', icon: '📊' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-3 py-1.5 rounded-lg text-[11px] font-bold transition flex items-center gap-1.5 ${
                      activeTab === tab.id 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'text-zinc-450 hover:text-zinc-200'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Dynamic Graph Render Area */}
            <div className="w-full min-h-[300px]">
              {activeTab === 'inventory' && (
                <div className="space-y-4 animate-fade-in">
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">SKU Level Stock Status</h4>
                    <p className="text-[11px] text-zinc-500">Comparing current inventory quantities on hand against target safety stock reorder thresholds</p>
                  </div>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={data.inventory_items} margin={{ top: 10, right: 10, left: 10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1f" />
                      <XAxis dataKey="sku" stroke="#52525b" fontSize={10} />
                      <YAxis stroke="#52525b" fontSize={10} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#111213', borderColor: '#1e1e22', borderRadius: '8px' }}
                        labelStyle={{ color: '#a1a1aa', fontWeight: 'bold' }}
                        itemStyle={{ color: '#e4e4e7' }}
                      />
                      <Legend verticalAlign="top" height={36} />
                      <Bar dataKey="qty_on_hand" fill="#8b5cf6" name="Quantity On Hand" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="reorder_point" fill="#f43f5e" name="Reorder Threshold" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {activeTab === 'tickets' && (
                <div className="space-y-4 animate-fade-in">
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Daily Support Ticket Load</h4>
                    <p className="text-[11px] text-zinc-550">Chronological volume of incoming customer support tickets generated</p>
                  </div>
                  <ResponsiveContainer width="100%" height={280}>
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
                      <Bar dataKey="tickets" fill="#f59e0b" name="Support Tickets Generated" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {activeTab === 'segments' && (
                <div className="space-y-4 animate-fade-in flex flex-col md:flex-row items-center justify-between gap-6">
                  <div className="space-y-2 max-w-xs">
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider">Client Revenue Segments</h4>
                    <p className="text-[11px] text-zinc-500 leading-relaxed">Closed-won revenue share split dynamically across Enterprise, SMB, and Startup segments in the active window.</p>
                  </div>
                  <div className="flex-1 w-full flex items-center justify-center min-h-[260px]">
                    <ResponsiveContainer width="100%" height={260}>
                      <PieChart>
                        <Pie
                          data={data.segments}
                          cx="50%"
                          cy="45%"
                          innerRadius={55}
                          outerRadius={80}
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
              )}
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
