"""
Helper utilities for process validation and scheduling metric calculations.
"""

def validate_process_data(processes: list[dict]) -> tuple[bool, str]:
    """
    Validates the input process data list.

    Requirements:
    1. Burst time and arrival time must be >= 0.
    2. Priority must be >= 1.
    3. PIDs must be unique and non-empty.

    Parameters:
        processes (list[dict]): List of process dictionaries.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not processes:
        return False, "No processes provided."

    seen_pids = set()

    for idx, proc in enumerate(processes):
        pid = proc.get("pid")
        arrival = proc.get("arrival")
        burst = proc.get("burst")
        priority = proc.get("priority")

        # Check PID existence and uniqueness
        if pid is None or str(pid).strip() == "":
            return False, f"Row {idx + 1}: PID cannot be empty."
        
        pid_str = str(pid).strip()
        if pid_str in seen_pids:
            return False, f"Duplicate PID found: '{pid_str}'."
        seen_pids.add(pid_str)

        # Validate Arrival Time
        try:
            arrival_val = float(arrival)
            if arrival_val < 0:
                return False, f"Process '{pid_str}': Arrival Time must be non-negative (>= 0)."
        except (ValueError, TypeError):
            return False, f"Process '{pid_str}': Arrival Time must be a valid number."

        # Validate Burst Time
        try:
            burst_val = float(burst)
            if burst_val < 0:
                return False, f"Process '{pid_str}': Burst Time must be non-negative (>= 0)."
            if burst_val == 0:
                return False, f"Process '{pid_str}': Burst Time must be greater than 0 to execute."
        except (ValueError, TypeError):
            return False, f"Process '{pid_str}': Burst Time must be a valid number."

        # Validate Priority
        try:
            priority_val = int(priority)
            if priority_val < 1:
                return False, f"Process '{pid_str}': Priority must be an integer >= 1."
        except (ValueError, TypeError):
            return False, f"Process '{pid_str}': Priority must be a valid integer."

    return True, ""


def fill_derived_metrics(results: list[dict]) -> list[dict]:
    """
    Calculates derived metrics for all scheduled processes, including:
    - turnaround_time (Completion Time - Arrival Time)
    - waiting_time (Turnaround Time - Burst Time)
    - response_time (First Start Time - Arrival Time)

    Parameters:
        results (list[dict]): Process dictionaries with start_time and completion_time.

    Returns:
        list[dict]: List of process dictionaries updated with calculated metric values.
    """
    updated_results = []
    for proc in results:
        updated = proc.copy()
        
        arrival = float(proc["arrival"])
        burst = float(proc["burst"])
        start = float(proc["start_time"])
        completion = float(proc["completion_time"])

        turnaround = completion - arrival
        waiting = turnaround - burst
        response = start - arrival

        # Standard safety check (precision errors)
        updated["turnaround_time"] = round(max(0.0, turnaround), 2)
        updated["waiting_time"] = round(max(0.0, waiting), 2)
        updated["response_time"] = round(max(0.0, response), 2)
        
        updated_results.append(updated)

    return updated_results
