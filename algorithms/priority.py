"""
Priority Scheduling Non-Preemptive CPU Scheduling Algorithm.
"""

from utils.helpers import fill_derived_metrics

# --- Priority Scheduling Implementation ---

def schedule_priority(
    processes: list[dict], 
    lower_is_higher: bool = True
) -> tuple[list[dict], list[tuple]]:
    """
    Simulates the non-preemptive Priority scheduling algorithm.
    At each decision point, among all arrived processes, it selects the one with the highest priority.
    
    Parameters:
        processes (list[dict]): A list of process dictionaries.
        lower_is_higher (bool): If True, lower numerical priority value represents higher priority.
                               If False, higher numerical value represents higher priority.

    Returns:
        tuple[list[dict], list[tuple]]:
            - list[dict]: Process dictionaries updated with all scheduling metrics.
            - list[tuple]: Timeline of execution as list of (pid, start_time, end_time) tuples.
    """
    unexecuted = [proc.copy() for proc in processes]
    results = []
    timeline = []
    current_time = 0.0

    while unexecuted:
        # Filter processes that have arrived at or before the current time
        arrived = [p for p in unexecuted if float(p["arrival"]) <= current_time]
        
        # If no processes have arrived, advance time to the next earliest arrival
        if not arrived:
            next_arrival = min(float(p["arrival"]) for p in unexecuted)
            current_time = next_arrival
            # Refilter
            arrived = [p for p in unexecuted if float(p["arrival"]) <= current_time]

        # Select process based on priority configuration.
        # Ties are broken by arrival time, and then by PID.
        selected_proc = min(
            arrived,
            key=lambda x: (
                float(x["priority"]) if lower_is_higher else -float(x["priority"]),
                float(x["arrival"]),
                str(x["pid"])
            )
        )
        
        pid = selected_proc["pid"]
        arrival = float(selected_proc["arrival"])
        burst = float(selected_proc["burst"])
        
        start_time = current_time
        completion_time = start_time + burst
        
        # Record execution timeline block
        timeline.append((pid, start_time, completion_time))
        
        # Record results
        selected_proc["start_time"] = start_time
        selected_proc["completion_time"] = completion_time
        results.append(selected_proc)
        
        # Remove from unexecuted queue
        unexecuted.remove(selected_proc)
        
        # Advance time
        current_time = completion_time

    # Fill derived metrics (waiting_time, turnaround_time, response_time)
    final_results = fill_derived_metrics(results)
    
    # Sort final results by arrival/PID for clean output presentation
    final_results = sorted(final_results, key=lambda x: (float(x["arrival"]), str(x["pid"])))

    return final_results, timeline
