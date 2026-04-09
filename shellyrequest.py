#!/usr/bin/env python3
import requests
import sys
import json
import csv
import os
from datetime import datetime

# Shelly device IPs
shelly1_ip = "10.93.10.240"  # EEE-lab
#shelly1_ip = "192.168.178.58"  # Home

CSV_FILE = "shelly_data.csv"
CSV_HEADERS = ["timestamp", "device_ip", "a_current", "a_voltage", "a_act_power", "a_aprt_power", "a_pf", "a_freq", "b_current", "b_voltage", "b_act_power", "b_aprt_power", "b_pf", "b_freq", "c_current", "c_voltage", "c_act_power", "c_aprt_power", "c_pf", "c_freq"]


def write_to_csv(data: dict, ip: str) -> None:
    """Append Shelly EM status data to CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    
    # Extract key fields from Shelly response
    timestamp = datetime.now().isoformat()
    row = {
        "timestamp": timestamp,
        "device_ip": ip,
        "a_current": data.get("a_current", ""),
        "a_voltage": data.get("a_voltage", ""),
        "a_act_power": data.get("a_act_power", ""),
        "a_aprt_power": data.get("a_aprt_power", ""),
        "a_pf": data.get("a_pf", ""),
        "a_freq": data.get("a_freq", ""),
        "b_current": data.get("b_current", ""),
        "b_voltage": data.get("b_voltage", ""),
        "b_act_power": data.get("b_act_power", ""),
        "b_aprt_power": data.get("b_aprt_power", ""),
        "b_pf": data.get("b_pf", ""),
        "b_freq": data.get("b_freq", ""),
        "c_current": data.get("c_current", ""),
        "c_voltage": data.get("c_voltage", ""),
        "c_act_power": data.get("c_act_power", ""),
        "c_aprt_power": data.get("c_aprt_power", ""),
        "c_pf": data.get("c_pf", ""),
        "c_freq": data.get("c_freq", ""),
    }
    
    with open(CSV_FILE, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    
    print(f"Data written to {CSV_FILE}")


def main():
    try:
        print(f"Fetching data from Shelly device at {shelly1_ip}...")
        shelly1_data = requests.get(
            f"http://{shelly1_ip}/rpc/EM.GetStatus?id=0",
            headers={"Content-Type": "application/json"},
            timeout=5,
        ).json()

        print("Raw data:", json.dumps(shelly1_data, indent=2))
        write_to_csv(shelly1_data, shelly1_ip)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Shelly device: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
