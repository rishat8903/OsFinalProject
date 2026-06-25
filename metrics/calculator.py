"""
Metrics computation and comparative analysis utility for CPU Scheduling algorithms.
"""

import pandas as pd

# --- Metrics Calculations ---

def compute_metrics(results: list[dict]) -> dict:
    """
    Computes overall scheduling performance metrics for a completed simulation run.

    Parameters:
        results (list[dict]): Process dictionaries containing waiting_time,
                             turnaround_time, response_time, and burst values.

    Returns:
        dict: Performance metrics including averages, throughput, and CPU utilization.
    """
    if not results:
        return {
            "avg_waiting_time": 0.0,
            "avg_turnaround_time": 0.0,
            "avg_response_time": 0.0,
            "throughput": 0.0,
            "cpu_utilization": 0.0,
            "per_process": []
        }

    n = len(results)
    
    # Calculate sum of metrics
    total_waiting = sum(float(p["waiting_time"]) for p in results)
    total_turnaround = sum(float(p["turnaround_time"]) for p in results)
    total_response = sum(float(p["response_time"]) for p in results)
    total_burst = sum(float(p["burst"]) for p in results)

    # Find the duration of execution: span = max_completion - min_arrival
    max_completion = max(float(p["completion_time"]) for p in results)
    min_arrival = min(float(p["arrival"]) for p in results)
    total_time_span = max_completion - min_arrival

    # Throughput and CPU Utilization calculations
    if total_time_span > 0:
        throughput = n / total_time_span
        cpu_utilization = (total_burst / total_time_span) * 100.0
    else:
        throughput = 0.0
        cpu_utilization = 0.0

    # Cap CPU utilization at 100% (should theoretically not exceed 100 in valid non-overlapping setups)
    cpu_utilization = min(100.0, cpu_utilization)

    return {
        "avg_waiting_time": round(total_waiting / n, 2),
        "avg_turnaround_time": round(total_turnaround / n, 2),
        "avg_response_time": round(total_response / n, 2),
        "throughput": round(throughput, 4),
        "cpu_utilization": round(cpu_utilization, 2),
        "per_process": results
    }


def compare_all(all_results: dict[str, dict]) -> pd.DataFrame:
    """
    Combines computed metrics for all algorithms into a single pandas DataFrame
    for comparative viewing.

    Parameters:
        all_results (dict[str, dict]): Map from algorithm name (e.g. "FCFS") to its computed metrics dict.

    Returns:
        pd.DataFrame: A comparison table with algorithms as rows and metrics as columns.
    """
    rows = []
    for algo_name, metrics in all_results.items():
        rows.append({
            "Algorithm": algo_name,
            "Avg Waiting Time": metrics["avg_waiting_time"],
            "Avg Turnaround Time": metrics["avg_turnaround_time"],
            "Avg Response Time": metrics["avg_response_time"],
            "Throughput": metrics["throughput"],
            "CPU Utilization (%)": metrics["cpu_utilization"]
        })
    
    df = pd.DataFrame(rows)
    df.set_index("Algorithm", inplace=True)
    return df
