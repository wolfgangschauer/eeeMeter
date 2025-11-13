import sys
import requests

#!/usr/bin/env python3

shelly1_ip = "10.93.10.249"
shelly1_data = requests.get(f'http://{shelly1_ip}/rpc/EM.GetStatus?id=0', headers={'Content-Type': 'application/json'}).json()
print(shelly1_data)

