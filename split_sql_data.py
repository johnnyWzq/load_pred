# -*- coding: utf-8 -*-
"""
Created on Wed May  9 13:36:16 2018

@author: wuzhiqiang
"""
import pymssql
import pandas as pd



def create_connection(config, as_dict=False):
    """
    create a connection
    """
    #尝试数据库连接
    print('conneting the database...')
    try:
        conn = pymssql.connect(server=config['s'], user=config['u'],
                               password=config['p'], database=config['db'],
                               as_dict=as_dict)
    except pymssql.OperationalError:
        print ("error: Could not Connection SQL Server!please check your dblink configure!")
    else:
        print('the connetion is sucessful.')
        return conn

def close_connection(conn):
    """
    close the connection
    """
    conn.close()
    print('the connetion is closed.')

#------------------------------------------------------------------------------

db_name = 'chargingdb'
config = {'s': 'localhost', 'u': 'sa', 'p': '123456', 'db': db_name}
conn = create_connection(config)
years = ['2015', '2016', '2017']
count = {}
cursor = conn.cursor()
for year in years:
    sql_cmd = "select count (*) from his_chargdata "\
                "where RecEndTime between '%s-01-01' and '%s-12-31'" % (year, year)

    cursor.execute(sql_cmd)
    row = cursor.fetchall()
    count[year] = row[0][0]
    print('the length of data_%s is: %d' %(year, count[year]))
cursor.close()
close_connection(conn)

conn = create_connection(config, as_dict=True)
cursor = conn.cursor()
max_row = 500000
for year in years:
    sql_cmd = "select * from his_chargdata "\
                "where RecEndTime between '%s-01-01' and '%s-12-31'" % (year, year)
    cursor.execute(sql_cmd)
    time = 0
    while count[year] > 0:
        rows = cursor.fetchmany(max_row)
        df = pd.DataFrame(rows)
        file_name = 'data\%s_%s_%d.csv'%('his_chargdata', year, time)
        print('writing the data which num is %d in a file named %s_%s_%d'
                  %(min(max_row, len(rows)), 'his_chargdata', year, time))
        df.to_csv(file_name, encoding='gb18030')
        time += 1
        count[year] = count[year] - max_row
cursor.close()
close_connection(conn)