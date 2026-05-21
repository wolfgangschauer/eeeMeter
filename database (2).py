import sqlite3
database = sqlite3.connect('test.db')

cursor = database.cursor()

#deelt everything
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

for table in tables:
    cursor.execute (f"DROP TABLE IF EXISTS {table[0]}")



#geting useful variables from dictionary and making temp dictionary
wanted_variables = ["timestamp",
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
                    "c_freq"]

temp_values =      {"timestamp": "5 o clock",
                    "a_current": 2,
                    "a_voltage": 3, 
                    "a_act_power": 4,
                    "a_aprt_power": 5,
                    "a_pf":6,
                    "a_freq":7,
                    "b_current":8,
                    "b_voltage":9,
                    "b_act_power":10,
                    "b_aprt_power":11,
                    "b_pf":12,
                    "b_freq":13,
                    "c_current":14,
                    "c_voltage":15,
                    "c_act_power":16,
                    "c_aprt_power" : 17,
                    "c_pf" : 18,
                    "c_freq" : 19,
                    "ip" : "10.97.10.240" }
                    
#shely listand ip list
shelly_list = ["shelly0",
               "shelly1", 
               "shelly2", 
               "shelly3", 
               "shelly4", 
               "shelly5",
               "shelly6", 
               "shelly7",
               "shelly8", 
               "shelly9"]

shelly_ip = ["10.97.10.240",
             "10.97.10.241",
             "10.97.10.242",
             "10.97.10.243",
             "10.97.10.244",
             "10.97.10.245",
             "10.97.10.246",
             "10.97.10.247",
             "10.97.10.248",
             "10.97.10.249",]

    

#filtering real variables from uusefulvariable
text_index = [0,1]
real_variables = [variable for variable in wanted_variables]
for num in text_index:
    real_variables.remove(wanted_variables[num])
    
    
#making a tuple for table columns
column_tuple = tuple(f"{variable} REAL" if variable in real_variables else f"{variable} TEXT"
               for variable in wanted_variables)


#creating table and looping with lists
for ip in shelly_ip:
    table_name = ip.replace(".", "_")
    make_table = f"CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(column_tuple)})"
    cursor.execute (make_table)



#making tuple which will be inserted in table 
insert_tuple = tuple(temp_values[variable]for variable in wanted_variables)


#inserting data and automting placeholders and filtering data to correct taables
placeholders = ", ".join("?" for element in insert_tuple)

insert_row = f"INSERT INTO {shelly_ip} VALUES ({placeholders})"

cursor.execute(insert_row, insert_tuple)
database.commit()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

print(cursor.fetchall())

                 









