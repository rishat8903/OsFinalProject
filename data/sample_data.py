"""
Sample datasets for the CPU Scheduling simulator.
Each dataset is represented as a list of dictionaries.
"""

# --- Basic Dataset ---
# 4 processes with simple values, perfect for testing base behavior
BASIC_DATA: list[dict] = [
    {"pid": "P1", "arrival": 0, "burst": 6, "priority": 3},
    {"pid": "P2", "arrival": 1, "burst": 8, "priority": 2},
    {"pid": "P3", "arrival": 2, "burst": 7, "priority": 4},
    {"pid": "P4", "arrival": 3, "burst": 3, "priority": 1},
]

# --- Bursty Dataset ---
# 5 processes with highly unequal burst times (useful for demonstrating SJF's advantage)
BURSTY_DATA: list[dict] = [
    {"pid": "P1", "arrival": 0, "burst": 2, "priority": 2},
    {"pid": "P2", "arrival": 1, "burst": 30, "priority": 1},
    {"pid": "P3", "arrival": 2, "burst": 1, "priority": 3},
    {"pid": "P4", "arrival": 3, "burst": 2, "priority": 4},
    {"pid": "P5", "arrival": 4, "burst": 25, "priority": 5},
]

# --- Priority-Heavy Dataset ---
# 5 processes with varied priorities and arrivals (useful for testing Priority Scheduling)
PRIORITY_DATA: list[dict] = [
    {"pid": "P1", "arrival": 0, "burst": 10, "priority": 5},
    {"pid": "P2", "arrival": 1, "burst": 5, "priority": 1},
    {"pid": "P3", "arrival": 3, "burst": 2, "priority": 2},
    {"pid": "P4", "arrival": 5, "burst": 4, "priority": 3},
    {"pid": "P5", "arrival": 10, "burst": 1, "priority": 4},
]

def get_sample_datasets() -> dict[str, list[dict]]:
    """
    Returns a dictionary of all available sample datasets.

    Returns:
        dict[str, list[dict]]: A dictionary mapping dataset names to process lists.
    """
    return {
        "Basic (4 Processes)": BASIC_DATA,
        "Bursty (5 Processes)": BURSTY_DATA,
        "Priority-Heavy (5 Processes)": PRIORITY_DATA,
    }
