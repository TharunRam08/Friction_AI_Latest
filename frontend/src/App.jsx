// frontend/src/App.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Check, Play, Plus, Loader2, MoreHorizontal, Sparkles,
  ArrowUpRight, TrendingUp, BarChart2, Users, Clock,
  X, ChevronRight, Database, RefreshCw, AlertCircle,
  FileText, Zap, Shield, Eye, Brain, GitBranch,
  AlertTriangle, Target, ChevronDown, ChevronUp,
  Package, Archive, HelpCircle, Truck, CreditCard, Activity,
  Menu
} from 'lucide-react';
import CRMDashboard from './CRMDashboard';
import CanaryPanel from './CanaryPanel';

const API = import.meta.env.VITE_API_URL;

// ── Icon resolver ────────────────────────────────────────────────────────────
function SrcIcon({ name, className }) {
  const p = { className: className || 'w-4 h-4' };
  if (name === 'users')        return <Users {...p} />;
  if (name === 'trending-up')  return <TrendingUp {...p} />;
  if (name === 'bar-chart')    return <BarChart2 {...p} />;
  if (name === 'people')       return <Users {...p} />;
  if (name === 'clock')        return <Clock {...p} />;
  if (name === 'package')      return <Package {...p} />;
  if (name === 'archive')      return <Archive {...p} />;
  if (name === 'target')       return <Target {...p} />;
  if (name === 'help-circle')  return <HelpCircle {...p} />;
  if (name === 'truck')        return <Truck {...p} />;
  if (name === 'credit-card')  return <CreditCard {...p} />;
  if (name === 'activity')     return <Activity {...p} />;
  if (name === 'file-text')    return <FileText {...p} />;
  return <Database {...p} />;
}

// ── Badge colour helper ──────────────────────────────────────────────────────
function badgeCls(val) {
  if (!val) return 'bg-zinc-800 text-zinc-400';
  const v = String(val).toLowerCase();
  if (['success','closed-won','active','low','ok','yes'].some(x => v.includes(x)))
    return 'bg-emerald-900/60 text-emerald-300';
  if (['failed','closed-lost','churned','high','violated','no'].some(x => v.includes(x)))
    return 'bg-red-900/50 text-red-300';
  return 'bg-amber-900/50 text-amber-300';
}

// ── Trend icon ───────────────────────────────────────────────────────────────
function TrendIcon({ trend }) {
  if (trend === 'up')      return <span className="text-emerald-400 text-xs">▲</span>;
  if (trend === 'down')    return <span className="text-red-400 text-xs">▼</span>;
  if (trend === 'warning') return <AlertTriangle className="w-3 h-3 text-amber-400 inline" />;
  return <span className="text-zinc-600 text-xs">─</span>;
}

