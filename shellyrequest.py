#!/usr/bin/env python3
import requests
import sys
import json
import csv
import os
import time
from datetime import datetime

# Shelly device IPs — 10.93.10.240 to 10.93.10.249
SHELLY_IPS = [f"10.93.10.{240 + i}" for i in range(10)]

CSV_FILE = "shelly_data.csv"
CSV_HEADERS = [
    "timestamp", "device_ip",
    "a_current", "a_voltage", "a_act_power", "a_aprt_power", "a_pf", "a_freq",
    "b_current", "b_voltage", "b_act_power", "b_aprt_power", "b_pf", "b_freq",
    "c_current", "c_voltage", "c_act_power", "c_aprt_power", "c_pf", "c_freq",
    "total_act_power", "total_aprt_power", "energy_kwh",
]

def val(data, key):
    v = data.get(key)
    return "" if v is None else v

def write_to_csv(data: dict, ip: str, interval: int) -> None:
    file_exists = os.path.isfile(CSV_FILE)
    timestamp = datetime.now().isoformat()

    total_act = data.get("total_act_power")
    energy_kwh = round(total_act * interval / 3_600_000, 6) if total_act is not None else ""

    row = {
        "timestamp": timestamp,
        "device_ip": ip,
        "a_current": val(data, "a_current"),
        "a_voltage": val(data, "a_voltage"),
        "a_act_power": val(data, "a_act_power"),
        "a_aprt_power": val(data, "a_aprt_power"),
        "a_pf": val(data, "a_pf"),
        "a_freq": val(data, "a_freq"),
        "b_current": val(data, "b_current"),
        "b_voltage": val(data, "b_voltage"),
        "b_act_power": val(data, "b_act_power"),
        "b_aprt_power": val(data, "b_aprt_power"),
        "b_pf": val(data, "b_pf"),
        "b_freq": val(data, "b_freq"),
        "c_current": val(data, "c_current"),
        "c_voltage": val(data, "c_voltage"),
        "c_act_power": val(data, "c_act_power"),
        "c_aprt_power": val(data, "c_aprt_power"),
        "c_pf": val(data, "c_pf"),
        "c_freq": val(data, "c_freq"),
        "total_act_power": val(data, "total_act_power"),
        "total_aprt_power": val(data, "total_aprt_power"),
        "energy_kwh": energy_kwh,
    }

    with open(CSV_FILE, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"  Data written to {CSV_FILE}")

def main(interval: int):
    for ip in SHELLY_IPS:
        try:
            print(f"Fetching data from {ip}...")
            data = requests.get(
                f"http://{ip}/rpc/EM.GetStatus?id=0",
                timeout=5,
            ).json()
            print(f"  Raw data: {json.dumps(data, indent=2)}")
            write_to_csv(data, ip, interval)
        except requests.exceptions.RequestException as e:
            print(f"  Skipping {ip} — network error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Skipping {ip} — unexpected error: {e}", file=sys.stderr)

if __name__ == "__main__":
    interval = int(input("Enter interval in seconds between each run (e.g. 300 for 5 min): "))
    loops = int(input("Enter number of times to run (0 = run forever): "))

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
