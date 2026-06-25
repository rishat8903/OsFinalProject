"""
First-Come, First-Served (FCFS) CPU Scheduling Algorithm.
"""

from utils.helpers import fill_derived_metrics

# --- FCFS Scheduling Implementation ---

def schedule_fcfs(processes: list[dict]) -> tuple[list[dict], list[tuple]]:
    """
    Simulates the First-Come, First-Served (FCFS) scheduling algorithm.
    This is a non-preemptive algorithm that executes processes in the order of their arrival.

    Parameters:
        processes (list[dict]): A list of process dictionaries, where each dict has:
            - "pid": str (Process Identifier)
            - "arrival": float/int (Arrival Time)
            - "burst": float/int (Burst Time)
            - "priority": int (Priority)

    Returns:
        tuple[list[dict], list[tuple]]:
            - list[dict]: Process dictionaries updated with all scheduling metrics.
            - list[tuple]: Timeline of execution as list of (pid, start_time, end_time) tuples.
    """
    # Sort processes primarily by arrival time. Keep original order/PID as secondary sort to be stable.
    sorted_procs = sorted(processes, key=lambda x: (float(x["arrival"]), str(x["pid"])))
    
    results = []
    timeline = []
    current_time = 0.0

    for proc in sorted_procs:
        pid = proc["pid"]
        arrival = float(proc["arrival"])
        burst = float(proc["burst"])
        
        # If CPU is idle waiting for the next process to arrive
        if current_time < arrival:
            current_time = arrival
        
        start_time = current_time
        completion_time = start_time + burst
        
        # Record execution timeline block
        timeline.append((pid, start_time, completion_time))
        
        # Build raw results for metrics derivation
        proc_result = proc.copy()
        proc_result["start_time"] = start_time
        proc_result["completion_time"] = completion_time
        results.append(proc_result)
        
        # Advance time
        current_time = completion_time

    # Fill derived metrics: waiting_time, turnaround_time, response_time
    final_results = fill_derived_metrics(results)
    
    return final_results, timeline
