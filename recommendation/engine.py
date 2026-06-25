"""
Rule-based recommendation engine for CPU scheduling scenarios.
Determines the best scheduling algorithm based on simulation metrics and operational goals.
"""

# Tie-breaker preference order: SJF > Round Robin > Priority > FCFS
TIE_BREAKER_PREFERENCE = ["SJF", "Round Robin", "Priority", "FCFS"]


def _resolve_ties(candidates: list[str]) -> str:
    """
    Selects the best algorithm from a list of candidates using the tie-breaker preference:
    SJF > Round Robin > Priority > FCFS.

    Parameters:
        candidates (list[str]): List of algorithm names that are tied.

    Returns:
        str: The selected algorithm name based on preference order.
    """
    for algo in TIE_BREAKER_PREFERENCE:
        if algo in candidates:
            return algo
    return candidates[0] if candidates else "FCFS"


def get_recommendations(all_metrics: dict[str, dict]) -> dict[str, dict]:
    """
    Analyzes simulation metrics to recommend the best algorithm for 8 different OS scenarios.

    Parameters:
        all_metrics (dict[str, dict]): Map from algorithm name ("FCFS", "SJF", etc.)
                                       to its calculated metrics dictionary.

    Returns:
        dict[str, dict]: Map of scenario names to a dictionary containing:
                         - "algorithm": str (the recommended algorithm)
                         - "reason": str (a brief explanation)
    """
    recommendations = {}

    # --- Scenario 1: Minimum Waiting Time ---
    # Lowest avg_waiting_time
    min_wt = min(m["avg_waiting_time"] for m in all_metrics.values())
    wt_candidates = [name for name, m in all_metrics.items() if m["avg_waiting_time"] == min_wt]
    best_wt_algo = _resolve_ties(wt_candidates)
    recommendations["Minimum Waiting Time"] = {
        "algorithm": best_wt_algo,
        "reason": f"Achieves the lowest average waiting time of {min_wt} time units."
    }

    # --- Scenario 2: Maximum Throughput ---
    # Highest throughput
    max_tp = max(m["throughput"] for m in all_metrics.values())
    tp_candidates = [name for name, m in all_metrics.items() if m["throughput"] == max_tp]
    best_tp_algo = _resolve_ties(tp_candidates)
    recommendations["Maximum Throughput"] = {
        "algorithm": best_tp_algo,
        "reason": f"Achieves the highest throughput of {max_tp} processes per time unit."
    }

    # --- Scenario 3: Best Completion Time ---
    # Lowest avg_turnaround_time
    min_tat = min(m["avg_turnaround_time"] for m in all_metrics.values())
    tat_candidates = [name for name, m in all_metrics.items() if m["avg_turnaround_time"] == min_tat]
    best_tat_algo = _resolve_ties(tat_candidates)
    recommendations["Best Completion Time"] = {
        "algorithm": best_tat_algo,
        "reason": f"Achieves the lowest average turnaround (completion) time of {min_tat} time units."
    }

    # --- Scenario 4: Fairness ---
    # Round Robin (always)
    recommendations["Fairness"] = {
        "algorithm": "Round Robin",
        "reason": "Round Robin uses preemption and equal time slices (quantums) to guarantee that no process starves."
    }

    # --- Scenario 5: Interactive Systems ---
    # Round Robin (always)
    recommendations["Interactive Systems"] = {
        "algorithm": "Round Robin",
        "reason": "Preemptive time slicing provides fast initial response times, crucial for user-facing systems."
    }

    # --- Scenario 6: Embedded / Real-Time ---
    # Priority Scheduling (always)
    recommendations["Embedded / Real-Time"] = {
        "algorithm": "Priority",
        "reason": "Embedded systems require deadline-driven execution, which is best handled by prioritizing critical tasks."
    }

    # --- Scenario 7: High Priority Tasks ---
    # Priority Scheduling (always)
    recommendations["High Priority Tasks"] = {
        "algorithm": "Priority",
        "reason": "Explicitly runs processes based on their designated importance/urgency value first."
    }

    # --- Scenario 8: Simplicity / Ease of Implementation ---
    # FCFS (always)
    recommendations["Simplicity"] = {
        "algorithm": "FCFS",
        "reason": "First-Come First-Served requires no complex queues, sorting, or preemption, making it simple to implement."
    }

    return recommendations
