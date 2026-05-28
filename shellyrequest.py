#!/usr/bin/env python3
"""
Shelly Energy Monitor
---------------------
Polls Shelly 3-phase energy meter devices over HTTP,
calculates energy consumed per phase and in total,
and saves the results to a CSV file.
"""

import requests
import sys
import json
import csv
import os
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# IP addresses of the 10 Shelly devices on the network (10.93.10.240 to .249)
SHELLY_IPS = [f"10.93.10.{240 + i}" for i in range(10)]

# Output CSV file where all readings are stored
CSV_FILE = "shelly_data.csv"

# Column names for the CSV file — one row is written per device per run
CSV_HEADERS = [
    "timestamp",            # Date and time of the reading
    "device_ip",            # IP address of the Shelly device

    # Phase A measurements
    "a_current",            # Current on phase A (Amperes)
    "a_voltage",            # Voltage on phase A (Volts)
    "a_act_power",          # Active (real) power on phase A (Watts)
    "a_aprt_power",         # Apparent power on phase A (VA)
    "a_pf",                 # Power factor on phase A (0 to 1)
    "a_freq",               # Frequency on phase A (Hz)
    "a_energy_ws",          # Energy consumed on phase A this interval (Watt-seconds)

    # Phase B measurements
    "b_current",
    "b_voltage",
    "b_act_power",
    "b_aprt_power",
    "b_pf",
    "b_freq",
    "b_energy_ws",          # Energy consumed on phase B this interval (Watt-seconds)

    # Phase C measurements
    "c_current",
    "c_voltage",
    "c_act_power",
    "c_aprt_power",
    "c_pf",
    "c_freq",
    "c_energy_ws",          # Energy consumed on phase C this interval (Watt-seconds)

    # Totals across all 3 phases
    "total_act_power",      # Total active power across all phases (Watts)
    "total_aprt_power",     # Total apparent power across all phases (VA)
    "total_energy_ws",      # Total energy consumed across all phases this interval (Watt-seconds)
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def val(data: dict, key: str):
    """
    Safely read a value from the device response dictionary.
    Returns an empty string if the key does not exist,
    so the CSV cell is left blank instead of crashing.
    """
    v = data.get(key)
    return "" if v is None else v


def fetch_data(ip: str) -> dict:
    """
    Send an HTTP request to the Shelly device and return its response as a dictionary.
    The endpoint EM.GetStatus returns all current electrical measurements.
    Raises requests.exceptions.RequestException if the device is unreachable.
    """
    response = requests.get(
        f"http://{ip}/rpc/EM.GetStatus?id=0",
        timeout=5,
    )
    return response.json()


def build_row(data: dict, ip: str, interval: int) -> dict:
    """
    Transform raw device data into a flat dictionary ready to be saved.

    Energy is calculated as:
        energy (Watt-seconds) = active_power (Watts) x interval (seconds)

    This assumes power stayed roughly constant during the interval,
    which is a standard approximation for periodic sampling.

    Parameters:
        data     — raw JSON response from the Shelly device
        ip       — IP address of the device (stored for reference)
        interval — seconds between readings (used to calculate energy)

    Returns:
        A dictionary with one value per CSV column.
    """
    timestamp = datetime.now().isoformat()

    def energy(key: str):
        """Calculate energy in Watt-seconds for the given power key."""
        power = data.get(key)
        return round(power * interval, 3) if power is not None else ""

    return {
        "timestamp":        timestamp,
        "device_ip":        ip,

        # Phase A
        "a_current":        val(data, "a_current"),
        "a_voltage":        val(data, "a_voltage"),
        "a_act_power":      val(data, "a_act_power"),
        "a_aprt_power":     val(data, "a_aprt_power"),
        "a_pf":             val(data, "a_pf"),
        "a_freq":           val(data, "a_freq"),
        "a_energy_ws":      energy("a_act_power"),

        # Phase B
        "b_current":        val(data, "b_current"),
        "b_voltage":        val(data, "b_voltage"),
        "b_act_power":      val(data, "b_act_power"),
        "b_aprt_power":     val(data, "b_aprt_power"),
        "b_pf":             val(data, "b_pf"),
        "b_freq":           val(data, "b_freq"),
        "b_energy_ws":      energy("b_act_power"),

        # Phase C
        "c_current":        val(data, "c_current"),
        "c_voltage":        val(data, "c_voltage"),
        "c_act_power":      val(data, "c_act_power"),
        "c_aprt_power":     val(data, "c_aprt_power"),
        "c_pf":             val(data, "c_pf"),
        "c_freq":           val(data, "c_freq"),
        "c_energy_ws":      energy("c_act_power"),

        # Totals
        "total_act_power":  val(data, "total_act_power"),
        "total_aprt_power": val(data, "total_aprt_power"),
        "total_energy_ws":  energy("total_act_power"),
    }


def write_to_csv(row: dict) -> None:
    """
    Append a single row of measurements to the CSV file.
    If the file does not exist yet, the header row is written first.

    Note: to connect a database instead, replace this function with
    a write_to_db(row) function that inserts the same dictionary.
    """
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    print(f"  Data written to {CSV_FILE}")

# ---------------------------------------------------------------------------
# Main polling logic
# ---------------------------------------------------------------------------

def main(interval: int) -> None:
    """
    Poll all Shelly devices once.
    For each device: fetch data → build row → save to CSV.
    Devices that are unreachable are skipped with a warning.
    """
    for ip in SHELLY_IPS:
        try:
            print(f"Fetching data from {ip}...")
            data = fetch_data(ip)
            print(f"  Raw data: {json.dumps(data, indent=2)}")
            row = build_row(data, ip, interval)
            write_to_csv(row)
        except requests.exceptions.RequestException as e:
            print(f"  Skipping {ip} — network error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Skipping {ip} — unexpected error: {e}", file=sys.stderr)


if __name__ == "__main__":
    interval = int(input("Enter interval in seconds between each run (e.g. 300 for 5 min): "))
    loops    = int(input("Enter number of times to run (0 = run forever): "))

    count = 0
    while True:
        count += 1
        print(f"\n--- Run {count} ---")
        main(interval)
        if loops != 0 and count >= loops:
            print("Done.")
            break
        print(f"Waiting {interval} seconds...\n")
        time.sleep(interval)
