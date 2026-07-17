import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Play, Square, RefreshCw, AlertTriangle, ShieldCheck, 
  Activity, Clock, FileText, CheckCircle2, XCircle, ChevronDown, ChevronUp 
} from 'lucide-react';

export default function CanaryPanel({ API }) {
  const [config, setConfig] = useState({ running: 0, interval_minutes: 1, last_run: null, next_run: null });
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [failures, setFailures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [expandedLogId, setExpandedLogId] = useState(null);

  const fetchData = async () => {
    try {
      const [cfgRes, alertsRes, logsRes, failRes] = await Promise.all([
        axios.get(`${API}/api/canary/config`),
        axios.get(`${API}/api/canary/alerts`),
        axios.get(`${API}/api/canary/logs`),
        axios.get(`${API}/api/canary/failure-library`)
      ]);
      if (!cfgRes.data.error) setConfig(cfgRes.data);
      if (!alertsRes.data.error) setAlerts(alertsRes.data);
      if (!logsRes.data.error) setLogs(logsRes.data);
      if (!failRes.data.error) setFailures(failRes.data);
    } catch (e) {
      console.error("Failed to fetch Canary data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000); // Poll every 8 seconds
    return () => clearInterval(interval);
  }, []);

  const handleToggleRunning = async () => {
    const newRunning = config.running === 1 ? 0 : 1;
    try {
      const res = await axios.post(`${API}/api/canary/config`, {
        running: newRunning,
        interval_minutes: config.interval_minutes
      });
      if (!res.data.error) setConfig(res.data.config);
    } catch (e) {
      console.error(e);
    }
  };

  const handleIntervalChange = async (minutes) => {
    try {
      const res = await axios.post(`${API}/api/canary/config`, {
        running: config.running,
        interval_minutes: minutes
      });
      if (!res.data.error) setConfig(res.data.config);
    } catch (e) {
      console.error(e);
    }
  };

  const handleManualTrigger = async () => {
    setTriggering(true);
    try {
      await axios.post(`${API}/api/canary/trigger`);
      fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setTriggering(false);
    }
  };

  const handleFeedback = async (alertId, type) => {
    try {
      await axios.post(`${API}/api/canary/alerts/${alertId}/feedback?feedback=${type}`);
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-8 pt-6 pb-28 md:pb-6 space-y-8 max-w-6xl w-full mx-auto flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-[#1e1e22] pb-6">
        <div>
          <span className="text-[10px] font-bold text-blue-500 uppercase tracking-widest block font-mono">Module 17 — Proactive Sentinel</span>
          <h1 className="text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
            <span>Canary Risk Watchdog</span>
            <span className="px-2 py-0.5 text-[10px] uppercase bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-full font-mono font-bold">
              Background Daemon
            </span>
          </h1>
          <p className="text-xs text-zinc-450 mt-1 max-w-2xl leading-relaxed">
            Canary scans already-ingested CRM ledger details and logistics metrics proactively on a persistent background thread. Uses dynamic z-score multi-signal distance metrics to identify risks before they arise.
          </p>
        </div>

        {/* Master Control Controls */}
        <div className="flex flex-wrap items-center gap-4 bg-[#111213] border border-[#1e1e22] p-3 rounded-xl">
          <div className="flex items-center gap-2 border-r border-[#1e1e22] pr-4">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Status:</span>
            <span className={`flex items-center gap-1.5 text-xs font-bold ${config.running ? 'text-emerald-400' : 'text-zinc-500'}`}>
              <span className={`w-2 h-2 rounded-full ${config.running ? 'bg-emerald-500 animate-ping' : 'bg-zinc-600'}`}></span>
              {config.running ? 'ACTIVE' : 'IDLE'}
            </span>
          </div>

          {/* Toggle Switch */}
          <button 
            onClick={handleToggleRunning}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow ${
              config.running 
                ? 'bg-red-600/10 border border-red-500/30 text-red-400 hover:bg-red-600/20' 
                : 'bg-blue-600 text-white hover:bg-blue-750'
            }`}
          >
            {config.running ? <Square className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {config.running ? 'Deactivate Canary' : 'Activate Canary'}
          </button>

          {/* Interval Selector */}
          <div className="flex items-center gap-1 bg-[#17181a] border border-[#1e1e22] p-1 rounded-lg">
            {[1, 60].map((interval) => (
              <button
                key={interval}
                onClick={() => handleIntervalChange(interval)}
                className={`px-2 py-1 rounded text-[10px] font-bold transition ${
                  config.interval_minutes === interval 
                    ? 'bg-[#1e1e22] text-white' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {interval === 1 ? '1 Min' : '1 Hour'}
              </button>
            ))}
          </div>

          {/* Manual Run */}
          <button 
            onClick={handleManualTrigger}
            disabled={triggering}
            className="p-1.5 rounded-lg bg-[#17181a] border border-[#1e1e22] text-zinc-450 hover:text-zinc-200 transition disabled:opacity-50"
            title="Scan Instantly Now"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${triggering ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Scheduler Status Metadata Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-[#111213] border border-[#1e1e22] p-4 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Last Scan Tick</span>
            <span className="text-xs font-bold text-white block font-mono">
              {config.last_run ? new Date(config.last_run).toLocaleTimeString() : 'Never'}
            </span>
          </div>
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#111213] border border-[#1e1e22] p-4 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Next Scan Tick</span>
            <span className="text-xs font-bold text-white block font-mono">
              {config.next_run ? new Date(config.next_run).toLocaleTimeString() : 'N/A'}
            </span>
          </div>
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Activity className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#111213] border border-[#1e1e22] p-4 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Fired Alerts</span>
            <span className="text-xs font-bold text-white block font-mono">
              {alerts.length} Incidents
            </span>
          </div>
          <div className="p-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertTriangle className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-[#111213] border border-[#1e1e22] p-4 rounded-xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Failure Library</span>
            <span className="text-xs font-bold text-white block font-mono">
              {failures.length} Incident Keys
            </span>
          </div>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Row 2: Live Alert Feed */}
      <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4">
        <div>
          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Proactive Alert Feed</span>
          <span className="text-xs text-zinc-400">Risk profiles detected autonomously by Canary's statistical engine</span>
        </div>

        {alerts.length === 0 ? (
          <div className="border border-dashed border-[#1e1e22] rounded-xl py-12 flex flex-col items-center justify-center text-center">
            <ShieldCheck className="w-10 h-10 text-zinc-650 mb-3" />
            <p className="text-xs text-zinc-400 font-bold">No active anomalies detected</p>
            <p className="text-[10px] text-zinc-500 mt-1 max-w-sm">All metrics are currently performing within normal historical baselines.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`border p-4.5 rounded-xl flex flex-col sm:flex-row sm:items-start justify-between gap-4 transition ${
                  alert.feedback === 'Accurate' 
                    ? 'bg-emerald-950/5 border-emerald-900/30' 
                    : alert.feedback === 'False-Positive'
                    ? 'bg-zinc-950/20 border-[#1e1e22] opacity-60'
                    : 'bg-[#17181a] border-red-900/20 hover:border-red-900/40'
                }`}
              >
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded-md font-mono ${
                      alert.severity === 'High' 
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20' 
                        : alert.severity === 'Medium'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                    }`}>
                      {alert.severity} Severity
                    </span>
                    <span className="text-[9.5px] text-zinc-550 font-mono">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                    <span className="text-[9.5px] uppercase font-mono text-zinc-600 bg-black/35 px-1.5 rounded border border-[#1e1e22]">
                      {alert.mode}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white leading-snug">{alert.headline}</h3>

                  <div className="bg-[#111213] border border-[#1e1e22] p-2.5 rounded-lg">
                    <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-wider block mb-1">Supporting Metrics Evidence</span>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[10px]">
                      {Object.entries(JSON.parse(alert.evidence)).map(([k, v]) => (
                        <div key={k} className="text-zinc-400">
                          <span className="text-zinc-550">{k}:</span> {Number(v).toFixed(1)}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Feedback Controls */}
                <div className="flex items-center gap-2 self-end sm:self-start">
                  {alert.feedback === 'None' ? (
                    <>
                      <button 
                        onClick={() => handleFeedback(alert.id, 'Accurate')}
                        className="px-2.5 py-1 text-[10px] font-bold rounded-lg border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/15 text-emerald-400 transition"
                      >
                        Accurate
                      </button>
                      <button 
                        onClick={() => handleFeedback(alert.id, 'False-Positive')}
                        className="px-2.5 py-1 text-[10px] font-bold rounded-lg border border-zinc-700 bg-zinc-800/10 hover:bg-zinc-800/30 text-zinc-400 transition"
                      >
                        False Alarm
                      </button>
                    </>
                  ) : (
                    <span className={`text-[10px] font-bold font-mono px-2 py-0.5 rounded ${
                      alert.feedback === 'Accurate' ? 'bg-emerald-950 text-emerald-400' : 'bg-zinc-900 text-zinc-500'
                    }`}>
                      Feedback: {alert.feedback}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Row 3: Failure Incidents Library & Scanning Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Failures Library */}
        <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4 lg:col-span-5 flex flex-col">
          <div>
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Failure Incident Signature Keys</span>
            <span className="text-xs text-zinc-400">Incidents mapped to prevent regression profiles</span>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto max-h-[300px]">
            {failures.map((fail) => (
              <div key={fail.id} className="bg-[#17181a] border border-[#1e1e22] p-3 rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-white">{fail.title}</h4>
                  <span className="text-[9px] font-mono text-zinc-550 bg-black/40 px-1.5 py-0.5 rounded border border-[#1e1e22]">
                    Key #{fail.id}
                  </span>
                </div>
                <p className="text-[10.5px] text-zinc-450 leading-relaxed">{fail.description}</p>
                <div className="font-mono text-[9px] text-zinc-500 flex flex-wrap gap-2">
                  <span className="text-zinc-600">Metrics:</span>
                  {fail.implicated_metrics.split(',').map(m => (
                    <span key={m} className="bg-black/30 px-1.5 py-0.2 rounded text-zinc-400 border border-[#1e1e22]">{m}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Scan Log History */}
        <div className="bg-[#111213] border border-[#1e1e22] rounded-xl p-5 space-y-4 lg:col-span-7 flex flex-col">
          <div>
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider block">Scheduler Scanning Audit Log</span>
            <span className="text-xs text-zinc-400">Verifiable logging trace of every execution tick</span>
          </div>

          <div className="flex-1 space-y-2 overflow-y-auto max-h-[300px] font-mono text-[11px]">
            {logs.map((log) => {
              const isExpanded = expandedLogId === log.run_id;
              return (
                <div key={log.run_id} className="border border-[#1e1e22] rounded-lg overflow-hidden bg-[#17181a]">
                  <div 
                    onClick={() => setExpandedLogId(isExpanded ? null : log.run_id)}
                    className="p-2.5 flex items-center justify-between cursor-pointer hover:bg-zinc-800/10 transition"
                  >
                    <div className="flex items-center gap-2">
                      {log.success ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <XCircle className="w-3.5 h-3.5 text-red-500" />
                      )}
                      <span className="text-zinc-400 font-bold text-[10px]">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="text-zinc-550">|</span>
                      <span className="text-zinc-300 text-[10px] truncate max-w-xs">{log.summary}</span>
                    </div>

                    <div className="flex items-center gap-2 text-zinc-500 text-[10px]">
                      <span>{log.duration_ms.toFixed(0)}ms</span>
                      {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="p-3 border-t border-[#1e1e22] bg-[#111213] text-[9.5px] text-zinc-400 whitespace-pre-wrap overflow-x-auto leading-relaxed">
                      {log.details}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
