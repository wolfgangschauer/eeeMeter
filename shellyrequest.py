import requests
import sys
import json

#!/usr/bin/env python3

#shelly1_ip = "10.93.10.249" #EEE-lab
shelly1_ip = "192.168.178.58" #Home

try:
    shelly1_data = requests.get(f'http://{shelly1_ip}/rpc/EM.GetStatus?id=0', headers={'Content-Type': 'application/json'}).json()
    print(shelly1_data)
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from Shelly1 device: {e}", file=sys.stderr)
    sys.exit(1) 
    
