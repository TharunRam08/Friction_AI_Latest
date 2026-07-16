# backend/modules/m10_canary.py
"""
Canary Anomaly Engine Math Module.
Calculates statistical Z-score drift for key business metrics and compares
them against historical failure patterns in the database using Cosine Similarity.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_drift(current_7d: list, baseline_30d: list) -> tuple:
    """
    Computes statistical Z-score drift and raw percentage drift.
    Formula: (current_7d_avg - baseline_30d_avg) / (baseline_30d_std + 1e-9)
    """
    b_arr = np.array(baseline_30d)
    c_arr = np.array(current_7d)
    
    baseline_avg = float(np.mean(b_arr))
    baseline_std = float(np.std(b_arr))
    current_avg = float(np.mean(c_arr))
    
    # Z-score drift calculation
    drift = (current_avg - baseline_avg) / (baseline_std + 1e-9)
    
    # Raw drift percentage
    drift_pct = ((current_avg - baseline_avg) / (baseline_avg + 1e-9)) * 100
    
    return drift, drift_pct

def run_canary_analysis(drift_vector: list, patterns: list) -> dict:
    """
    Computes cosine similarity of drift vector vs database failure signatures.
    drift_vector: [rev_drift, exp_drift, tkt_drift, inv_drift]
    patterns: list of tuples/dicts [(pattern_name, [rev, exp, tkt, inv])]
    """
    drift_arr = np.array(drift_vector).reshape(1, -1)
    
    all_scores = {}
    best_pattern = "None"
    best_score = -1.0
    
    for pattern_name, pattern_vec in patterns:
        pat_arr = np.array(pattern_vec).reshape(1, -1)
        # Cosine similarity calculation using sklearn
        sim = float(cosine_similarity(drift_arr, pat_arr)[0][0])
        
        # Clip score between -1 and 1, represent as percentage -100% to 100%
        sim_pct = round(sim * 100, 2)
        all_scores[pattern_name] = sim_pct
        
        if sim > best_score:
            best_score = sim
            best_pattern = pattern_name
            
    # Alert is triggered if similarity >= 85%
    alert = best_score >= 0.85
    
    return {
        "alert": alert,
        "matched_pattern": best_pattern if alert else (best_pattern if best_score > 0 else "None"),
        "similarity": round(max(0.0, best_score) * 100, 2),
        "all_scores": all_scores
    }
