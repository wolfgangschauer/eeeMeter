
import requests
import sys
import json
#import csv
#import os
import time
from datetime import datetime
#import streamlit as st
import sqlite3
#import pandas as pd
database = sqlite3.connect('test.db')

cursor = database.cursor()

###########################################################################################################

#delet everything
#cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#
#tables = cursor.fetchall()
#
#for table in tables:
#   cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}"')

############################################################################################################

SHELLY_IPS =["10.93.10.240",
             "10.93.10.241",
             "10.93.10.242",
             "10.93.10.243",
             "10.93.10.244",
             "10.93.10.245",
             "10.93.10.246",
             "10.93.10.247",
             "10.93.10.248",
             "10.93.10.249",]

wanted_variables = ["time",
                    "date",
                    "ip",
                    "a_current",
                    "a_voltage", 
                    "a_act_power",
                    "a_aprt_power",
                    "a_pf",
                    "a_freq",
                    "b_current",
                    "b_voltage",
                    "b_act_power",
                    "b_aprt_power",
                    "b_pf",
                    "b_freq",
                    "c_current",
                    "c_voltage",
                    "c_act_power",
                    "c_aprt_power",
                    "c_pf",
                    "c_freq",
                    "total_energy_ws",
                    "total_aprt_power",
                    "total_act_power"]

def val(data: dict, key: str):
    """
    Safely read a value from the device response dictionary.
    Returns an empty string if the key does not exist,
    so the CSV cell is left blank instead of crashing.
    """
    v = data.get(key)
    return 0 if v is None else v


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

####################################################################################

def build_dictionary(data: dict, ip: str, interval: int) -> dict:

    timestamp = datetime.now()
    time = timestamp.time().isoformat()
    date = timestamp.date().isoformat()

    def energy(key: str):
        """Calculate energy in Watt-seconds for the given power key."""
        power = data.get(key)
        return round(power * interval, 3) if power is not None else 0
    
    dictionary = {
        "date":             date,
        "time":             time,
        "ip":        ip,

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
    return dictionary

#################################################################################################################

table_names_ip = [ip.replace(".", "_") for ip in SHELLY_IPS]
    

#filtering real variables from uusefulvariable
def making_column_tuple ():
    text_index = [0,1,2]
    real_variables = [variable for variable in wanted_variables]
    for num in text_index:
       real_variables.remove(wanted_variables[num])
    
#making a tuple for table columns
    global column_tuple
    column_tuple = tuple(f"{variable} REAL" if variable in real_variables else f"{variable} TEXT"
                    for variable in wanted_variables)


#creating table and looping with lists
def creating_tables():
    for ip in SHELLY_IPS:
        table_name = ip.replace(".", "_")
        make_table = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(column_tuple)})'
        cursor.execute(make_table)









#################################################################################################################

def main(interval: int) -> None:
    """
    Poll all Shelly devices once.
    For each device: fetch data → build row → save to CSV.
    Devices that are unreachable are skipped with a warning.
    """
    making_column_tuple()
    creating_tables()
    for ip in SHELLY_IPS:
        try:
            print(f"Fetching data from {ip}...")
            data = fetch_data(ip)
            print(f"  Raw data: {json.dumps(data, indent=2)}")
            #making tuple which will be inserted in table 
            dictionary = build_dictionary(data, ip, interval)
            insert_tuple = tuple(dictionary[variable]for variable in wanted_variables)
            #inserting data and automting placeholders and filtering data to correct taables
            placeholders = ", ".join("?" for element in insert_tuple)
            ip_name = dictionary["ip"].replace(".", "_")
            insert_row = f'INSERT INTO "{ip_name}" VALUES ({placeholders})'

            cursor.execute(insert_row, insert_tuple)
            database.commit()
#insert make place holders and call insert row query from making_database_and_components ifiuniction
        except requests.exceptions.RequestException as e:
            print(f"  Skipping {ip} — network error: {e}", file=sys.stderr)
        except Exception as e:
            print(f"  Skipping {ip} — unexpected error: {e}", file=sys.stderr)

#################################################################################################################

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