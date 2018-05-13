# -*- coding: utf-8 -*-
"""
Created on Tue May  8 18:21:47 2018

@author: wuzhiqiang
"""
import pymssql
import pandas as pd
import csv

db_name = 'chargingdb'
config = {'s': 'localhost', 'u': 'sa', 'p': '123456', 'db': db_name}
print('conneting the database...')
try:
    conn = pymssql.connect(server=config['s'], user=config['u'],
                           password=config['p'], database=config['db'])
except pymssql.OperationalError:
    print ("error: Could not Connection SQL Server!please check your dblink configure!")
else:
    print('the connetion is sucessful.')
    
cursor = conn.cursor()

num = 100
rows = {}
table_names = ['type_info']#['his_chargdata']#['charger_detail_table', 'type_info', 'eidev_info']
for table_name in table_names:
    sql_cmd = 'SELECT * FROM %s' %table_name
    cursor.execute(sql_cmd)
    rows[table_name] = cursor.fetchmany(num)
    rowcount = cursor.rowcount
    print(rowcount)
    if rowcount >=0:
        f = open(table_name+'.csv', 'w', newline='')
        writer = csv.writer(f)
        print('writing the data which num is %d in a file named %s'%(num, table_name))
        writer.writerows(rows[table_name])
    f.close()

    cursor.close()
conn.close()

