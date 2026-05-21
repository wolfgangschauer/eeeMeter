# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 12:54:53 2026

@author: shreyash
"""

import sqlite3
conn = sqlite3.connect('shelly1.db')

cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS shelly_1 (
              time text,
              a_current real,
              a_voltage real,
              a_act_power real,
              a_aprt_power real,
              a_pf real,
              a_freq real,
              b_current real,
              b_voltage real,
              b_act_power real,
              b_aprt_power real,
              b_pf real,
              b_freq real,
              c_current real,
              c_voltage real,
              c_act_power real,
              c_aprt_power real,
              c_pf real,
              c_freq real,
              calculation_1 real,
              calculation_2 real,
              calculation_3 real,
              calculation_4 real,
              calculation_5 real,
              calculation_6 real
              )""")

conn.commit()



#tupel structure        index
#timestamp                0
#sample_index,            1
# device_ip               2
#a_current                3
#a_voltage,               4
#a_act_power,             5
#a_aprt_power,            6
#a_pf,                    7
#a_freq,                  8
#b_current,               9
#b_voltage,               10
#b_act_power,             11
#b_aprt_power,            12
#b_pf,                    13
#b_freq,                  14
#c_current,               15
#c_voltage,               16
#c_act_power              17
#c_aprt_power             18
#c_pf,                    19
#c_freq                   20


 
 


new_data = ("2026-04-23T16:03:46.062496",1,"10.93.10.240",1.363,229.2,207.3,312.2,0.67,50.1,0.874,229.4,113.5,200.2,0.57,50.1,1.005,228.7,142.4,229.5,0.59,50.1)

shelly_data = new_data


value_1 = 1.1
value_2 = 2.1
value_3 = 3.1
value_4 = 4.1
value_5 = 5.1
value_6 = 6.1


ordered_shelly_data = (shelly_data[0],
    shelly_data[3],
    shelly_data[4],
    shelly_data[5],
    shelly_data[6],
    shelly_data[7],
    shelly_data[8],
    shelly_data[9],
    shelly_data[10],
    shelly_data[11],
    shelly_data[12],
    shelly_data[13],
    shelly_data[14],
    shelly_data[15],
    shelly_data[16],
    shelly_data[17],
    shelly_data[18],
    shelly_data[19],
    shelly_data[20],
    value_1,
    value_2,
    value_3,
    value_4,
    value_5,
    value_6)
 



print (ordered_shelly_data)

cursor.execute("INSERT INTO shelly_1 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ordered_shelly_data)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()