"""
Round Robin (RR) Preemptive CPU Scheduling Algorithm.
"""

from utils.helpers import fill_derived_metrics

# --- Round Robin Scheduling Implementation ---

def schedule_round_robin(
    processes: list[dict], 
    time_quantum: int = 2
) -> tuple[list[dict], list[tuple]]:
    """
    Simulates the Round Robin (RR) preemptive CPU scheduling algorithm.
    Processes are run for a maximum of `time_quantum` units before being preempted.
    Ties in arrivals are resolved by PID.

    Parameters:
        processes (list[dict]): A list of process dictionaries.
        time_quantum (int): The CPU time slice allocated to each process.

    Returns:
        tuple[list[dict], list[tuple]]:
            - list[dict]: Process dictionaries updated with all scheduling metrics.
            - list[tuple]: Timeline of execution as list of (pid, start_time, end_time) tuples.
    """
    # Create copies of process dictionaries and sort by arrival then PID
    unstarted = sorted(
        [proc.copy() for proc in processes],
        key=lambda x: (float(x["arrival"]), str(x["pid"]))
    )
    
    remaining_burst = {p["pid"]: float(p["burst"]) for p in unstarted}
    first_start_time = {p["pid"]: None for p in unstarted}
    
    ready_queue = []
    results = []
    timeline = []
    current_time = 0.0

    # Pop initial processes at or before start time
    if unstarted:
        min_arrival = float(unstarted[0]["arrival"])
        if current_time < min_arrival:
            current_time = min_arrival
        
        # Pull all processes that have arrived up to current_time
        arrived = [p for p in unstarted if float(p["arrival"]) <= current_time]
        for p in arrived:
            ready_queue.append(p)
            unstarted.remove(p)

    while ready_queue or unstarted:
        if not ready_queue:
            # Advance current time to the next process arrival
            next_arrival = float(unstarted[0]["arrival"])
            current_time = next_arrival
            
            # Move arrived processes to the ready queue
            arrived = [p for p in unstarted if float(p["arrival"]) <= current_time]
            for p in arrived:
                ready_queue.append(p)
                unstarted.remove(p)

        # Get process at the head of the queue
        proc = ready_queue.pop(0)
        pid = proc["pid"]
        
        # Record response time (first time CPU is acquired)
        if first_start_time[pid] is None:
            first_start_time[pid] = current_time

        # Calculate time slice for execution
        exec_time = min(float(time_quantum), remaining_burst[pid])
        start_slice = current_time
        end_slice = current_time + exec_time
        
        # Record this slice in timeline
        timeline.append((pid, start_slice, end_slice))
        
        # Advance clock and update remaining burst
        current_time = end_slice
        remaining_burst[pid] -= exec_time

        # Move new arrivals to queue before re-queueing current process
        new_arrivals = [p for p in unstarted if float(p["arrival"]) <= current_time]
        for p in new_arrivals:
            ready_queue.append(p)
            unstarted.remove(p)

        # If current process is not yet finished, re-queue it
        if remaining_burst[pid] > 0:
            ready_queue.append(proc)
        else:
            # Process complete; construct its output result dict
            completed_proc = proc.copy()
            completed_proc["start_time"] = first_start_time[pid]
            completed_proc["completion_time"] = current_time
            results.append(completed_proc)

    # Calculate final derived metrics
    final_results = fill_derived_metrics(results)
    
    # Sort results by arrival time and PID for presentation
    final_results = sorted(final_results, key=lambda x: (float(x["arrival"]), str(x["pid"])))

    return final_results, timeline
