import requests
import sys
import csv
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base IP — last octet is the device number (0–9)
BASE_IP = "10.93.10.24"
DEVICE_IDS = list(range(10))   # 0 → 10.93.10.240, …, 9 → 10.93.10.249

CSV_FILE_2 = "shelly_data.csv"
CSV_HEADERS = [
    "timestamp", "sample_index", "device_ip",
    "a_current", "a_voltage", "a_act_power", "a_aprt_power", "a_pf", "a_freq",
    "b_current", "b_voltage", "b_act_power", "b_aprt_power", "b_pf", "b_freq",
    "c_current", "c_voltage", "c_act_power", "c_aprt_power", "c_pf", "c_freq",
]


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def write_rows_to_csv(rows: list[dict]) -> None:
    """Append a batch of rows to the CSV, writing the header only once."""
    file_exists = os.path.isfile(CSV_FILE_2)
    with open(CSV_FILE_2, mode="a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def build_row(data: dict, ip: str, sample_index: int, timestamp: str) -> dict:
    return {
        "timestamp":    timestamp,
        "sample_index": sample_index,
        "device_ip":    ip,
        "a_current":    data.get("a_current",    ""),
        "a_voltage":    data.get("a_voltage",    ""),
        "a_act_power":  data.get("a_act_power",  ""),
        "a_aprt_power": data.get("a_aprt_power", ""),
        "a_pf":         data.get("a_pf",         ""),
        "a_freq":       data.get("a_freq",        ""),
        "b_current":    data.get("b_current",    ""),
        "b_voltage":    data.get("b_voltage",    ""),
        "b_act_power":  data.get("b_act_power",  ""),
        "b_aprt_power": data.get("b_aprt_power", ""),
        "b_pf":         data.get("b_pf",         ""),
        "b_freq":       data.get("b_freq",        ""),
        "c_current":    data.get("c_current",    ""),
        "c_voltage":    data.get("c_voltage",    ""),
        "c_act_power":  data.get("c_act_power",  ""),
        "c_aprt_power": data.get("c_aprt_power", ""),
        "c_pf":         data.get("c_pf",         ""),
        "c_freq":       data.get("c_freq",        ""),
    }


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def fetch_device(ip: str) -> dict | None:
    """Fetch EM status from one Shelly. Returns parsed JSON or None on error."""
    try:
        response = requests.get(
            f"http://{ip}/rpc/EM.GetStatus?id=0",
            headers={"Content-Type": "application/json"},
            timeout=2,          # tight timeout so slow devices don't lag the round
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  [WARN] {ip}: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- user input -----------------------------------------------------------
    try:
        measurement_time = float(input("Measurement duration (seconds): ").strip())
        if measurement_time <= 0:
            raise ValueError
    except ValueError:
        print("Please enter a positive number.", file=sys.stderr)
        sys.exit(1)

    ips = [f"{BASE_IP}{d}" for d in DEVICE_IDS]

    print(f"\nSampling {len(ips)} devices every ~1 s for {measurement_time} s")
    print(f"Devices: {ips[0]} … {ips[-1]}")
    print(f"Output : {CSV_FILE_2}\n")

    sample_index = 0
    start_time   = time.monotonic()

    # ThreadPoolExecutor is created once and reused across all rounds
    with ThreadPoolExecutor(max_workers=len(ips)) as executor:
        while (elapsed := time.monotonic() - start_time) < measurement_time:
            sample_index += 1
            round_start  = time.monotonic()

            # Shared timestamp stamped at the START of the round for all devices
            timestamp = datetime.now().isoformat()

            # Fire all 10 requests simultaneously
            future_to_ip = {executor.submit(fetch_device, ip): ip for ip in ips}

            rows = []
            ok_count = 0
            for future in as_completed(future_to_ip):
                ip   = future_to_ip[future]
                data = future.result()
                if data is not None:
                    rows.append(build_row(data, ip, sample_index, timestamp))
                    ok_count += 1

            # Sort rows by device so CSV order is deterministic per sample
            rows.sort(key=lambda r: r["device_ip"])
            write_rows_to_csv(rows)

            round_duration = time.monotonic() - round_start
            print(f"  Sample {sample_index:>4} | t={elapsed:6.1f}s | "
                  f"{ok_count}/{len(ips)} devices OK | round took {round_duration*1000:.0f} ms")

            # Sleep for the remainder of the 1-second window
            sleep_for = 1.0 - round_duration
            if sleep_for > 0:
                time.sleep(sleep_for)

    print(f"\nFinished. {sample_index} samples written to {CSV_FILE_2}")


if __name__ == "__main__":
    main()