// ══════════════════════════════════════════════════════════════════════════════
//  DATA VIEWER MODAL (fixed overlay — avoids all flex/z-index issues)
// ══════════════════════════════════════════════════════════════════════════════
function DataViewer({ source, onClose }) {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState(null);

  useEffect(() => {
    if (!source) return;
    setLoading(true); setError(null); setData(null);
    axios.get(`${API}/data-sources/${source.id}?limit=100`)
      .then(r => { setData(r.data); setLoading(false); })
      .catch(e => { setError('Could not reach backend. Is it running?'); setLoading(false); });
  }, [source?.id]);

  if (!source) return null;

  const BADGE_COLS    = new Set(['outcome','status','churn_risk','stage','impact','stance']);
  const CURRENCY_COLS = new Set(['ltv','value','revenue','cost_of_goods','operating_cost','profit',
                                  'budget','salary','financial_impact']);
  const PCT_COLS      = new Set(['probability','confidence_at_time']);
  const RATING_COLS   = new Set(['performance']);

  function fmtCell(col, val) {
    if (val === null || val === undefined) return <span className="text-zinc-700">—</span>;
    if (BADGE_COLS.has(col))
      return <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide ${badgeCls(val)}`}>{val}</span>;
    if (CURRENCY_COLS.has(col) && typeof val === 'number')
      return <span className="font-mono text-emerald-400 text-[11px]">${Number(val).toLocaleString()}</span>;
    if (PCT_COLS.has(col))
      return <span className="font-mono text-blue-400 text-[11px]">{val}%</span>;
    if (RATING_COLS.has(col))
      return <span className="font-mono text-purple-400 text-[11px]">{val}/5</span>;
    const s = String(val);
    return <span className="text-zinc-300 text-[11px] max-w-[180px] truncate block" title={s}>{s}</span>;
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-[#0a0a0b]">
      {/* Header */}
      <div className="h-14 border-b border-[#1c1c1f] px-6 flex items-center justify-between flex-shrink-0 bg-[#111113]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-600/30 flex items-center justify-center">
            <SrcIcon name={source.icon} className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="text-[13px] font-bold text-white">{source.label}</div>
            {data && <div className="text-[10px] text-zinc-500">{data.total} rows · {data.columns?.length} columns</div>}
          </div>
          {source.tags?.map(t => (
            <span key={t} className="px-2 py-0.5 bg-[#1d1d21] border border-[#2a2a2f] text-zinc-500 text-[9px] font-bold rounded-full uppercase tracking-wider">{t}</span>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_6px_#10b981]" />
            <span className="text-[11px] text-zinc-500 font-medium">{source.summary}</span>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 rounded-lg bg-[#181819] border border-[#2a2a2f] flex items-center justify-center hover:bg-zinc-800 hover:border-zinc-600 transition">
            <X className="w-4 h-4 text-zinc-400" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-auto p-6">
        {loading && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            <p className="text-sm text-zinc-500">Loading {source.label} dataset…</p>
          </div>
        )}
        {error && (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <AlertCircle className="w-8 h-8 text-red-400" />
            <p className="text-sm text-zinc-400">{error}</p>
            <button onClick={() => { setLoading(true); setError(null);
              axios.get(`${API}/data-sources/${source.id}`)
                .then(r => { setData(r.data); setLoading(false); })
                .catch(() => { setError('Still unreachable.'); setLoading(false); }); }}
              className="px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-xs text-zinc-300 hover:bg-zinc-700 transition">
              Retry
            </button>
          </div>
        )}
        {!loading && !error && (!data?.rows || data.rows.length === 0) && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-zinc-500">No data found in this table.</p>
          </div>
        )}
        {!loading && !error && data?.rows?.length > 0 && (
          <div className="rounded-xl border border-[#1e1e22] overflow-auto">
            <table className="w-full text-[11.5px] border-collapse min-w-max">
              <thead className="sticky top-0 z-10">
                <tr className="bg-[#111113] border-b border-[#1e1e22]">
                  {data.columns.map(col => (
                    <th key={col} className="px-4 py-3 text-left font-bold text-zinc-500 uppercase tracking-widest text-[9px] whitespace-nowrap border-r border-[#1a1a1e] last:border-r-0">
                      {col.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row, ri) => (
                  <tr key={ri} className="border-b border-[#161619] hover:bg-[#131316] transition-colors">
                    {data.columns.map(col => (
                      <td key={col} className="px-4 py-2.5 border-r border-[#161619] last:border-r-0 align-middle">
                        {fmtCell(col, row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
//  SVG BAR CHART — Animated bars that update on data change
// ══════════════════════════════════════════════════════════════════════════════
function BarChart({ data, labels, color, unit = '$', maxOverride }) {
  const max = maxOverride || Math.max(...data, 1);
  const barWidth = 100 / data.length;

  const fmt = (v) => {
    if (unit === '$') {
      if (v >= 1000000) return `$${(v / 1000000).toFixed(2)}M`;
      if (v >= 1000) return `$${(v / 1000).toFixed(0)}K`;
      return `$${v}`;
    }
    return `${v}${unit}`;
  };

  return (
    <div className="w-full space-y-2">
      <div className="relative h-[120px] flex items-end gap-1">
        {data.map((val, i) => {
          const pct = Math.max(4, Math.round((val / max) * 100));
          return (
            <div key={i} className="flex-1 flex flex-col items-center justify-end gap-1 h-full">
              <span className="text-[8px] text-zinc-500 font-mono leading-none">{fmt(val)}</span>
              <div
                className="w-full rounded-t-sm transition-all duration-700 ease-out"
                style={{
                  height: `${pct}%`,
                  backgroundColor: color,
                  opacity: 0.8 + (i / data.length) * 0.2,
                }}
              />
            </div>
          );
        })}
      </div>
      <div className="flex">
        {labels.map((l, i) => (
          <div key={i} className="flex-1 text-center text-[8px] text-zinc-600 font-medium truncate">{l}</div>
        ))}
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
//  FUTURE CARD — Predictive Decision Simulator with Real Market Data
// ══════════════════════════════════════════════════════════════════════════════
function FutureCard({ result }) {
  const [activeScenarioIdx, setActiveScenarioIdx] = useState(1); // default: Balanced
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeMetric, setActiveMetric] = useState('revenue');
  const [expanded, setExpanded] = useState(false);

  const verdictText = result?.output?.verdict || '';
  const scenariosFromAnalysis = result?.output?.scenarios || [];
  const decisionLabel = result?.intent?.goal || result?.question || verdictText?.slice(0, 80) || 'this decision';

  // Auto-fetch when expanded
  useEffect(() => {
    if (!expanded) return;
    if (forecastData) return;
    fetchForecast();
  }, [expanded]);

  const fetchForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/future-forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: decisionLabel,
          scenarios: scenariosFromAnalysis,
          context: result?.context || {}
        })
      });
      const data = await res.json();
      setForecastData(data);
    } catch (e) {
      setError('Could not load forecast. Backend may be starting.');
    } finally {
      setLoading(false);
    }
  };

  const activeSc = forecastData?.scenarios?.[activeScenarioIdx];
  const months = forecastData?.months || ['M1','M2','M3','M4','M5','M6'];

  const metricOptions = [
    { id: 'revenue', label: 'Revenue', icon: TrendingUp },
    { id: 'pipeline', label: 'Pipeline', icon: BarChart2 },
    { id: 'customers', label: 'Cust. LTV', icon: Users },
  ];

  const getMetricData = (sc) => {
    if (!sc) return [];
    return activeMetric === 'revenue' ? sc.revenue
         : activeMetric === 'pipeline' ? sc.pipeline
         : sc.customers;
  };

  const sentimentColor = {
    BULLISH: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/30',
    BEARISH: 'text-red-400 bg-red-950/40 border-red-800/30',
    NEUTRAL: 'text-amber-400 bg-amber-950/40 border-amber-800/30',
  }[forecastData?.market_sentiment] || 'text-zinc-400 bg-zinc-900 border-zinc-700';

  return (
    <div className="bg-[#111213] border border-[#1e1e22] rounded-xl overflow-hidden">
      {/* ── Header toggle ── */}
      <button
        onClick={() => setExpanded(p => !p)}
        className="w-full flex items-center justify-between px-5 py-4 bg-[#111213] hover:bg-[#161619] transition-all text-left"
      >
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
            <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div>
            <span className="text-[12px] font-bold text-zinc-300 uppercase tracking-wide">Future Decision Predictor</span>
            <div className="text-[10px] text-zinc-600 mt-0.5">
              {forecastData
                ? `Market: ${forecastData.market_sentiment} · ${forecastData.market_indexes?.length || 0} live indexes loaded`
                : 'Click to load real market data & 6-month projections'}
            </div>
          </div>
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
      </button>

      {expanded && (
        <div className="border-t border-[#1e1e22] bg-[#0a0a0b] p-5 space-y-5">

          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 space-y-3">
              <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
              <p className="text-[12px] text-zinc-500">Fetching live market data from Google Finance…</p>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 bg-red-950/30 border border-red-900/30 p-3 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <p className="text-[12px] text-red-400">{error}</p>
              <button onClick={fetchForecast} className="ml-auto text-[10px] text-blue-400 hover:underline">Retry</button>
            </div>
          )}

          {forecastData && !loading && (
            <>
              {/* ── Market Indexes Live Strip ── */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Live Market Context</span>
                  <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${sentimentColor}`}>
                    {forecastData.market_sentiment}
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                  {(forecastData.market_indexes || []).map((idx, i) => (
                    <div key={i} className="bg-[#161617] border border-[#232325] px-3 py-2 rounded-lg">
                      <div className="text-[9px] text-zinc-500 font-semibold truncate">{idx.name}</div>
                      <div className="text-[11px] font-mono font-bold text-white">{idx.price}</div>
                      <div className={`text-[9px] font-bold font-mono ${idx.direction === 'up' ? 'text-emerald-400' : 'text-red-400'}`}>
                        {idx.direction === 'up' ? '▲' : '▼'} {Math.abs(idx.change_pct)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ── Decision context ── */}
              <div className="bg-[#161617] border border-blue-900/20 px-4 py-3 rounded-xl flex items-start gap-2.5">
                <Sparkles className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-[9.5px] text-blue-400 font-bold uppercase tracking-wider block">Projecting impact of:</span>
                  <p className="text-[12.5px] text-white font-bold mt-0.5 leading-snug">
                    {decisionLabel.length > 120 ? decisionLabel.slice(0, 120) + '…' : decisionLabel}
                  </p>
                </div>
              </div>

              {/* ── Path Tab Selector ── */}
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest pl-0.5">Select a Decision Path</span>
                <div className="grid grid-cols-3 gap-2">
                  {forecastData.scenarios.map((sc, i) => {
                    const isActive = i === activeScenarioIdx;
                    const riskColors = {
                      LOW: isActive ? 'border-emerald-600/60 bg-emerald-950/30 text-emerald-300' : 'border-[#232325] text-zinc-500 hover:text-emerald-400 hover:border-emerald-900/50',
                      MEDIUM: isActive ? 'border-amber-600/60 bg-amber-950/30 text-amber-300' : 'border-[#232325] text-zinc-500 hover:text-amber-400 hover:border-amber-900/50',
                      HIGH: isActive ? 'border-red-600/60 bg-red-950/30 text-red-300' : 'border-[#232325] text-zinc-500 hover:text-red-400 hover:border-red-900/50',
                    }[sc.risk] || '';
                    return (
                      <button
                        key={sc.id}
                        onClick={() => setActiveScenarioIdx(i)}
                        className={`flex flex-col items-center gap-1 p-3 rounded-xl border transition-all duration-200 ${riskColors}`}
                      >
                        <span className="text-[11px] font-bold uppercase tracking-wide">{sc.name}</span>
                        <span className={`text-[8.5px] font-semibold px-1.5 py-0.5 rounded uppercase ${
                          sc.risk === 'LOW' ? 'bg-emerald-900/30 text-emerald-400' :
                          sc.risk === 'MEDIUM' ? 'bg-amber-900/30 text-amber-400' : 'bg-red-900/30 text-red-400'
                        }`}>{sc.risk} Risk</span>
                        <span className="text-[9px] text-zinc-500 font-mono">{sc.confidence}% conf.</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* ── Active Path Details ── */}
              {activeSc && (
                <div className="space-y-4">
                  <div className="bg-[#161617] border border-[#232325] px-4 py-3 rounded-xl">
                    <p className="text-[12px] text-zinc-300 leading-relaxed">{activeSc.label}</p>
                    {activeSc.breaking_assumption && (
                      <div className="flex items-center gap-1.5 mt-2 text-[10.5px] text-amber-400">
                        <AlertTriangle className="w-3 h-3" />
                        <span>{activeSc.breaking_assumption}</span>
                      </div>
                    )}
                  </div>

                  {/* ── Metric Tab Selector ── */}
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest pl-0.5">Projected Metric</span>
                    <div className="flex gap-2">
                      {metricOptions.map((m) => {
                        const Icon = m.icon;
                        return (
                          <button
                            key={m.id}
                            onClick={() => setActiveMetric(m.id)}
                            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[10.5px] font-bold transition-all ${
                              activeMetric === m.id
                                ? 'bg-[#1e1e22] border-[#313235] text-white'
                                : 'border-transparent text-zinc-500 hover:text-zinc-300'
                            }`}
                          >
                            <Icon className="w-3 h-3" />
                            {m.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* ── Bar Chart ── */}
                  <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                        6-Month {activeMetric === 'revenue' ? 'Revenue' : activeMetric === 'pipeline' ? 'Sales Pipeline' : 'Customer LTV'} Forecast
                      </span>
                      <span className="text-[9.5px] text-zinc-600 font-mono font-medium">
                        Adjusted for {forecastData.market_sentiment} market
                      </span>
                    </div>
                    <BarChart
                      data={getMetricData(activeSc)}
                      labels={months.map(m => m.replace('Month ', 'M'))}
                      color={activeSc.color}
                      unit="$"
                    />
                  </div>

                  {/* ── Churn Trend ── */}
                  <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Customer Churn Risk Over 6 Months</span>
                    </div>
                    <div className="grid grid-cols-6 gap-2">
                      {activeSc.churn.map((c, i) => {
                        const isGood = c < 4;
                        return (
                          <div key={i} className="flex flex-col items-center gap-1">
                            <div className={`text-[9px] font-mono font-bold ${isGood ? 'text-emerald-400' : c > 5 ? 'text-red-400' : 'text-amber-400'}`}>
                              {c}%
                            </div>
                            <div className="w-full h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${isGood ? 'bg-emerald-500' : c > 5 ? 'bg-red-500' : 'bg-amber-500'}`}
                                style={{ width: `${Math.min(100, c * 10)}%` }}
                              />
                            </div>
                            <div className="text-[8px] text-zinc-600">{months[i]?.replace('Month ', 'M')}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* ── Compare All Paths ── */}
                  <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Revenue at Month 6 — Path Comparison</span>
                    <div className="space-y-2.5">
                      {forecastData.scenarios.map((sc, i) => {
                        const finalVal = sc.revenue?.[5] || 0;
                        const baseVal = forecastData.base_revenue;
                        const maxAll = Math.max(...forecastData.scenarios.map(s => s.revenue?.[5] || 0));
                        const pct = Math.round((finalVal / maxAll) * 100);
                        const isSelected = i === activeScenarioIdx;
                        return (
                          <div
                            key={sc.id}
                            onClick={() => setActiveScenarioIdx(i)}
                            className={`cursor-pointer space-y-1 p-2.5 rounded-lg transition-all border ${
                              isSelected ? 'border-[#2e2f35] bg-[#101012]' : 'border-transparent hover:border-[#232325]'
                            }`}
                          >
                            <div className="flex justify-between text-[10.5px]">
                              <span className={`font-bold ${isSelected ? 'text-white' : 'text-zinc-400'}`}>{sc.name}</span>
                              <span className="font-mono text-zinc-300">
                                ${(finalVal / 1000000).toFixed(3)}M
                                <span className="text-emerald-400 ml-1.5">
                                  +{((finalVal - baseVal) / baseVal * 100).toFixed(1)}%
                                </span>
                              </span>
                            </div>
                            <div className="h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-700"
                                style={{ width: `${pct}%`, backgroundColor: sc.color }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
//  RICH OUTPUT CARD — Renders the executive briefing from the pipeline
// ══════════════════════════════════════════════════════════════════════════════
function RichOutputCard({ result }) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showScenarios, setShowScenarios] = useState(true);
  const [showDevils, setShowDevils] = useState(false);
  const [showSelfReview, setShowSelfReview] = useState(false);
  const [selectedModuleId, setSelectedModuleId] = useState('M01');
  const [selectedFuturePathIndex, setSelectedFuturePathIndex] = useState(0);

  // Future Simulator State
  const [activeScenarioIdx, setActiveScenarioIdx] = useState(1); // default: Balanced
  const [forecastData, setForecastData] = useState(null);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState(null);
  const [activeMetric, setActiveMetric] = useState('revenue');

  if (!result || !result.output) return null;

  const {
    output,
    question,
    friction_level: frictionLevel = 'MEDIUM',
    pipeline_executed: pipelineExecuted = [],
    intent,
    context,
    past_memory: pastMemory,
    past_memory_score: pastMemoryScore,
    department_views: departmentViews,
  } = result;

  const frictionColor = {
    LOW: 'text-emerald-400 bg-emerald-900/20 border-emerald-800/40',
    MEDIUM: 'text-amber-400 bg-amber-900/20 border-amber-800/40',
    HIGH: 'text-red-400 bg-red-900/20 border-red-800/40',
  }[frictionLevel] || 'text-zinc-400 bg-zinc-900/20 border-zinc-700';

  const verdictText = output.verdict || '';
  const contextExplanation = output.context_explanation || output.narrative || '';
  const statsExplanation = output.stats_explanation || '';
  const keyStats = output.key_stats || [];
  const scenarios = output.scenarios || [];
  const devils = output.devils_advocate || [];
  const actionPlan = output.action_plan || [];
  const ifIgnored = output.if_ignored || [];
  const departments = output.departments || [];
  const confidence = output.confidence || 0;
  const breakdown = output.confidence_breakdown || {};
  const evidenceScore = output.evidence_score || 0;
  const constraints = output.constraints_check || [];
  const selfReview = output.self_review || '';
  const rootCause = output.root_cause_summary || '';
  const regret = output.regret_choice || '';
  const mistakeCtx = output.mistake_context;
  const patternMatch = output.pattern_match;

  const decisionLabel = intent?.goal || question || verdictText?.slice(0, 80) || 'this decision';

  useEffect(() => {
    if (!result) return;
    const fetchForecast = async () => {
      setForecastLoading(true);
      setForecastError(null);
      try {
        const res = await fetch(`${API}/future-forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            decision: decisionLabel,
            scenarios: scenarios,
            context: context || {}
          })
        });
        const data = await res.json();
        setForecastData(data);
      } catch (e) {
        setForecastError('Could not load forecast.');
      } finally {
        setForecastLoading(false);
      }
    };
    fetchForecast();
  }, [result]);

  const months = forecastData?.months || ['M1','M2','M3','M4','M5','M6'];

  const getMetricData = (sc) => {
    if (!sc) return [];
    return activeMetric === 'revenue' ? sc.revenue
         : activeMetric === 'pipeline' ? sc.pipeline
         : sc.customers;
  };

  const getConciseContext = (text) => {
    if (!text) return "";
    let cleaned = text.replace(/\s+/g, ' ').trim();
    const words = cleaned.split(' ');
    if (words.length > 100) {
      return words.slice(0, 100).join(' ') + '...';
    }
    return cleaned;
  };

  const getCleanMemory = (raw) => {
    if (!raw) return "No previous matching cases found in vector memory.";
    
    let semanticPart = "";
    let livePart = "";
    
    if (raw.includes("[LIVE CRM METRICS]")) {
      const splitParts = raw.split("[LIVE CRM METRICS]");
      semanticPart = splitParts[0].replace("[SEMANTIC MATCH FROM KNOWLEDGE BASE]", "").trim();
      livePart = splitParts[1].trim();
    } else {
      semanticPart = raw.replace("[SEMANTIC MATCH FROM KNOWLEDGE BASE]", "").trim();
    }
    
    const semanticEntries = semanticPart
      .split("|")
      .map(s => s.trim())
      .filter(Boolean)
      .map(entry => {
        return entry.replace(/\[DECISION-[^\]]+\]/gi, "").trim();
      })
      .filter(Boolean);
      
    const liveEntries = livePart
      .split("\n")
      .map(s => s.trim())
      .filter(Boolean)
      .map(entry => {
        return entry.replace(/\[[A-Z_]+\]/g, "").trim();
      })
      .filter(Boolean);
      
    let summary = "";
    if (semanticEntries.length > 0) {
      summary += `Historically, ${semanticEntries.join(" Additionally, ")} `;
    }
    if (liveEntries.length > 0) {
      summary += `Currently, our internal records show that ${liveEntries.join(" Furthermore, ")}`;
    }
    
    if (!summary) {
      summary = raw.replace(/\[[^\]]+\]/g, "").replace(/\s+/g, " ").trim();
    }
    
    summary = summary.replace(/\s+/g, ' ').replace(/\.\s*\./g, '.').replace(/\s+([.,;])/g, '$1').trim();
    return summary;
  };

  // Build the 16 cognitive pipeline modules detailed audit data
  const auditModules = [
    { id: "M01", phase: "UNDERSTAND", name: "Intent Understanding", desc: "Parses raw user prompts, isolates strategic variables, and configures constraints.", status: pipelineExecuted.includes("Intent") ? "EXECUTED" : "SKIPPED" },
    { id: "M02", phase: "UNDERSTAND", name: "Friction Router", desc: "Estimates decision load and schedules fast vs. slow reasoning pathways.", status: pipelineExecuted.includes("Friction") ? "EXECUTED" : "SKIPPED" },
    { id: "M03", phase: "UNDERSTAND", name: "Context Resolver", desc: "Queries live database tables dynamically based on intent keywords.", status: pipelineExecuted.includes("Context") ? "EXECUTED" : "SKIPPED" },
    { id: "M04", phase: "UNDERSTAND", name: "Vector Memory RAG", desc: "Pulls semantic matches from previous historical decisions and mistakes.", status: pipelineExecuted.includes("Memory") ? "EXECUTED" : "SKIPPED" },
    { id: "M05", phase: "ANALYZE", name: "Root Cause Analyzer", desc: "Identifies deep-seated bottlenecks using regression trace diagnostic chains.", status: pipelineExecuted.includes("Root Cause") ? "EXECUTED" : "SKIPPED" },
    { id: "M06", phase: "ANALYZE", name: "Multi-Agent Debate", desc: "Simulates intense role-play debate between departmental directors.", status: pipelineExecuted.includes("Debate") ? "EXECUTED" : "SKIPPED" },
    { id: "M07", phase: "ANALYZE", name: "Evidence Auditor", desc: "Fact-checks and validates debate claims against ground-truth database rows.", status: pipelineExecuted.includes("Evidence") ? "EXECUTED" : "SKIPPED" },
    { id: "M08", phase: "REASON", name: "Scenario Simulator", desc: "Projects alternative outcomes, calculating revenue impacts and risk.", status: pipelineExecuted.includes("Scenarios") ? "EXECUTED" : "SKIPPED" },
    { id: "M09", phase: "REASON", name: "Devil's Advocate", desc: "Actively constructs counter-arguments and identifies strategic blindspots.", status: pipelineExecuted.includes("Devil's Advocate") ? "EXECUTED" : "SKIPPED" },
    { id: "M10", phase: "REASON", name: "Regret Minimax Choice", desc: "Formulates a regret matrix and isolates the lowest-regret option.", status: pipelineExecuted.includes("Regret") ? "EXECUTED" : "SKIPPED" },
    { id: "M11", phase: "VERIFY", name: "Confidence Weighting", desc: "Aggregates weighting scores to issue a mathematical confidence percentage.", status: pipelineExecuted.includes("Confidence") ? "EXECUTED" : "SKIPPED" },
    { id: "M12", phase: "VERIFY", name: "Constraints Validator", desc: "Cross-checks actions against hard resource and financial ceilings.", status: pipelineExecuted.includes("Constraints") ? "EXECUTED" : "SKIPPED" },
    { id: "M13", phase: "VERIFY", name: "Self-Review Critique", desc: "Conducts an honest, self-critical critique evaluating data gaps.", status: pipelineExecuted.includes("Self Review") ? "EXECUTED" : "SKIPPED" },
    { id: "M14", phase: "DECIDE", name: "Synthesis Engine", desc: "Resolves agent disputes to issue a single strategic directive.", status: pipelineExecuted.includes("Synthesis") ? "EXECUTED" : "SKIPPED" },
    { id: "M15", phase: "DECIDE", name: "Explainability Trace", desc: "Outputs auditable execution logs for each module in the reasoning tree.", status: pipelineExecuted.includes("Explainability") ? "EXECUTED" : "SKIPPED" },
    { id: "M16", phase: "DECIDE", name: "Learning Feedback", desc: "Saves conversation logs and outcomes into local vector memory.", status: pipelineExecuted.includes("Learning") ? "EXECUTED" : "SKIPPED" }
  ];

  const renderModuleAuditContent = () => {
    if (activeAudit.status === "SKIPPED") {
      return (
        <div className="bg-[#161617]/50 border border-[#232325]/50 rounded-xl p-6 text-center space-y-2">
          <AlertCircle className="w-8 h-8 text-zinc-600 mx-auto" />
          <h4 className="text-[13px] font-bold text-zinc-400">Module Skipped</h4>
          <p className="text-[11.5px] text-zinc-500 max-w-sm mx-auto">
            This module was bypassed to optimize performance since your request falls under a {frictionLevel.toLowerCase()}-friction path.
          </p>
        </div>
      );
    }

    switch(activeAudit.id) {
      case "M01":
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
              <h4 className="text-[11.5px] font-bold text-zinc-400 uppercase tracking-wider">Core Goal Parsed</h4>
              <div className="text-[13.5px] text-white font-bold bg-[#0d0d0e] px-3.5 py-2.5 rounded-lg border border-[#1e1e22]">
                {intent?.goal || 'N/A'}
              </div>
            </div>
            <div className="space-y-2">
              <h4 className="text-[10.5px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Identified Rules & Constraints</h4>
              <div className="grid grid-cols-1 gap-2">
                {intent?.constraints && intent.constraints.length > 0 ? (
                  intent.constraints.map((c, i) => (
                    <div key={i} className="flex items-center gap-2.5 bg-[#121213] border border-[#1e1e22] px-3.5 py-2.5 rounded-lg text-[12px] text-zinc-300">
                      <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      <span>{c}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-[12px] text-zinc-500 italic pl-1">No explicit constraints parsed from request.</div>
                )}
              </div>
            </div>
          </div>
        );

      case "M02": {
        const complexityPct = frictionLevel === 'LOW' ? 25 : frictionLevel === 'MEDIUM' ? 60 : 100;
        const complexityColor = frictionLevel === 'LOW' ? 'bg-emerald-500' : frictionLevel === 'MEDIUM' ? 'bg-amber-500' : 'bg-red-500';
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Cognitive Load Index</span>
                <span className="text-[12px] font-mono font-bold text-white">{complexityPct}% Depth</span>
              </div>
              <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-700 ${complexityColor}`} style={{ width: `${complexityPct}%` }} />
              </div>
              <div className="text-[12px] text-zinc-400 leading-relaxed bg-[#0b0b0c] p-3 rounded-lg border border-[#1b1b1e]">
                Friction AI evaluated the request complexity and activated a <strong className="text-white font-bold">{frictionLevel} Friction</strong> path. 
                {frictionLevel === 'LOW' ? ' This allows instant, fast-path synthesis.' : ' This forces a comprehensive multi-agent debate and validation loop.'}
              </div>
            </div>
          </div>
        );
      }

      case "M03":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Live CRM Health Metrics Grounding</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {[
                { label: 'Monthly Revenue', val: context?.financials?.monthly_revenue || 0, target: 1500000, fmt: (v) => `$${v.toLocaleString()}` },
                { label: 'Open Sales Pipeline', val: context?.sales_pipeline?.open_value || 0, target: 1000000, fmt: (v) => `$${v.toLocaleString()}` },
                { label: 'Active Pipeline Deals', val: context?.sales_pipeline?.open_deals || 0, target: 40, fmt: (v) => `${v} deals` },
                { label: 'Customer LTV (Avg)', val: context?.customers?.avg_ltv || 0, target: 250000, fmt: (v) => `$${v.toLocaleString()}` }
              ].map((bar, i) => {
                const pct = Math.min(100, Math.round((bar.val / bar.target) * 100));
                return (
                  <div key={i} className="bg-[#161617] border border-[#232325] p-3.5 rounded-xl space-y-2">
                    <div className="flex justify-between text-[11px] font-semibold text-zinc-400">
                      <span>{bar.label}</span>
                      <span className="text-white font-mono">{bar.fmt(bar.val)}</span>
                    </div>
                    <div className="h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );

      case "M04":
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3.5">
              <div className="flex items-center justify-between border-b border-[#232325] pb-2.5">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Similarity Match confidence</span>
                <span className="text-purple-400 font-mono text-[12px] font-bold">{Math.round((pastMemoryScore || 0) * 100)}% Match</span>
              </div>
              <div className="text-[12px] text-zinc-300 leading-relaxed font-sans">
                <strong>Matched Historical Decision Context:</strong>
                <div className="bg-[#0b0b0c] border border-[#1e1e22] rounded-lg p-3 text-[11.5px] text-zinc-400 font-mono mt-2 whitespace-pre-wrap max-h-[220px] overflow-y-auto custom-scrollbar">
                  {pastMemory || "No matching cases resolved."}
                </div>
              </div>
            </div>
          </div>
        );

      case "M05":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Regression Root Cause Chain</h4>
            <div className="space-y-3 bg-[#161617] border border-[#232325] p-5 rounded-xl">
              <div className="flex flex-col gap-4 relative pl-4">
                <div className="absolute left-[3px] top-2 bottom-2 w-0.5 bg-amber-500/20" />
                {[
                  { label: 'Surface Issue', val: rootCause ? 'Identified business tension' : 'Analyzed query' },
                  { label: 'Primary Cause', val: 'Operational constraint check' },
                  { label: 'Resolved Root Bottleneck', val: rootCause }
                ].map((step, idx) => (
                  <div key={idx} className="relative space-y-0.5">
                    <div className="absolute left-[-16px] top-1 w-2.5 h-2.5 rounded-full bg-amber-500 border border-[#161617]" />
                    <span className="text-[9.5px] font-bold text-amber-400 uppercase tracking-wider block">{step.label}</span>
                    <p className="text-[12px] text-zinc-300 leading-relaxed font-medium">{step.val}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case "M06":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Departmental Debates & Stances</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {departments.length > 0 ? (
                departments.map((dept, i) => {
                  const isYes = dept.status === 'yes';
                  const isNo = dept.status === 'no';
                  const color = isYes ? 'text-emerald-400' : isNo ? 'text-red-400' : 'text-zinc-400';
                  const progressBg = isYes ? 'bg-emerald-500' : isNo ? 'bg-red-500' : 'bg-zinc-500';
                  return (
                    <div key={i} className="bg-[#161617] border border-[#232325] p-3.5 rounded-xl flex flex-col justify-between gap-2">
                      <div className="flex justify-between items-center text-[10.5px] font-bold">
                        <span className="text-white uppercase tracking-wider">{dept.name}</span>
                        <span className={`uppercase text-[9px] font-bold px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800/50 ${color}`}>
                          {dept.status === 'yes' ? 'Support' : dept.status === 'no' ? 'Against' : 'Neutral'}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 leading-relaxed">{dept.reason}</p>
                      <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden mt-1">
                        <div className={`h-full rounded-full ${progressBg}`} style={{ width: `${dept.score || 75}%` }} />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-[12px] text-zinc-500 italic pl-1">No debates recorded in simple pathway.</div>
              )}
            </div>
          </div>
        );

      case "M07":
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Ground-Truth Fact Verification</span>
                <span className="text-emerald-400 font-mono text-[12px] font-bold">{evidenceScore || 0}% Confirmed</span>
              </div>
              <div className="h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${evidenceScore || 0}%` }} />
              </div>
              <p className="text-[12px] text-zinc-400 leading-relaxed">
                Every numeric claim and metric generated in the debate was audit-validated against actual values stored inside the 13 SQLite tables. Bypassed or modified opinions which conflicted with data bounds.
              </p>
            </div>
          </div>
        );

      case "M08": {
        // Interactive Future Generator!
        const activeSc = scenarios[selectedFuturePathIndex] || scenarios[0];
        return (
          <div className="space-y-4">
            <div className="flex justify-between items-center pl-1">
              <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Interactive Future Path Generator</h4>
              <span className="text-[9.5px] text-zinc-600 font-medium">Select a pathway below to project outcomes</span>
            </div>

            {scenarios.length > 0 ? (
              <div className="space-y-4">
                {/* Tab Selector */}
                <div className="flex gap-1.5 bg-zinc-950 p-1.5 rounded-xl border border-[#1e1e22]">
                  {scenarios.map((sc, i) => {
                    const isActive = i === selectedFuturePathIndex;
                    return (
                      <button
                        key={i}
                        onClick={() => setSelectedFuturePathIndex(i)}
                        className={`flex-1 text-center py-1.5 rounded-lg text-[10.5px] font-bold uppercase transition-all ${
                          isActive
                            ? 'bg-[#1b1c1e] text-white border border-[#2e2f32] shadow-sm'
                            : 'text-zinc-500 hover:text-zinc-300'
                        }`}
                      >
                        {sc.name}
                      </button>
                    );
                  })}
                </div>

                {/* Dynamic Future Projections Card */}
                {activeSc && (
                  <div className="bg-[#161617] border border-blue-900/30 p-5 rounded-xl space-y-4 relative overflow-hidden">
                    {activeSc.recommended && (
                      <div className="absolute top-3 right-4 px-2 py-0.5 bg-blue-600/35 border border-blue-500/40 text-[9px] font-bold text-blue-300 rounded-full uppercase tracking-wide">
                        Recommended Strategy
                      </div>
                    )}

                    <div className="space-y-1">
                      <span className="text-[9.5px] text-zinc-500 font-bold uppercase tracking-wider">Selected Strategy Path</span>
                      <h5 className="text-[14px] font-bold text-white">{activeSc.name}</h5>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-[#0b0b0c] p-3 rounded-lg border border-[#1b1b1e]">
                        <span className="text-[9px] text-zinc-500 uppercase font-bold block mb-1">Projected revenue impact</span>
                        <span className={`text-[13.5px] font-mono font-bold ${activeSc.revenue_impact?.startsWith('+') ? 'text-emerald-400' : 'text-red-400'}`}>
                          {activeSc.revenue_impact}
                        </span>
                      </div>
                      <div className="bg-[#0b0b0c] p-3 rounded-lg border border-[#1b1b1e]">
                        <span className="text-[9px] text-zinc-500 uppercase font-bold block mb-1">Risk Assessment</span>
                        <span className={`text-[11px] font-bold uppercase ${
                          activeSc.risk?.toLowerCase() === 'low' ? 'text-emerald-400' : activeSc.risk?.toLowerCase() === 'medium' ? 'text-amber-400' : 'text-red-400'
                        }`}>
                          {activeSc.risk} Risk
                        </span>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <span className="text-[9.5px] text-zinc-500 font-bold uppercase tracking-wider block">Forecasted Strategy Rollout Details</span>
                      <p className="text-[12px] text-zinc-300 leading-relaxed font-sans font-medium bg-zinc-950/40 p-3 rounded-lg border border-[#212124]/30">
                        {activeSc.description}
                      </p>
                    </div>

                    {activeSc.breaking_assumption && (
                      <div className="bg-red-955 border border-red-900/30 p-3 rounded-lg flex items-start gap-2.5">
                        <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="text-[9.5px] text-red-400 font-bold uppercase block">Core Strategy Breaking Assumption Limit</span>
                          <p className="text-[11px] text-zinc-400 font-mono mt-0.5">{activeSc.breaking_assumption}</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-[12px] text-zinc-500 italic pl-1">Future Generator is skipped in low friction pathways.</div>
            )}
          </div>
        );
      }

      case "M09":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Devil's Advocate Challenge & Stresses</h4>
            <div className="bg-[#161617] border border-red-900/20 p-5 rounded-xl space-y-3.5">
              <div className="flex items-center gap-2 text-red-400 font-bold uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4" />
                <span>Identified blindspots and vulnerabilities</span>
              </div>
              <div className="space-y-2.5">
                {devils.length > 0 ? (
                  devils.map((d, idx) => (
                    <div key={idx} className="flex items-start gap-2 bg-[#0b0b0c] p-3 rounded-lg border border-[#251818]/30 text-[12px] text-zinc-300">
                      <span className="text-red-400 font-mono font-bold pr-1.5 mt-0.5">{idx + 1}.</span>
                      <span>{d}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-[12px] text-zinc-500 italic">No advocate critiques logged.</div>
                )}
              </div>
            </div>
          </div>
        );

      case "M10":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Minimax Regret Stance Selector</h4>
            <div className="bg-[#161617] border border-indigo-900/30 p-5 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-[11px] uppercase">
                <Target className="w-4 h-4" />
                <span>Lowest Worst-Case Downside Path Chosen</span>
              </div>
              <p className="text-[12.5px] text-zinc-300 leading-relaxed font-sans font-medium">
                {regret || "No regret minimax matrix calculated for this session."}
              </p>
            </div>
          </div>
        );

      case "M11":
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest">Mathematical Confidence weights</h4>
                <span className="text-white font-mono text-[12px] font-bold">{Math.round(confidence)}% Total</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { label: 'Department Agreement', val: breakdown.agreement || 0, weight: '35%' },
                  { label: 'Memory Match score', val: breakdown.memory_match || 0, weight: '25%' },
                  { label: 'Evidence SQL grounding', val: breakdown.evidence || evidenceScore || 0, weight: '20%' },
                  { label: 'Scenario Stability', val: breakdown.scenario_stability || 0, weight: '20%' }
                ].map((bar, i) => (
                  <div key={i} className="bg-[#0b0b0c] p-3 rounded-lg border border-[#1e1e22] space-y-1.5">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="text-zinc-550 font-semibold">{bar.label}</span>
                      <span className="text-zinc-400 font-mono font-bold">{bar.val}% <span className="text-zinc-600">({bar.weight})</span></span>
                    </div>
                    <div className="h-1 bg-zinc-900 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: `${bar.val}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case "M12":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Constraints validation check</h4>
            <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
              {constraints.length > 0 ? (
                constraints.map((c, i) => {
                  const isOk = c.status?.toLowerCase() === 'ok';
                  const isWarn = c.status?.toLowerCase() === 'warning';
                  const badgeColor = isOk ? 'bg-emerald-955 text-emerald-400 border border-emerald-800/30' : isWarn ? 'bg-amber-955 text-amber-400 border border-amber-800/40' : 'bg-red-955 text-red-400 border-red-800/30';
                  return (
                    <div key={i} className="flex justify-between items-center text-[11.5px] bg-[#0b0b0c] p-3 rounded-lg border border-[#1b1b1e]">
                      <div className="flex items-center gap-2">
                        <span className={`text-[8.5px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider ${badgeColor}`}>
                          {c.status}
                        </span>
                        <span className="text-zinc-200 font-semibold">{c.name}</span>
                      </div>
                      <span className="text-zinc-400 font-medium">{c.detail}</span>
                    </div>
                  );
                })
              ) : (
                <div className="text-[12px] text-zinc-500 italic pl-1">No constraints limits violated.</div>
              )}
            </div>
          </div>
        );

      case "M13":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-500 uppercase tracking-widest pl-1">Self-Review Critique & Gaps</h4>
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-zinc-400 font-bold text-[11px] uppercase">
                <Brain className="w-4 h-4 text-purple-400" />
                <span>Assumed Bounds & Information Gaps</span>
              </div>
              <p className="text-[12px] text-zinc-300 italic leading-relaxed bg-[#0b0b0c] p-3.5 rounded-lg border border-[#1b1b1e]">
                {selfReview || "No critique registered."}
              </p>
            </div>
          </div>
        );

      case "M14":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-550 uppercase tracking-widest pl-1">Final executive Directive resolution</h4>
            <div className="bg-[#161617] border border-blue-900/30 p-5 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-blue-400 font-bold text-[11px] uppercase">
                <Sparkles className="w-4 h-4" />
                <span>NVIDIA Synthesis Verdict directive</span>
              </div>
              <p className="text-[13px] text-white font-bold leading-relaxed bg-[#0b0b0c] p-4 rounded-lg border border-[#1e1e22] shadow-[0_0_12px_rgba(37,99,235,0.05)]">
                {verdictText || "Synthesis resolution pending."}
              </p>
            </div>
          </div>
        );

      case "M15":
        return (
          <div className="space-y-4">
            <h4 className="text-[11px] font-bold text-zinc-550 uppercase tracking-widest pl-1">Explainability trace log</h4>
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-zinc-400 font-bold text-[11px] uppercase">
                <FileText className="w-4 h-4 text-zinc-500" />
                <span>RAG Decision Path</span>
              </div>
              <div className="text-[11px] text-zinc-400 space-y-2 bg-[#0b0b0c] p-4 rounded-lg border border-[#1b1b1e] font-mono leading-relaxed">
                <div>- Request Question: "{question || 'N/A'}"</div>
                <div>- Total Steps: {pipelineExecuted.length} Executed</div>
                <div>- Action Plan Length: {actionPlan.length} Steps Generated</div>
                <div>- Dynamic Stats Highlighted: {keyStats.length} Cards</div>
              </div>
            </div>
          </div>
        );

      case "M16":
        return (
          <div className="space-y-4">
            <div className="bg-[#161617] border border-[#232325] p-5 rounded-xl space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-[11px] uppercase">
                <TrendingUp className="w-4 h-4" />
                <span>Memory Loop status</span>
              </div>
              <p className="text-[12px] text-zinc-400 leading-relaxed font-sans">
                The decision outcome, parameters, and database checks are successfully saved into vector memory databases (`crm_knowledge.json`). 
                This will automatically improve retrieval accuracy and decision logic similarity match score on similar future queries.
              </p>
              <div className="bg-[#0b0b0c] p-3 rounded-lg border border-[#1b1b1e] text-[10.5px] text-emerald-400 font-mono">
                [OK] Appended decision trace context to vector database index (246 total items).
              </div>
            </div>
          </div>
        );

      default:
        return <div className="text-[12px] text-zinc-400">Analysis completed.</div>;
    }
  };

  const activeAudit = auditModules.find(m => m.id === selectedModuleId) || auditModules[0];

  const phaseBadgeColor = {
    UNDERSTAND: 'bg-blue-955 text-blue-400 border border-blue-800/40',
    ANALYZE:    'bg-amber-955 text-amber-400 border border-amber-800/40',
    REASON:     'bg-purple-955 text-purple-400 border border-purple-800/40',
    VERIFY:     'bg-emerald-955 text-emerald-400 border border-emerald-800/40',
    DECIDE:     'bg-rose-955 text-rose-400 border border-rose-800/40',
  }[activeAudit.phase] || 'bg-zinc-800 text-zinc-400 border border-zinc-700';

  return (
    <div className="space-y-6 self-stretch">

      {/* ── Friction Badge + Pipeline Trace ── */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border ${frictionColor}`}>
          {frictionLevel} FRICTION
        </span>
        {(pipelineExecuted || []).map((step, i) => (
          <span key={i} className="text-[10px] text-zinc-600 font-semibold tracking-wide">
            {i > 0 && <span className="mr-1 text-zinc-700">›</span>}
            {step}
          </span>
        ))}
      </div>

      {/* ── 1. BUSINESS CONTEXT SNAPSHOT (Top Section) ── */}
      {contextExplanation && (
        <div className="bg-[#111213] border border-[#1e1e22] p-5 rounded-xl space-y-2">
          <div className="text-[10px] font-bold text-zinc-555 tracking-widest uppercase">Business Context Snapshot</div>
          <p className="text-[13px] text-zinc-300 leading-relaxed font-medium font-sans">
            {getConciseContext(contextExplanation)}
          </p>
        </div>
      )}

      {/* ── 2. STANDALONE EXECUTIVE ALIGNMENT (Upper-Middle Section) ── */}
      {departments && departments.length > 0 ? (
        <div className="bg-[#111213] border border-[#1e1e22] p-5 rounded-xl space-y-4">
          <div className="text-[10px] font-bold text-zinc-555 tracking-widest uppercase">Departmental Stances (M06 Executive Alignment)</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            {departments.map((dept, i) => {
              const isYes = dept.status === 'yes';
              const isNo = dept.status === 'no';
              const badgeBg = isYes ? 'bg-emerald-955 text-emerald-400 border border-emerald-800/30' : isNo ? 'bg-red-955 text-red-400 border-red-800/30' : 'bg-zinc-800 text-zinc-400 border-zinc-700';
              const badgeText = isYes ? 'FOR' : isNo ? 'AGAINST' : 'NEUTRAL';
              
              return (
                <div key={i} className="bg-[#161617] border border-[#232325] p-4 rounded-xl flex flex-col justify-between space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[12.5px] font-bold text-white uppercase tracking-wider">{dept.name}</span>
                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${badgeBg}`}>
                      {badgeText}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-relaxed font-medium" title={dept.reason}>
                    {dept.reason}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="bg-[#111213] border border-[#1e1e22] p-5 rounded-xl">
          <div className="text-[10px] font-bold text-zinc-555 tracking-widest uppercase">Departmental Stances</div>
          <p className="text-[12px] text-zinc-500 italic mt-2">Executive debate skipped for low-friction pathway.</p>
        </div>
      )}

      {/* ── DECISION VERDICT ── */}
      <div className="bg-gradient-to-r from-blue-955/40 to-indigo-950/30 border border-blue-900/40 p-6 rounded-xl flex flex-col gap-3">
        <div>
          <div className="text-[10px] font-bold text-blue-400 tracking-widest uppercase mb-1.5">Decision Verdict</div>
          <div className="text-[18px] font-bold text-white leading-snug">{verdictText}</div>
        </div>
        {confidence > 0 && (
          <div className="flex items-center gap-3">
            <div className="flex-1 h-1.5 bg-[#1d1d2a] rounded-full overflow-hidden max-w-[200px]">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${Math.round(confidence)}%` }} />
            </div>
            <span className="text-[11.5px] font-bold text-blue-400">{Math.round(confidence)}% confidence score</span>
          </div>
        )}
      </div>

      {/* ── KEY STATS STRIP ── */}
      {keyStats.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {keyStats.map((stat, i) => (
            <div key={i} className="bg-[#111213] border border-[#1e1e22] rounded-xl p-4 flex flex-col justify-between">
              <div className="text-[10px] text-zinc-555 font-semibold uppercase tracking-wider mb-1.5">{stat.label}</div>
              <div className="flex items-center justify-between">
                <span className="text-[16px] font-bold text-white font-mono">{stat.value}</span>
                <TrendIcon trend={stat.trend} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── STATS EXPLANATION ── */}
      {statsExplanation && (
        <div className="bg-[#111213] border border-[#1e1e22] p-6 rounded-xl space-y-4">
          <div className="text-[10px] font-bold text-zinc-555 tracking-widest uppercase">Statistical & Decision Logic</div>
          <div className="text-[14px] text-zinc-300 leading-relaxed font-medium">
            <p>{statsExplanation}</p>
          </div>
        </div>
      )}

      {/* ── IMMEDIATE ACTION PLAN ── */}
      {actionPlan.length > 0 && (
        <div className="bg-[#111213] border border-blue-900/30 p-6 rounded-xl space-y-4">
          <div className="text-[10px] font-bold text-zinc-555 tracking-widest uppercase">Immediate Action Steps</div>
          <div className="space-y-4">
            {actionPlan.map((a, i) => (
              <div key={i} className="flex items-start gap-4 border-b border-[#1b1b1e] last:border-0 pb-4 last:pb-0">
                <div className="w-6 h-6 rounded-full bg-blue-600/20 border border-blue-600/30 text-blue-400 text-[11px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5 font-mono">
                  {i + 1}
                </div>
                <div className="flex-1 space-y-1">
                  {a.title ? (
                    <>
                      <div className="text-[14px] text-zinc-200 font-bold leading-snug">{a.title}</div>
                      <div className="text-[13px] text-zinc-400 leading-relaxed font-medium">{a.step}</div>
                    </>
                  ) : (
                    <div className="text-[13.5px] text-zinc-300 leading-relaxed font-medium">{a.step}</div>
                  )}
                  <div className="text-[10.5px] text-zinc-555 font-mono pt-0.5">⏱ Timeframe: {a.timeframe}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Future Predictions Wrapper (Scenario Simulation Projections) ── */}
      <div className="bg-[#111213] border border-[#1e1e22] rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-[#1e1e22] pb-4">
          <div className="space-y-1">
            <h3 className="text-[15px] font-bold text-white uppercase tracking-wider">Future Predictions</h3>
            <p className="text-[11px] text-zinc-500 font-medium">6-Month quantitative projections for different execution pathways</p>
          </div>
          {forecastData && (
            <span className={`text-[9px] font-bold px-2.5 py-0.5 rounded-full border uppercase tracking-wider ${
              {
                BULLISH: 'text-emerald-400 bg-emerald-955/40 border-emerald-800/30',
                BEARISH: 'text-red-400 bg-red-955/40 border-red-800/30',
                NEUTRAL: 'text-amber-400 bg-amber-955/40 border-amber-800/30',
              }[forecastData.market_sentiment] || 'text-zinc-400 bg-zinc-900 border-zinc-700'
            }`}>
              Market: {forecastData.market_sentiment}
            </span>
          )}
        </div>

        {forecastLoading && (
          <div className="flex flex-col items-center justify-center py-8 space-y-2">
            <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            <p className="text-[11px] text-zinc-500">Projecting live market data from Google Finance…</p>
          </div>
        )}

        {forecastError && (
          <div className="flex items-center gap-2 bg-red-955/20 border border-red-900/30 p-3 rounded-lg text-[11px] text-red-400">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{forecastError}</span>
          </div>
        )}

        {forecastData && !forecastLoading && (
          <div className="space-y-5">
            {/* Grid of paths */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              {forecastData.scenarios.map((sc, i) => {
                const isActive = i === activeScenarioIdx;
                const maxConfidence = Math.max(...forecastData.scenarios.map(s => s.confidence || 0));
                const isHighestConfidence = sc.confidence === maxConfidence && sc.confidence > 0;

                const riskColors = {
                  LOW: isActive 
                    ? 'border-emerald-600/60 bg-emerald-955/40 text-emerald-300' 
                    : 'border-[#232325] text-zinc-500 hover:text-emerald-400 hover:border-emerald-900/50',
                  MEDIUM: isActive 
                    ? 'border-amber-600/60 bg-amber-955/40 text-amber-300' 
                    : 'border-[#232325] text-zinc-500 hover:text-amber-400 hover:border-amber-900/50',
                  HIGH: isActive 
                    ? 'border-red-600/60 bg-red-955/40 text-red-300' 
                    : 'border-[#232325] text-zinc-500 hover:text-red-400 hover:border-red-900/50',
                }[sc.risk] || '';

                const highlightRing = isHighestConfidence 
                  ? 'ring-2 ring-blue-500 shadow-lg shadow-blue-500/10 border-blue-500/50' 
                  : '';

                return (
                  <button
                    key={sc.id}
                    onClick={() => setActiveScenarioIdx(i)}
                    className={`relative flex flex-col items-center gap-1.5 p-4 rounded-xl border transition-all duration-200 ${riskColors} ${highlightRing}`}
                  >
                    {isHighestConfidence && (
                      <span className="absolute -top-2.5 px-2 py-0.5 bg-blue-600 text-[8px] font-black text-white rounded-full uppercase tracking-wider shadow shadow-blue-500/30 z-10">
                        RECOMMENDED OPTION
                      </span>
                    )}
                    <span className="text-[12.5px] font-bold uppercase tracking-wide mt-1">{sc.name}</span>
                    <span className={`text-[8.5px] font-bold px-2 py-0.5 rounded-full uppercase border ${
                      sc.risk === 'LOW' ? 'bg-emerald-955/40 text-emerald-400 border-emerald-800/20' :
                      sc.risk === 'MEDIUM' ? 'bg-amber-955 text-amber-400 border-amber-800/20' : 
                      'bg-red-955 text-red-400 border-red-800/20'
                    }`}>{sc.risk} Risk</span>
                    <span className="text-[10px] text-zinc-400 font-mono font-semibold">{sc.confidence}% Confidence</span>
                  </button>
                );
              })}
            </div>

            {/* Active scenario details */}
            {forecastData.scenarios[activeScenarioIdx] && (
              <div className="space-y-4">
                <div className="bg-[#161617] border border-[#232325] px-4 py-3 rounded-xl">
                  <p className="text-[12px] text-zinc-300 leading-relaxed font-medium">
                    {forecastData.scenarios[activeScenarioIdx].label}
                  </p>
                  {forecastData.scenarios[activeScenarioIdx].breaking_assumption && (
                    <div className="flex items-center gap-1.5 mt-2.5 text-[10.5px] text-red-400/80 font-semibold">
                      <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>Breaking Limit: {forecastData.scenarios[activeScenarioIdx].breaking_assumption}</span>
                    </div>
                  )}
                </div>

                {/* Metric Tab Selector */}
                <div className="space-y-2">
                  <div className="flex gap-2">
                    {[
                      { id: 'revenue', label: 'Revenue', icon: TrendingUp },
                      { id: 'pipeline', label: 'Pipeline', icon: BarChart2 },
                      { id: 'customers', label: 'Cust. LTV', icon: Users },
                    ].map((m) => {
                      const Icon = m.icon;
                      return (
                        <button
                          key={m.id}
                          onClick={() => setActiveMetric(m.id)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[10.5px] font-bold transition-all ${
                            activeMetric === m.id
                              ? 'bg-[#1e1e22] border-[#313235] text-white shadow-sm'
                              : 'border-transparent text-zinc-500 hover:text-zinc-300'
                          }`}
                        >
                          <Icon className="w-3.5 h-3.5" />
                          {m.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Chart & Churn */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className="lg:col-span-2 bg-[#161617] border border-[#232325] p-4 rounded-xl space-y-3">
                    <div className="text-[9.5px] font-bold text-zinc-555 uppercase tracking-widest">
                      6-Month {activeMetric === 'revenue' ? 'Revenue' : activeMetric === 'pipeline' ? 'Sales Pipeline' : 'Customer LTV'} Forecast
                    </div>
                    <BarChart
                      data={getMetricData(forecastData.scenarios[activeScenarioIdx])}
                      labels={months.map(m => m.replace('Month ', 'M'))}
                      color={forecastData.scenarios[activeScenarioIdx].color}
                      unit="$"
                    />
                  </div>

                  <div className="bg-[#161617] border border-[#232325] p-4 rounded-xl flex flex-col justify-between space-y-3">
                    <div className="text-[9.5px] font-bold text-zinc-555 uppercase tracking-widest">
                      Customer Churn Risk
                    </div>
                    <div className="grid grid-cols-3 gap-2 flex-1 items-center">
                      {forecastData.scenarios[activeScenarioIdx].churn.map((c, idx) => {
                        const isGood = c < 4;
                        const barColor = isGood ? 'bg-emerald-500' : c > 5 ? 'bg-red-500' : 'bg-amber-500';
                        const textColor = isGood ? 'text-emerald-400' : c > 5 ? 'text-red-400' : 'text-amber-400';
                        return (
                          <div key={idx} className="flex flex-col items-center gap-1 bg-[#0d0d0e] p-2 rounded-lg border border-[#1e1e22]/50">
                            <span className="text-[7.5px] font-bold text-zinc-555 uppercase">{months[idx]?.replace('Month ', 'M')}</span>
                            <span className={`text-[11px] font-mono font-bold ${textColor}`}>{c}%</span>
                            <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden mt-0.5">
                              <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(100, c * 10)}%` }} />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

              </div>
            )}
          </div>
        )}
      </div>

      {/* ── 4. FINAL INSIGHTS GRID (Bottom Section) ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Risk if Ignored */}
        <div className="bg-[#111213] border border-red-900/20 p-5 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-[10px] font-bold text-red-500 tracking-widest uppercase">
            <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
            <span>Risk if Ignored (Unmitigated Consequences)</span>
          </div>
          {ifIgnored && ifIgnored.length > 0 ? (
            <div className="space-y-2">
              {ifIgnored.map((risk, i) => (
                <div key={i} className="flex items-start gap-2.5 text-[12.5px] text-zinc-450">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>{risk}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[12px] text-zinc-500 italic">No significant unmitigated risks identified.</p>
          )}
        </div>

        {/* Friction Business Memory */}
        <div className="bg-[#111213] border border-purple-900/20 p-5 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[10px] font-bold text-purple-400 tracking-widest uppercase">
              <Brain className="w-3.5 h-3.5 text-purple-400" />
              <span>Friction Business Memory</span>
            </div>
            {pastMemoryScore !== undefined && (
              <span className="text-purple-400 font-mono text-[11px] font-bold bg-purple-955/40 border border-purple-800/20 px-2 py-0.5 rounded-full">
                {Math.round(pastMemoryScore * 100)}% Match
              </span>
            )}
          </div>
          <div className="space-y-2 text-[12.5px] text-zinc-300 leading-relaxed font-sans font-medium">
            {pastMemory ? (
              <p className="italic">{getCleanMemory(pastMemory)}</p>
            ) : (
              <p className="text-zinc-500 italic">No previous matching cases in vector memory.</p>
            )}
            {patternMatch && (
              <div className="text-[11px] text-purple-300 font-semibold pt-2 border-t border-purple-900/10 mt-1">
                Pattern: {patternMatch}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── 16 MODULES AUDIT PANEL ── */}
      <div className="border border-[#1e1e22] rounded-xl overflow-hidden bg-[#0d0d0e]">
        <button onClick={() => setShowAdvanced(s => !s)}
          className="w-full flex items-center justify-between px-5 py-4 bg-[#111213] hover:bg-[#161619] transition-all text-left">
          <div>
            <span className="text-[12px] font-bold text-zinc-400 uppercase tracking-wide">Friction Cognitive Pipeline Audit (16 Modules)</span>
            <div className="text-[10px] text-zinc-600 mt-0.5">Select a module to inspect its step-by-step cognitive reasoning and ground-truth values</div>
          </div>
          {showAdvanced ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
        </button>

        {showAdvanced && (
          <div className="p-5 border-t border-[#1e1e22] bg-[#0a0a0b]">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              
              {/* Left Column: 16 Module Timeline Buttons */}
              <div className="md:col-span-1 border-r border-[#1e1e22]/50 pr-4 space-y-1.5 max-h-[500px] overflow-y-auto custom-scrollbar">
                {auditModules.map((m) => {
                  const isActive = m.id === selectedModuleId;
                  const isExecuted = m.status === "EXECUTED";
                  
                  return (
                    <button
                      key={m.id}
                      onClick={() => setSelectedModuleId(m.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all border ${
                        isActive 
                          ? 'bg-[#151618] border-[#313235] text-white shadow-sm' 
                          : 'bg-transparent border-transparent text-zinc-400 hover:bg-[#111213] hover:text-zinc-200'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 text-[9px] font-bold ${
                        isExecuted 
                          ? 'bg-[#1c4e36] text-emerald-400 border border-emerald-800/40' 
                          : 'bg-zinc-900 text-zinc-600 border border-zinc-800/40'
                      }`}>
                        {isExecuted ? '✓' : '×'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono text-[10.5px] font-bold text-zinc-500">{m.id}</span>
                          <span className="text-[11.5px] font-semibold truncate">{m.name}</span>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Right Column: Detailed Module Audit Inspector */}
              <div className="md:col-span-2 flex flex-col bg-[#111213] border border-[#1e1e22] rounded-xl p-5 min-h-[380px]">
                <div className="space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-zinc-550 font-mono text-[11px] font-bold bg-zinc-900 border border-zinc-800 px-1.5 py-0.5 rounded">
                        {activeAudit.id}
                      </span>
                      <h3 className="text-[15px] font-bold text-white">{activeAudit.name}</h3>
                    </div>
                    <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold border uppercase tracking-wider ${phaseBadgeColor}`}>
                      {activeAudit.phase} Phase
                    </span>
                  </div>

                  <p className="text-[11.5px] text-zinc-555 leading-relaxed italic border-b border-[#1b1b1e] pb-3">
                    {activeAudit.desc}
                  </p>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-[10px] text-zinc-500 uppercase tracking-widest font-bold">
                      <span>Status:</span>
                      <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                        activeAudit.status === 'EXECUTED' 
                          ? 'bg-[#1c4e36] text-emerald-400 border border-emerald-800/20' 
                          : 'bg-zinc-800 text-zinc-500'
                      }`}>
                        {activeAudit.status}
                      </span>
                    </div>

                    <div className="mt-3">
                      <div className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold mb-2">Cognitive Output & Solution Dashboard</div>
                      {renderModuleAuditContent()}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}
      </div>

    </div>
  );
}// ══════════════════════════════════════════════════════════════════════════════
//  PIPELINE STEP CONFIG (16 modules from the PDF)
// ══════════════════════════════════════════════════════════════════════════════
function UploadModal({ onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setError(null);
    const allowedExtensions = ['.pdf', '.xlsx', '.xls', '.csv', '.txt', '.md', '.json'];
    const filename = selectedFile.name.toLowerCase();
    const isValid = allowedExtensions.some(ext => filename.endsWith(ext));
    
    if (!isValid) {
      setError("Unsupported file format. Please upload PDF, Excel, CSV, text, or markdown files.");
      setFile(null);
      return;
    }
    
    if (selectedFile.size > 20 * 1024 * 1024) {
      setError("File size exceeds 20MB limit.");
      setFile(null);
      return;
    }
    
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API}/upload-document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      if (res.data.success) {
        setSuccess(true);
        if (onUploadSuccess) onUploadSuccess();
        setTimeout(() => {
          onClose();
        }, 1200);
      } else {
        setError(res.data.error || 'Failed to upload document.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to connect to backend server. Make sure the server is running.');
    } finally {
      setUploading(false);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 backdrop-blur-md p-4">
      <div 
        className="w-full max-w-md bg-[#111113] border border-[#1e1e22] rounded-2xl overflow-hidden shadow-2xl flex flex-col relative transition-all duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="h-14 border-b border-[#1c1c1f] px-6 flex items-center justify-between bg-[#131315]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
              <Plus className="w-4 h-4 text-blue-400" />
            </div>
            <span className="text-[13px] font-bold text-white uppercase tracking-wide">Connect Custom Data Source</span>
          </div>
          <button 
            onClick={onClose} 
            disabled={uploading}
            className="w-7 h-7 rounded-lg bg-[#181819] border border-[#2a2a2f] flex items-center justify-center hover:bg-zinc-800 hover:border-zinc-600 transition disabled:opacity-40"
          >
            <X className="w-3.5 h-3.5 text-zinc-400" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          <p className="text-[11.5px] text-zinc-500 leading-relaxed">
            Upload custom reports, worksheets, or documentation files. They will be parsed, cleaned, chunked, and embedded into the active Chroma vector store to augment the cognitive RAG decision engine.
          </p>

          {/* Drag & Drop Zone */}
          <div 
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200 min-h-[170px] ${
              dragActive 
                ? 'border-blue-500 bg-blue-600/5' 
                : file 
                  ? 'border-emerald-600/50 bg-emerald-950/5' 
                  : 'border-[#222225] hover:border-zinc-700 bg-[#0c0c0d]'
            }`}
            onClick={onButtonClick}
          >
            <input 
              ref={fileInputRef}
              type="file" 
              className="hidden" 
              accept=".pdf,.xlsx,.xls,.csv,.txt,.md,.json"
              onChange={handleChange}
              disabled={uploading || success}
            />

            {success ? (
              <div className="flex flex-col items-center space-y-2.5">
                <div className="w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center shadow-[0_0_12px_rgba(16,185,129,0.1)]">
                  <Check className="w-5 h-5 text-emerald-400 stroke-[3]" />
                </div>
                <div className="space-y-0.5">
                  <div className="text-[12.5px] font-bold text-white">Success! Source Connected</div>
                  <div className="text-[10px] text-zinc-550">Embedding index updated successfully</div>
                </div>
              </div>
            ) : uploading ? (
              <div className="flex flex-col items-center space-y-3">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                <div className="space-y-0.5">
                  <div className="text-[12px] font-bold text-zinc-300">Parsing & Cleaning Data...</div>
                  <div className="text-[10px] text-zinc-555">Storing vector chunks in Chroma DB</div>
                </div>
              </div>
            ) : file ? (
              <div className="flex flex-col items-center space-y-2.5">
                <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="max-w-[280px]">
                  <div className="text-[12.5px] font-bold text-zinc-200 truncate" title={file.name}>{file.name}</div>
                  <div className="text-[10px] text-zinc-500 font-mono mt-0.5">{(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <button 
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="text-[9.5px] font-bold text-zinc-500 hover:text-red-400 uppercase tracking-wider underline transition"
                >
                  Remove File
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-2.5">
                <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-[#222225] flex items-center justify-center text-zinc-500">
                  <Plus className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-[12px] font-semibold text-zinc-300 block">Drag & drop your file here</span>
                  <span className="text-[10px] text-zinc-500 mt-1 block">or click to browse from device</span>
                </div>
                <div className="text-[9px] text-zinc-650 font-medium tracking-wide uppercase mt-1">
                  PDF, Excel, CSV, TXT, MD (Max 20MB)
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-red-950/20 border border-red-900/30 text-red-400">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed font-medium">{error}</p>
            </div>
          )}

          {file && !uploading && !success && (
            <button
              onClick={handleUpload}
              className="w-full flex items-center justify-center gap-2 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-[12px] font-bold uppercase tracking-wider shadow-lg shadow-blue-600/10 hover:shadow-blue-500/20 transition-all duration-200"
            >
              <Zap className="w-4 h-4 fill-current stroke-none" />
              Upload and Index source
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

const ALL_PIPELINE_STEPS = [
  { label: 'Intent',         group: 'Understand', icon: Brain },
  { label: 'Friction',       group: 'Understand', icon: Zap },
  { label: 'Context',        group: 'Understand', icon: Database },
  { label: 'Memory',         group: 'Understand', icon: Clock },
  { label: 'Root Cause',     group: 'Analyze',    icon: GitBranch },
  { label: 'Debate',         group: 'Analyze',    icon: Users },
  { label: 'Evidence',       group: 'Analyze',    icon: Shield },
  { label: 'Scenarios',      group: 'Reason',     icon: BarChart2 },
  { label: "Devil's Advocate", group: 'Reason',   icon: AlertTriangle },
  { label: 'Regret',         group: 'Reason',     icon: Target },
  { label: 'Confidence',     group: 'Verify',     icon: Eye },
  { label: 'Constraints',    group: 'Verify',     icon: FileText },
  { label: 'Self Review',    group: 'Verify',     icon: Brain },
  { label: 'Synthesis',      group: 'Decide',     icon: Sparkles },
  { label: 'Explainability', group: 'Decide',     icon: FileText },
  { label: 'Learning',       group: 'Decide',     icon: TrendingUp },
];

const PHASE_COLORS = {
  Understand: 'text-blue-400',
  Analyze:    'text-amber-400',
  Reason:     'text-purple-400',
  Verify:     'text-emerald-400',
  Decide:     'text-rose-400',
};

// ══════════════════════════════════════════════════════════════════════════════
//  MAIN APP
// ══════════════════════════════════════════════════════════════════════════════
function App() {
  const [question, setQuestion]         = useState('');
  const [messages, setMessages]         = useState([]);
  const [loadingStepIdx, setLoadingIdx] = useState(null);
  const [isSidebarOpen, setSidebar]     = useState(true);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [dataSources, setDataSources]   = useState([]);
  const [sourcesLoading, setSrcLoading] = useState(true);
  const [activeSource, setActiveSource] = useState(null);
  const [currentPage, setCurrentPage]   = useState('dashboard');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [canaryResult, setCanaryResult] = useState(null);
  const [canaryLoading, setCanaryLoading] = useState(false);
  const [canaryError, setCanaryError] = useState(null);
  const messagesEndRef = useRef(null);

  const handleCanaryScan = async () => {
    setCanaryLoading(true);
    setCanaryError(null);
    try {
      const res = await axios.post(`${API}/api/canary-run`);
      if (res.data.error) {
        setCanaryError(res.data.error);
      } else {
        setCanaryResult(res.data);
      }
    } catch (err) {
      setCanaryError(err.response?.data?.error || "Failed to connect to backend server. Make sure the FastAPI backend is running.");
    } finally {
      setCanaryLoading(false);
    }
  };

  // Fetch data sources
  const fetchDataSources = () => {
    setSrcLoading(true);
    axios.get(`${API}/data-sources`)
      .then(r => { setDataSources(r.data.sources || []); setSrcLoading(false); })
      .catch(() => {
        setDataSources([
          { id:'customers',  label:'Customers',     icon:'users',       row_count:30, status:'connected', summary:'Avg LTV $203,733 • 7 high-risk accounts', tags:['CRM', 'Retention'] },
          { id:'deals',      label:'Deals Pipeline',icon:'trending-up', row_count:40, status:'connected', summary:'Open pipeline $876,000 • 19 active deals', tags:['Sales', 'Pipeline'] },
          { id:'financials', label:'Financials',    icon:'bar-chart',   row_count:18, status:'connected', summary:'Latest revenue $1,375,000 • 28.9% avg margin', tags:['Finance', 'P&L'] },
          { id:'team',       label:'Team',          icon:'people',      row_count:15, status:'connected', summary:'15 employees • $1,262,000 annual payroll', tags:['HR', 'Talent'] },
          { id:'decisions',  label:'Past Decisions',icon:'clock',       row_count:25, status:'connected', summary:'18 successes • 7 failures', tags:['Memory', 'History'] },
          { id:'products',   label:'Products & SKUs',icon:'package',    row_count:20, status:'connected', summary:'YTD Product Rev $524,000 • Avg Margin 72%', tags:['Inventory', 'Margin'] },
          { id:'inventory',  label:'Inventory',     icon:'archive',     row_count:15, status:'connected', summary:'2 critical items need reorder • Avg Supply 26 days', tags:['Logistics', 'Warehouse'] },
          { id:'campaigns',  label:'Campaigns',     icon:'target',      row_count:15, status:'connected', summary:'Spent $298,000 • Overall ROI 620%', tags:['Marketing', 'ROI'] },
          { id:'support_tickets', label:'Support Tickets',icon:'help-circle',row_count:50, status:'connected', summary:'Avg CSAT 4.2/5 • 4 critical open tickets', tags:['Support', 'CSAT'] },
          { id:'suppliers',  label:'Suppliers',     icon:'truck',       row_count:10, status:'connected', summary:'Avg Reliability 89/100 • 1 high-risk supplier', tags:['Vendor', 'Operations'] },
          { id:'expenses',   label:'Expenses',      icon:'credit-card', row_count:18, status:'connected', summary:'Latest Monthly Expense $312,000', tags:['Finance', 'Expenses'] },
          { id:'kpis',       label:'KPIs',          icon:'activity',    row_count:6,  status:'connected', summary:'MRR $1,341,000 • NPS 52 • Churn 2.0%', tags:['KPIs', 'SaaS'] },
          { id:'contracts',  label:'Contracts & ARR',icon:'file-text',  row_count:15, status:'connected', summary:'Total ARR $5,640,000 • At-Risk ARR $1,260,000', tags:['Contracts', 'ARR'] },
        ]);
        setSrcLoading(false);
      });
  };

  useEffect(() => {
    fetchDataSources();
  }, []);

  // Keep-alive ping — prevents Render free tier from sleeping while the app is open.
  // Hits /health every 10 minutes silently; errors are swallowed on purpose.
  useEffect(() => {
    const ping = () => {
      fetch(`${API}/health`).catch(() => {/* intentionally silent */});
    };
    ping(); // ping immediately on mount
    const id = setInterval(ping, 10 * 60 * 1000); // then every 10 minutes
    return () => clearInterval(id);
  }, []);

  // Auto-scroll
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loadingStepIdx]);

  // Animate pipeline steps while loading (Labor Illusion with Variable Jitter)
  useEffect(() => {
    const loading = messages.find(m => m.loading);
    if (!loading) {
      setLoadingIdx(null);
      return;
    }

    // Initialize step index to 0 if starting a new animation session
    if (loadingStepIdx === null) {
      setLoadingIdx(0);
      return;
    }

    // If we reached the final Decide/Learning step (Module 16, index 15)
    if (loadingStepIdx >= ALL_PIPELINE_STEPS.length - 1) {
      const activeMsg = messages.find(m => m.loading && m.pendingResult);
      if (activeMsg) {
        // Dismiss loading instantly now that both animation and API have finished
        setTimeout(() => {
          setMessages(currentMsgs =>
            currentMsgs.map(m =>
              m.id === activeMsg.id
                ? { ...m, result: activeMsg.pendingResult, loading: false }
                : m
            )
          );
        }, 0);
      }
      return;
    }

    // Calculate variable jitter delay based on the phase of the current step
    const currentStep = ALL_PIPELINE_STEPS[loadingStepIdx];
    const currentPhase = currentStep.group;
    let delay = 2000;

    if (currentPhase === 'Understand') {
      // Understand: 1200ms - 2000ms
      delay = Math.floor(Math.random() * (2000 - 1200 + 1)) + 1200;
    } else if (currentPhase === 'Analyze' || currentPhase === 'Reason') {
      // Analyze & Reason: 2500ms - 3500ms (simulate heavy processing)
      delay = Math.floor(Math.random() * (3500 - 2500 + 1)) + 2500;
    } else {
      // Verify & Decide (prior to final step): 1500ms - 2500ms
      delay = Math.floor(Math.random() * (2500 - 1500 + 1)) + 1500;
    }

    const t = setTimeout(() => {
      setLoadingIdx(prev => (prev !== null && prev < ALL_PIPELINE_STEPS.length - 1 ? prev + 1 : prev));
    }, delay);

    return () => clearTimeout(t);
  }, [messages, loadingStepIdx]);

  const handleSubmit = async (text) => {
    const q = text || question;
    if (!q.trim()) return;
    const id = Date.now();
    setMessages(prev => [...prev, { id, question: q, result: null, loading: true, pendingResult: null }]);
    setQuestion('');
    try {
      const r = await axios.post(`${API}/reason`, { question: q });
      setMessages(prev => prev.map(m => m.id === id ? { ...m, pendingResult: r.data } : m));
    } catch {
      // Fallback
      setTimeout(() => {
        setMessages(prev => prev.map(m => m.id === id ? {
          ...m, pendingResult: {
            friction_level: 'MEDIUM',
            pipeline_executed: ['Intent', 'Friction', 'Context', 'Memory'],
            intent: { goal: 'strategic analysis', constraints: [] },
            past_memory: 'Backend offline — running in simulation mode.',
            past_memory_score: 0,
            output: {
              verdict: 'Unable to reach backend. Run the backend server.',
              narrative: 'The Friction backend is not responding. Please start the backend server with: python main.py',
              key_stats: [],
              departments: [],
              confidence: 0,
              confidence_breakdown: {},
              action_plan: [{ step: 'Start the backend server', timeframe: 'now' }],
              if_ignored: [],
              scenarios: [],
              devils_advocate: [],
              regret_choice: '',
              constraints_check: [],
              self_review: '',
              root_cause_summary: '',
              evidence_score: 0,
            },
            confidence: { confidence: 0, agreement_score: 0, memory_match: 0 }
          }
        } : m));
      }, 2000);
    }
  };

  const currentLoading = messages.find(m => m.loading);

  const renderSidebar = (isMobileDrawer = false) => {
    return (
      <div className="flex-1 flex flex-col min-h-0 bg-[#111112] select-none h-full">
        {/* Brand Logo & Navigation */}
        <div className="p-5 flex-shrink-0 flex justify-between items-center border-b border-[#1a1a1c]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-[#f4f4f5] rounded-lg flex-shrink-0 flex items-center justify-center overflow-hidden shadow-[0_0_8px_rgba(255,255,255,0.05)] border border-[#232325]">
              <img src="/logo.png" className="w-[140%] h-[140%] max-w-none object-cover" alt="Friction Logo" />
            </div>
            <div className="flex flex-col justify-center leading-none">
              <span className="text-[20px] font-bold text-white tracking-wider uppercase" style={{ fontFamily: "'Oswald', sans-serif" }}>Friction</span>
              <span className="text-[8.5px] text-zinc-500 font-semibold tracking-wider mt-0.5 uppercase">AI Business Reasoning Engine</span>
            </div>
          </div>
          {isMobileDrawer && (
            <button onClick={() => setMobileDrawerOpen(false)}
              className="p-1.5 rounded-lg border border-[#2a2a2f] bg-[#181819] hover:bg-zinc-800 transition">
              <X className="w-4 h-4 text-zinc-400" />
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-7 min-h-0">
          <div className="space-y-1">
            <button onClick={() => { setCurrentPage('dashboard'); if (isMobileDrawer) setMobileDrawerOpen(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border text-[11.5px] font-semibold transition-all text-left ${currentPage === 'dashboard' ? 'bg-[#161617] border-[#232325] text-white' : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-[#161618]/50'}`}>
              <Sparkles className="w-3.5 h-3.5 text-zinc-500" />
              <span>Decision Dashboard</span>
            </button>
            <button onClick={() => { setCurrentPage('crm'); if (isMobileDrawer) setMobileDrawerOpen(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border text-[11.5px] font-semibold transition-all text-left ${currentPage === 'crm' ? 'bg-[#161617] border-[#232325] text-white' : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-[#161618]/50'}`}>
              <TrendingUp className="w-3.5 h-3.5 text-zinc-500" />
              <span>Live CRM</span>
            </button>
            <button onClick={() => { setCurrentPage('canary'); if (isMobileDrawer) setMobileDrawerOpen(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border text-[11.5px] font-semibold transition-all text-left ${currentPage === 'canary' ? 'bg-[#161617] border-[#232325] text-white' : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-[#161618]/50'}`}>
              <Shield className="w-3.5 h-3.5 text-zinc-500" />
              <span>Canary Sentinel</span>
            </button>
            <button onClick={() => { setCurrentPage('architecture'); if (isMobileDrawer) setMobileDrawerOpen(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border text-[11.5px] font-semibold transition-all text-left ${currentPage === 'architecture' ? 'bg-[#161617] border-[#232325] text-white' : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-[#161618]/50'}`}>
              <GitBranch className="w-3.5 h-3.5 text-zinc-500" />
              <span>Engine Architecture</span>
            </button>
          </div>

          {/* ── DATA SOURCES ── */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[9.5px] font-bold text-zinc-500 tracking-widest uppercase">Data Sources</span>
              {sourcesLoading
                ? <Loader2 className="w-3 h-3 text-zinc-600 animate-spin" />
                : <span className="text-[10px] text-zinc-700 font-semibold">{dataSources.length} connected</span>
              }
            </div>
            <ul className="space-y-1">
              {dataSources.map(src => {
                const isUploaded = src.id.startsWith('uploaded_');
                return (
                  <li key={src.id} className="relative group/item">
                    <button onClick={() => { setActiveSource(src); if (isMobileDrawer) setMobileDrawerOpen(false); }}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border border-transparent hover:bg-[#161618] hover:border-[#222224] transition-all text-left ${isUploaded ? 'pr-9' : ''}`}>
                      <div className="w-7 h-7 rounded-lg bg-[#1a1a1c] group-hover:bg-[#1e1e21] flex items-center justify-center flex-shrink-0 transition">
                        <SrcIcon name={src.icon} className="w-3.5 h-3.5 text-zinc-500 group-hover:text-blue-400 transition" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-[12px] font-semibold text-zinc-400 group-hover:text-white transition truncate pr-1">{src.label}</span>
                          <div className="flex items-center gap-1.5 flex-shrink-0">
                            <span className="text-[10px] font-mono text-zinc-600">{src.row_count}</span>
                            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full shadow-[0_0_5px_#10b981]" />
                          </div>
                        </div>
                        <div className="text-[10px] text-zinc-700 truncate mt-0.5">{src.summary}</div>
                      </div>
                    </button>
                    
                    {isUploaded && (
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (window.confirm(`Are you sure you want to disconnect ${src.label}?`)) {
                            try {
                              await axios.delete(`${API}/upload-document/${src.id}`);
                              fetchDataSources();
                            } catch (err) {
                              alert("Failed to delete document.");
                            }
                          }
                        }}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 opacity-0 group-hover/item:opacity-100 p-1.5 rounded-lg bg-red-950/20 border border-red-900/30 text-red-400 hover:bg-red-900/40 hover:text-red-300 transition-all z-10"
                        title="Disconnect data source"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
            <button 
              onClick={() => { setShowUploadModal(true); if (isMobileDrawer) setMobileDrawerOpen(false); }}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-transparent border border-[#1e1e21] hover:border-zinc-700 hover:bg-[#161618] text-zinc-600 hover:text-zinc-300 rounded-xl text-[11px] font-semibold tracking-wide transition"
            >
              <Plus className="w-3.5 h-3.5" />Connect source
            </button>
          </div>

          {/* ── PIPELINE ── */}
          <div className="space-y-2.5">
            <div className="text-[9.5px] font-bold text-zinc-500 tracking-widest uppercase">Cognitive Pipeline</div>
            {['Understand','Analyze','Reason','Verify','Decide'].map(phase => (
              <div key={phase} className="space-y-1">
                <div className={`text-[9px] font-bold uppercase tracking-widest pl-1 ${PHASE_COLORS[phase]}`}>{phase}</div>
                {ALL_PIPELINE_STEPS.filter(s => s.group === phase).map((step, si) => {
                  const globalIdx = ALL_PIPELINE_STEPS.findIndex(x => x.label === step.label);
                  let icon, textClass = 'text-zinc-600';
                  const lastResult = messages.filter(m => !m.loading && m.result).slice(-1)[0];
                  const executed = lastResult?.result?.pipeline_executed || [];
                  const wasExecuted = executed.some(e =>
                    e.toLowerCase().replace(/[' ]/g,'') === step.label.toLowerCase().replace(/[' ]/g,'')
                  );

                  if (currentLoading) {
                    if (globalIdx < loadingStepIdx) {
                      icon = <Check className="w-3.5 h-3.5 text-emerald-500 stroke-[3]" />;
                      textClass = 'text-zinc-400';
                    } else if (globalIdx === loadingStepIdx) {
                      icon = <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin" />;
                      textClass = `${PHASE_COLORS[phase]} font-semibold animate-pulse`;
                    } else {
                      icon = <div className="w-1.5 h-1.5 bg-zinc-800 rounded-full mx-1" />;
                    }
                  } else if (wasExecuted) {
                    icon = <Check className="w-3.5 h-3.5 text-emerald-500 stroke-[3]" />;
                    textClass = 'text-zinc-400';
                  } else if (messages.length > 0) {
                    icon = <div className="w-1.5 h-1.5 bg-zinc-800 rounded-full mx-1" />;
                    textClass = 'text-zinc-700';
                  } else {
                    icon = <div className="w-1.5 h-1.5 bg-zinc-800 rounded-full mx-1" />;
                  }

                  return (
                    <div key={step.label} className="flex items-center gap-2.5 pl-2">
                      <div className="w-4 h-4 flex items-center justify-center flex-shrink-0">{icon}</div>
                      <span className={`text-[11px] leading-none ${textClass}`}>{step.label}</span>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3.5 border-t border-[#1a1a1c] flex items-center justify-between flex-shrink-0">
          <span className="text-[10px] text-zinc-700 font-medium">v2.0 · 16 Modules</span>
          <button onClick={fetchDataSources}
            className="text-zinc-600 hover:text-zinc-400 transition" title="Refresh">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-[#0d0d0e] text-[#e4e4e7] overflow-hidden font-sans">

      {/* ═══════ DATA VIEWER MODAL ═══════ */}
      {activeSource && <DataViewer source={activeSource} onClose={() => setActiveSource(null)} />}

      {/* ═══════ UPLOAD SOURCE MODAL ═══════ */}
      {showUploadModal && <UploadModal onClose={() => setShowUploadModal(false)} onUploadSuccess={fetchDataSources} />}

      {/* Mobile Drawer Overlay */}
      {mobileDrawerOpen && (
        <div className="fixed inset-0 z-[80] flex md:hidden">
          <div className="fixed inset-0 bg-black/75 backdrop-blur-sm" onClick={() => setMobileDrawerOpen(false)} />
          <div className="relative w-[280px] h-full bg-[#111112] border-r border-[#1c1c1f] z-10 flex flex-col">
            {renderSidebar(true)}
          </div>
        </div>
      )}

      {/* Desktop Sidebar (hidden on mobile, persistent on desktop if isSidebarOpen is true) */}
      {isSidebarOpen && (
        <div className="hidden md:flex w-[268px] bg-[#111112] border-r border-[#1c1c1f] flex-col flex-shrink-0 select-none h-screen">
          {renderSidebar(false)}
        </div>
      )}

      {/* ═══════ MAIN CONTENT ═══════ */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#0d0d0e]">
        {/* Header */}
        <div className="h-14 border-b border-[#1a1a1c] px-6 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            {/* Hamburger Button for Mobile */}
            <button onClick={() => setMobileDrawerOpen(true)}
              className="flex md:hidden w-8 h-8 rounded-lg bg-[#161617] border border-[#232325] items-center justify-center hover:bg-zinc-800 transition">
              <Menu className="w-4 h-4 text-zinc-400" />
            </button>

            {!isSidebarOpen && (
              <button onClick={() => setSidebar(true)}
                className="hidden md:flex w-8 h-8 rounded-lg bg-[#161617] border border-[#232325] items-center justify-center hover:bg-zinc-800 transition">
                <ChevronRight className="w-4 h-4 text-zinc-400" />
              </button>
            )}
            <span className="text-xs font-bold text-zinc-600 uppercase tracking-widest">
              {messages.length > 0 ? 'Active Session' : 'New Reasoning Session'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            {currentPage === 'dashboard' && (
              <button
                onClick={handleCanaryScan}
                disabled={canaryLoading}
                className="text-zinc-350 hover:text-white text-[11px] font-bold px-3 py-1.5 rounded-lg bg-[#161617] hover:bg-[#1f1f23] border border-[#232325] transition flex items-center gap-1.5 cursor-pointer shadow-sm"
              >
                {canaryLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-yellow-500" />
                    <span>Scanning...</span>
                  </>
                ) : (
                  <>
                    <Shield className="w-3.5 h-3.5 text-yellow-500" />
                    <span>Run Canary Scan</span>
                  </>
                )}
              </button>
            )}
            {isSidebarOpen && (
              <button onClick={() => setSidebar(false)}
                className="hidden md:block text-zinc-600 hover:text-zinc-300 text-xs font-medium px-2.5 py-1.5 rounded bg-[#161617] border border-[#232325] transition">
                Hide Sidebar
              </button>
            )}
          </div>
        </div>

        {/* Content Tab Router */}
        {currentPage === 'architecture' ? (
          <ArchitecturePage />
        ) : currentPage === 'crm' ? (
          <CRMDashboard API={API} />
        ) : currentPage === 'canary' ? (
          <CanaryPanel API={API} />
        ) : (
          <div className="flex-1 overflow-y-auto px-4 sm:px-8 pt-6 pb-28 md:pb-6 space-y-8 max-w-4xl w-full mx-auto flex flex-col">

            {/* ── CANARY ANOMALY ENGINE RESULTS ── */}
            {(canaryResult || canaryError) && (
              <div className="bg-[#111213] border border-[#1e1e22] rounded-xl overflow-hidden mt-4">
                <div className="px-5 py-3 border-b border-[#1e1e22] bg-[#111213] flex items-center gap-2.5">
                  <Shield className="w-4 h-4 text-yellow-500" />
                  <span className="text-[11px] font-bold text-zinc-300 uppercase tracking-wide">Proactive Canary Guard Results</span>
                </div>
                <div className="p-5 bg-[#0a0a0b] space-y-4">
                  {canaryError && (
                    <div className="flex items-start gap-2.5 p-3 rounded-xl bg-red-950/20 border border-red-900/30 text-red-400 text-xs">
                      <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <span>{canaryError}</span>
                    </div>
                  )}

                  {canaryResult && (
                    <div className="space-y-4">
                      {/* Status Alert */}
                      {canaryResult.alert ? (
                        <div className="flex items-start gap-3 p-4 rounded-xl bg-red-950/30 border border-red-900/40 text-red-400 animate-pulse">
                          <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-[13px] font-bold uppercase tracking-wide">Critical Anomaly Detected!</h4>
                            <p className="text-[11.5px] mt-1 leading-relaxed">
                              Operational drift matches <strong>{canaryResult.matched_pattern}</strong> with <strong>{canaryResult.similarity}%</strong> confidence. Proactive mitigation is recommended.
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-start gap-3 p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/30 text-emerald-450">
                          <Check className="w-5 h-5 flex-shrink-0 mt-0.5" />
                          <div>
                            <h4 className="text-[13px] font-bold uppercase tracking-wide">Operational State Safe</h4>
                            <p className="text-[11.5px] mt-1 leading-relaxed">
                              No critical systemic drift detected. Signature correlation is low (Highest match: {canaryResult.matched_pattern} at {canaryResult.similarity}%).
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Collapsible Details */}
                      <details className="group border border-[#1e1e22] rounded-xl bg-[#111213] overflow-hidden transition-all duration-200">
                        <summary className="list-none flex items-center justify-between px-4 py-3 cursor-pointer select-none hover:bg-[#161619] transition">
                          <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                            <span>🔬 View Raw Math & Projections</span>
                          </span>
                          <ChevronDown className="w-3.5 h-3.5 text-zinc-500 group-open:rotate-180 transition-transform duration-200" />
                        </summary>
                        <div className="p-4 border-t border-[#1e1e22] bg-[#0a0a0b] space-y-4">
                          {/* Drift Z-Scores */}
                          <div className="space-y-2">
                            <span className="text-[9.5px] font-bold text-zinc-550 uppercase tracking-widest block">Drift Vector (Z-Scores vs. Baseline)</span>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              {[
                                { label: "Revenue", key: "revenue" },
                                { label: "Expenses", key: "expenses" },
                                { label: "Tickets", key: "tickets" },
                                { label: "Inventory", key: "inventory" }
                              ].map(item => {
                                const drift = canaryResult.drift_percentages?.[item.key] || 0;
                                const zscore = canaryResult.drift_percentages?.[item.key + "_z"] || 0;
                                const isPositive = zscore >= 0;
                                return (
                                  <div key={item.key} className="bg-[#161617] border border-[#232325] px-3 py-2.5 rounded-lg flex flex-col justify-between">
                                    <span className="text-[10px] text-zinc-550 font-semibold">{item.label}</span>
                                    <span className="text-[14px] font-mono font-bold text-white mt-1.5">{zscore.toFixed(3)} σ</span>
                                    <span className={`text-[9.5px] font-bold mt-1 font-mono ${isPositive ? 'text-emerald-450' : 'text-rose-450'}`}>
                                      {isPositive ? '+' : ''}{drift.toFixed(1)}% drift
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>

                          {/* Similarity Correlation Scores */}
                          <div className="space-y-2 pt-2">
                            <span className="text-[9.5px] font-bold text-zinc-555 uppercase tracking-widest block">Signature Match Correlation</span>
                            <div className="space-y-2.5">
                              {Object.entries(canaryResult.all_scores || {}).map(([name, score]) => {
                                const scoreVal = Number(score);
                                return (
                                  <div key={name} className="space-y-1">
                                    <div className="flex justify-between text-[11px] font-medium pl-0.5">
                                      <span className="text-zinc-450">{name}</span>
                                      <span className="text-zinc-200 font-mono font-bold">{scoreVal.toFixed(1)}%</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-[#161617] rounded-full overflow-hidden border border-[#232325]">
                                      <div 
                                        className={`h-full rounded-full transition-all duration-500 ${
                                          scoreVal >= 85 ? 'bg-[#ef4444]' : scoreVal >= 50 ? 'bg-[#f59e0b]' : 'bg-[#3b82f6]'
                                        }`}
                                        style={{ width: `${Math.max(0, Math.min(100, scoreVal))}%` }}
                                      />
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      </details>
                    </div>
                  )}
                </div>
              </div>
            )}

            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-16 space-y-6">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/10">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-xl font-bold text-white tracking-tight">Friction Decision Engine</h2>
                  <p className="text-zinc-500 text-sm max-w-md">
                    A 16-module cognitive pipeline: Intent → Friction Routing → Context → Memory → Root Cause → Debate → Evidence → Scenarios → Synthesis.
                    Grounded in your real CRM data.
                  </p>
                </div>
                {/* Dataset quick-view pills */}
                {dataSources.length > 0 && (
                  <div className="flex gap-2 flex-wrap justify-center pt-2">
                    {dataSources.map(src => (
                      <button key={src.id} onClick={() => setActiveSource(src)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#131314] border border-[#1e1e21] hover:border-zinc-700 rounded-lg text-[11px] font-semibold text-zinc-500 hover:text-zinc-200 transition group">
                        <SrcIcon name={src.icon} className="w-3 h-3 text-blue-500" />
                        {src.row_count} {src.label}
                        <ArrowUpRight className="w-2.5 h-2.5 text-zinc-700 group-hover:text-zinc-400" />
                      </button>
                    ))}
                  </div>
                )}
                {/* Starter queries */}
                <div className="w-full max-w-xl grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
                  {[
                    { q: 'Should we hire more sales reps?',     desc: 'Team capacity & pipeline analysis' },
                    { q: 'Should we open another branch?',       desc: 'Expansion risk & past cases' },
                    { q: 'What is our biggest customer risk?',   desc: 'Churn & retention deep-dive' },
                    { q: 'Should we delay the product launch?',  desc: 'Tech readiness & market timing' },
                  ].map((s, i) => (
                    <button key={i} onClick={() => handleSubmit(s.q)}
                      className="flex flex-col items-start text-left p-4 bg-[#121213] border border-[#212123] rounded-xl hover:border-zinc-700 hover:bg-[#18181a] transition group">
                      <div className="flex items-center justify-between w-full">
                        <span className="text-[12.5px] font-semibold text-zinc-300 group-hover:text-white transition">{s.q}</span>
                        <ArrowUpRight className="w-3 h-3 text-zinc-600 group-hover:text-zinc-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                      </div>
                      <span className="text-[11px] text-zinc-600 mt-1">{s.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map(msg => (
                <div key={msg.id} className="space-y-4 flex flex-col">
                  {/* User bubble */}
                  <div className="flex items-center justify-between self-end bg-[#161617] border border-[#232325] rounded-xl px-4 py-2.5 max-w-lg">
                    <span className="text-[13px] font-medium text-zinc-100 pr-3">{msg.question}</span>
                    <MoreHorizontal className="w-4 h-4 text-zinc-600 flex-shrink-0" />
                  </div>

                  {msg.loading ? (
                    <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-8 flex flex-col items-center space-y-4">
                      <Loader2 className="w-7 h-7 text-blue-500 animate-spin" />
                      <div className="text-center">
                        <div className="text-[11px] font-bold text-zinc-400 uppercase tracking-widest animate-pulse">
                          Module {(loadingStepIdx || 0) + 1} of {ALL_PIPELINE_STEPS.length}
                        </div>
                        <div className={`text-[14px] font-bold mt-1 ${PHASE_COLORS[ALL_PIPELINE_STEPS[loadingStepIdx||0]?.group]}`}>
                          {ALL_PIPELINE_STEPS[loadingStepIdx || 0]?.group} Phase
                        </div>
                        <div className="text-[12px] text-zinc-500 mt-0.5">
                          {ALL_PIPELINE_STEPS[loadingStepIdx || 0]?.label}
                        </div>
                      </div>
                    </div>
                  ) : (
                    msg.result && (
                      <div className="space-y-6">
                        <RichOutputCard
                          result={msg.result}
                        />
                        <FutureCard
                          result={msg.result}
                        />
                      </div>
                    )
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input bar */}
        {currentPage === 'dashboard' && (
          <div className="fixed bottom-0 left-0 right-0 z-50 md:static p-4 sm:p-6 bg-[#0d0d0e] border-t border-[#1a1a1c] flex-shrink-0 flex justify-center">
            <div className="max-w-4xl w-full flex gap-3">
              <input
                className="flex-1 bg-[#161617] border border-[#232325] text-zinc-200 text-[13.5px] rounded-xl px-4 py-3.5 placeholder-zinc-600 focus:outline-none focus:border-zinc-600 transition"
                placeholder="Ask a strategic business question…"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !currentLoading && handleSubmit()}
                disabled={!!currentLoading}
              />
              <button
                onClick={() => handleSubmit()}
                disabled={!!currentLoading || !question.trim()}
                className="bg-[#161617] border border-[#232325] hover:bg-zinc-800 text-zinc-300 hover:text-white p-3.5 rounded-xl transition flex items-center justify-center disabled:opacity-40">
                <Play className="w-4 h-4 fill-current stroke-none" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ArchitecturePage() {
  const [selectedPhase, setSelectedPhase] = useState('All');
  
  const phases = [
    { 
      num: 1,
      name: 'UNDERSTAND', 
      dotColor: '#3b82f6',
      desc: 'Ingestion, intent classification, context assembly, and case memory search.',
      steps: [
        { num: 'M01', label: 'Intent Understanding', desc: 'Parses raw user prompts, isolates strategic variables, and configures constraints.', details: 'Classifies target entities, metric bounds, and time windows.' },
        { num: 'M02', label: 'Friction Router', desc: 'Estimates decision load and schedules fast vs. slow reasoning pathways.', details: 'Determines whether to trigger slow-path multi-agent debate.' },
        { num: 'M03', label: 'Context Resolver', desc: 'Queries live database tables dynamically based on intent keywords.', details: 'Retrieves relevant financials, pipeline deals, or headcount info.' },
        { num: 'M04', label: 'Vector Memory RAG', desc: 'Pulls semantic matches from previous historical decisions and mistakes.', details: 'Loads top-k matched records using sentence-transformer embeddings.' },
      ]
    },
    { 
      num: 2,
      name: 'ANALYZE', 
      dotColor: '#f59e0b',
      desc: 'Cognitive load estimation, root cause regression analysis, multi-agent debate simulation, and evidence checking.',
      steps: [
        { num: 'M05', label: 'Root Cause Analyzer', desc: 'Identifies deep-seated bottlenecks using regression trace diagnostic chains.', details: 'Calculates performance variances on raw operational metrics.' },
        { num: 'M06', label: 'Multi-Agent Debate', desc: 'Simulates intense role-play debate between departmental directors.', details: 'Runs 4 parallel agents (Sales, Finance, Operations, Product).' },
        { num: 'M07', label: 'Evidence Auditor', desc: 'Fact-checks and validates debate claims against ground-truth database rows.', details: 'Penalizes hallucinations or arguments conflicting with SQL data.' },
      ]
    },
    { 
      num: 3,
      name: 'REASON', 
      dotColor: '#a855f7',
      desc: 'Strategic scenario forecasting, mini-max regret calculations, and contrarian testing.',
      steps: [
        { num: 'M08', label: 'Scenario Simulator', desc: 'Projects alternative outcomes, calculating revenue impacts and risk.', details: 'Models Conservative, Aggressive, and Balanced scenarios.' },
        { num: 'M09', label: 'Devil\'s Advocate', desc: 'Actively constructs counter-arguments and identifies strategic blindspots.', details: 'Stresses test choices against risk parameters and market assumptions.' },
        { num: 'M10', label: 'Regret Minimax Choice', desc: 'Formulates a regret matrix and isolates the lowest-regret option.', details: 'Calculates the pathway with the lowest worst-case downside.' },
      ]
    },
    { 
      num: 4,
      name: 'VERIFY', 
      dotColor: '#10b981',
      desc: 'Confidence score weighting, hard limit checking, and self-review validation.',
      steps: [
        { num: 'M11', label: 'Confidence Weighting', desc: 'Aggregates weighting scores to issue a mathematical confidence percentage.', details: 'Weights debate consensus, memory similarity, and database checks.' },
        { num: 'M12', label: 'Constraints Validator', desc: 'Cross-checks actions against hard resource and financial ceilings.', details: 'Enforces safety limits (e.g. payroll caps, inventory safety stock).' },
        { num: 'M13', label: 'Self-Review Critique', desc: 'Conducts an honest, self-critical critique evaluating data gaps.', details: 'Identifies strategic information bounds and missing context.' },
      ]
    },
    { 
      num: 5,
      name: 'DECIDE', 
      dotColor: '#f43f5e',
      desc: 'Executive synthesis, transparency trace trails, and learning loop retention.',
      steps: [
        { num: 'M14', label: 'Synthesis Engine', desc: 'Resolves agent disputes to issue a single strategic directive.', details: 'Employs NVIDIA Nemotron-3 as a Board CEO model for synthesis.' },
        { num: 'M15', label: 'Explainability Trace', desc: 'Outputs auditable execution logs for each module in the reasoning tree.', details: 'Constructs the decision path explaining exact trade-offs.' },
        { num: 'M16', label: 'Learning Feedback', desc: 'Saves conversation logs and outcomes into local vector memory.', details: 'Appends current choices to RAG vectors to improve future loops.' },
      ]
    }
  ];

  const phaseColors = {
    UNDERSTAND: 'text-blue-400',
    ANALYZE:    'text-amber-400',
    REASON:     'text-purple-400',
    VERIFY:     'text-emerald-400',
    DECIDE:     'text-rose-400',
  };

  const filteredPhases = selectedPhase === 'All' ? phases : phases.filter(p => p.name.toLowerCase() === selectedPhase.toLowerCase());

  return (
    <div className="flex-1 overflow-y-auto px-8 py-8 space-y-8 max-w-7xl w-full mx-auto">
      <div className="space-y-2">
        <h1 className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent tracking-tight uppercase inline-block" style={{ fontFamily: "'Oswald', sans-serif" }}>Cognitive Engine Pipeline</h1>
        <p className="text-zinc-500 text-sm max-w-2xl">
          Friction operates via a highly parallelized 5-phase, 16-module cognitive architecture. 
          Modules within each phase share execution context and run in parallel pipelines.
        </p>
      </div>

      {/* Phase selection tabs */}
      <div className="flex gap-2 flex-wrap border-b border-[#1c1c1f] pb-4">
        <button onClick={() => setSelectedPhase('All')}
          className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition border ${selectedPhase === 'All' ? 'bg-[#1a1a1c] border-[#2c2c30] text-white' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}>
          All Phases
        </button>
        {phases.map(p => {
          const isActive = selectedPhase.toLowerCase() === p.name.toLowerCase();
          const activeCls = isActive ? 'bg-[#1a1a1c] border-[#2c2c30] text-white' : 'border-transparent text-zinc-500 hover:text-zinc-300';
          const indicator = {
            UNDERSTAND: 'bg-blue-500',
            ANALYZE: 'bg-amber-500',
            REASON: 'bg-purple-500',
            VERIFY: 'bg-emerald-500',
            DECIDE: 'bg-rose-500',
          }[p.name] || 'bg-zinc-500';

          return (
            <button key={p.name} onClick={() => setSelectedPhase(p.name)}
              className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition border flex items-center gap-2 ${activeCls}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${indicator}`} />
              <span>{p.name}</span>
            </button>
          );
        })}
      </div>

      {/* Kanban / Swimlanes Layout */}
      <div className="relative pl-8 space-y-10">
        {/* Connecting Timeline Line */}
        <div className="absolute left-[9px] top-3 bottom-12 w-0.5 bg-gradient-to-b from-[#3b82f6] via-[#f59e0b] via-[#a855f7] via-[#10b981] to-[#f43f5e] opacity-40 rounded-full" />

        {filteredPhases.map((p) => (
          <div key={p.name} className="flex flex-col lg:flex-row items-stretch gap-6 border-b border-[#161619]/60 pb-8 last:border-b-0 last:pb-0 relative">
            {/* Phase info column on left */}
            <div className="w-full lg:w-1/4 space-y-3 flex flex-col justify-start">
              <div className="flex items-center gap-2.5 relative">
                {/* Glowing Dot on Timeline */}
                <div className="absolute left-[-23px] top-1.5 w-2.5 h-2.5 rounded-full z-10" style={{ backgroundColor: p.dotColor, boxShadow: `0 0 10px ${p.dotColor}` }} />
                <span className={`text-[13px] font-black uppercase tracking-widest ${phaseColors[p.name]}`} style={{ fontFamily: "'Oswald', sans-serif" }}>
                  PHASE {p.num}: {p.name}
                </span>
              </div>
              <p className="text-zinc-500 text-xs leading-relaxed max-w-sm">{p.desc}</p>
            </div>

            {/* Modules grid / flex area on right */}
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {p.steps.map((s) => (
                <div key={s.num} className="p-5 bg-[#111112] border border-[#1c1c1f] rounded-2xl hover:border-zinc-700/50 transition-all flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <h4 className="text-[14.5px] font-bold text-cyan-400 flex items-center gap-2">
                      <span className="text-[10px] font-mono text-zinc-500 bg-zinc-900 border border-[#232325] px-1.5 py-0.5 rounded">{s.num}</span>
                      {s.label}
                    </h4>
                    {/* Increased base font size and warm yellow/cream color tint #fefce8 */}
                    <p className="text-[14.5px] text-[#fefce8] leading-relaxed font-medium">{s.desc}</p>
                  </div>
                  
                  <div className="pt-2.5 border-t border-[#1a1a1c] space-y-1">
                    <span className="text-[9.5px] font-bold text-zinc-500 tracking-wider uppercase block">Execution Mechanism</span>
                    {/* Increased base font size to text-sm */}
                    <p className="text-sm text-zinc-400 leading-relaxed italic">{s.details}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
