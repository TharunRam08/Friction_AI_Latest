# backend/modules/canary_engine.py
import time
import json
import threading
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import traceback
import os
from groq import Groq

from data.canary_db import (
    get_canary_config, update_canary_config, log_canary_run,
    get_failure_library, add_canary_alert, get_checkpoint, update_checkpoint, get_conn
)

# Initialize Groq client
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class CanaryEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(CanaryEngine, cls).__new__(cls, *args, **kwargs)
                cls._instance._init_engine()
            return cls._instance

    def _init_engine(self):
        self.thread = None
        self.stop_event = threading.Event()
        self.running = False

    def start(self):
        with self._lock:
            if self.running:
                return
            self.stop_event.clear()
            self.running = True
            self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.thread.start()

    def stop(self):
        with self._lock:
            if not self.running:
                return
            self.stop_event.set()
            self.running = False
            if self.thread:
                self.thread.join(timeout=2.0)
                self.thread = None

    def _scheduler_loop(self):
        while not self.stop_event.is_set():
            config = get_canary_config()
            if not config or not config.get("running"):
                # Canary is toggled OFF
                time.sleep(2)
                continue

            # Check if it is time to run
            now = datetime.now()
            next_run_str = config.get("next_run")
            
            should_run = False
            if not next_run_str:
                should_run = True
            else:
                try:
                    next_run_time = datetime.fromisoformat(next_run_str)
                    if now >= next_run_time:
                        should_run = True
                except:
                    should_run = True

            if should_run:
                # Update next run immediately to prevent double execution
                interval = config.get("interval_minutes", 1)
                next_run = now + timedelta(minutes=interval)
                update_canary_config(
                    running=1,
                    interval_minutes=interval,
                    last_run=now.isoformat(),
                    next_run=next_run.isoformat()
                )
                
                # Execute scan
                start_time = time.time()
                try:
                    summary, details = self.run_scan()
                    duration = (time.time() - start_time) * 1000.0
                    log_canary_run(now.isoformat(), duration, 1, summary, details)
                except Exception as e:
                    duration = (time.time() - start_time) * 1000.0
                    err_msg = traceback.format_exc()
                    log_canary_run(now.isoformat(), duration, 0, f"Error: {str(e)}", err_msg)

            # Sleep short duration to stay responsive to ON/OFF toggles
            time.sleep(2)

    def run_scan(self):
        """Runs incremental data scanning, computes statistical similarity/drift, and fires alerts."""
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "../data/crm.db"))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Incremental Scanning: pull support tickets opened since last scan
        last_tkt_scan = get_checkpoint("support_tickets")
        cursor.execute("SELECT opened_date, COUNT(*) as c FROM support_tickets WHERE opened_date > ? GROUP BY opened_date", (last_tkt_scan,))
        new_tickets = cursor.fetchall()
        
        # Incremental Scanning: pull deals closed since last scan
        last_deal_scan = get_checkpoint("deals")
        cursor.execute("SELECT close_date, value FROM deals WHERE stage='Closed-Won' AND close_date > ?", (last_deal_scan,))
        new_deals = cursor.fetchall()

        # Get latest timestamps to update checkpoints
        cursor.execute("SELECT MAX(opened_date) FROM support_tickets")
        max_tkt_date = cursor.fetchone()[0] or last_tkt_scan
        cursor.execute("SELECT MAX(close_date) FROM deals")
        max_deal_date = cursor.fetchone()[0] or last_deal_scan
        
        update_checkpoint("support_tickets", max_tkt_date)
        update_checkpoint("deals", max_deal_date)

        # Build registry metrics from real DB tables
        cursor.execute("SELECT MIN(qty_on_hand) FROM inventory WHERE product_name LIKE '%Edge Gateway%'")
        qty_val = cursor.fetchone()[0]
        qty_on_hand = float(qty_val) if qty_val is not None else 45.0

        cursor.execute("SELECT MIN(reorder_point) FROM inventory WHERE product_name LIKE '%Edge Gateway%'")
        reorder_val = cursor.fetchone()[0]
        reorder_point = float(reorder_val) if reorder_val is not None else 20.0

        # Calculate average ticket count daily from past 30 days
        cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE opened_date >= date('now', '-30 days')")
        total_recent_tickets = float(cursor.fetchone()[0] or 0.0)
        recent_daily_avg_tickets = total_recent_tickets / 30.0

        conn.close()

        # ── STATISTICAL COMPUTATION (THE ACTUAL MATH) ──────────────────────────
        # Metrics registry values
        current_metrics = {
            "qty_on_hand": qty_on_hand,
            "reorder_point": reorder_point,
            "tickets": recent_daily_avg_tickets
        }

        # 1. Baseline statistics (normal historical range)
        baselines = {
            "qty_on_hand": {"mean": 45.0, "std": 5.0},
            "reorder_point": {"mean": 20.0, "std": 1.0},
            "tickets": {"mean": 1.5, "std": 0.8}
        }

        # 2. Multi-Signal Aggregate Z-score (Mahalanobis distance approximation)
        # S = sqrt( sum( (val - mean)/std )^2 )
        # High score if inventory drops (negative z) and support tickets rise (positive z)
        z_scores = {}
        for m, val in current_metrics.items():
            b = baselines[m]
            z_scores[m] = (val - b["mean"]) / b["std"]

        # Aggregate score: give higher weights to inventory depletion combined with ticket volume spikes
        # E.g., inventory z is negative when stock drops, tickets z is positive when support volume rises
        weighted_z_sum = ((-z_scores["qty_on_hand"]) ** 2) + (z_scores["tickets"] ** 2)
        aggregate_score = np.sqrt(weighted_z_sum)

        # 3. Dynamic Time Warping (DTW) / Cosine similarity with Failure Library
        library = get_failure_library()
        highest_similarity = 0.0
        matched_failure = None

        for entry in library:
            try:
                pattern = json.loads(entry["historical_pattern"])
                # Compute Cosine Similarity between current metrics vector and failure pattern vector
                common_metrics = [m for m in ["qty_on_hand", "reorder_point", "tickets"] if m in pattern]
                if not common_metrics:
                    continue
                v_curr = np.array([current_metrics[m] for m in common_metrics], dtype=np.float32)
                v_pat = np.array([pattern[m] for m in common_metrics], dtype=np.float32)
                
                # Normalize
                v_curr_norm = v_curr / (np.linalg.norm(v_curr) + 1e-9)
                v_pat_norm = v_pat / (np.linalg.norm(v_pat) + 1e-9)
                
                sim = float(np.dot(v_curr_norm, v_pat_norm))
                if sim > highest_similarity:
                    highest_similarity = sim
                    matched_failure = entry
            except:
                pass

        # ── VERDICT GENERATION ────────────────────────────────────────────────
        # If aggregate score crosses threshold (e.g. 2.0) or similarity crosses threshold (e.g. 0.85)
        # We fire an alert!
        alert_threshold = 2.0
        similarity_threshold = 0.85

        fired = False
        mode = "anomaly-based"
        severity = "Low"
        
        if matched_failure and highest_similarity >= similarity_threshold:
            fired = True
            mode = "failure-pattern-based"
            severity = "High" if aggregate_score > 3.0 else "Medium"
        elif aggregate_score >= alert_threshold:
            fired = True
            mode = "anomaly-based"
            severity = "High" if aggregate_score > 3.5 else "Medium" if aggregate_score > 2.2 else "Low"

        summary = f"Scan completed. Agg score: {aggregate_score:.2f}, max similarity: {highest_similarity:.2f}."
        details_dict = {
            "metrics": current_metrics,
            "z_scores": z_scores,
            "aggregate_score": float(aggregate_score),
            "highest_similarity": float(highest_similarity),
            "matched_failure_title": matched_failure["title"] if matched_failure else None,
            "new_tickets_pulled": len(new_tickets),
            "new_deals_pulled": len(new_deals)
        }

        if fired:
            # Generate risk statement using Groq or fallback plain text
            headline = f"Canary detected potential risk pattern of {severity} severity."
            solution = "Please verify your safety stock thresholds and allocate support bandwidth."
            evidence = json.dumps(current_metrics)
            
            if groq_client:
                try:
                    prompt = (
                        f"You are the Canary proactive risk watchdog module in Friction AI. "
                        f"A statistical scan flagged a potential business threat.\n"
                        f"Current metrics: {current_metrics}\n"
                        f"Baselines: {baselines}\n"
                        f"Aggregate Z-score: {aggregate_score:.2f}\n"
                        f"Detected Mode: {mode}\n"
                        f"Construct a clear explanation of the problem AND a detailed, simple, understandable solution.\n"
                        f"Return ONLY a valid JSON object with the keys 'problem' and 'solution'.\n"
                        f"The 'problem' must be one single, clear, simple, and friendly sentence explaining the risk in plain English.\n"
                        f"The 'solution' must be a detailed, step-by-step, simple set of practical actions (2-3 sentences) explaining exactly what the business owner should do to fix the problem (e.g. order stock, allocate support staff, adjust thresholds)."
                    )
                    primary_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
                    models = [primary_model, "openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
                    chat_completion = None
                    last_err = None
                    for m in models:
                        try:
                            chat_completion = groq_client.chat.completions.create(
                                messages=[
                                    {
                                        "role": "user",
                                        "content": prompt,
                                    }
                                ],
                                model=m,
                                response_format={"type": "json_object"},
                                temperature=0.3,
                            )
                            break
                        except Exception as ex:
                            last_err = ex
                            continue
                    if chat_completion is None:
                        raise last_err if last_err is not None else Exception("All models failed")
                    clean_res = json.loads(chat_completion.choices[0].message.content.strip())
                    headline = clean_res.get("problem", f"Potential profit decline linked to safety stock depletion ({qty_on_hand:.0f} units) and rising support load ({recent_daily_avg_tickets:.1f} tickets/day).")
                    solution = clean_res.get("solution", "Verify safety stock thresholds and allocate support bandwidth.")
                except Exception as e:
                    headline = f"Alert: Low stock alert ({qty_on_hand:.0f} units left) paired with high customer ticket volumes ({recent_daily_avg_tickets:.1f} per day)."
                    solution = "Purchase Edge Gateway devices immediately and delegate extra developers to clear support backlog."
            else:
                headline = f"Alert: Low stock alert ({qty_on_hand:.0f} units left) paired with high customer ticket volumes ({recent_daily_avg_tickets:.1f} per day)."
                solution = "Purchase Edge Gateway devices immediately and delegate extra developers to clear support backlog."
 
            # Add to alerts table
            add_canary_alert(headline, solution, evidence, severity, mode, datetime.now().isoformat())
            summary += " ALERT FIRED!"

        return summary, json.dumps(details_dict, indent=2)
