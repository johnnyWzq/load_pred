# -*- coding: utf-8 -*-
"""
Created on Tue May  8 16:28:18 2018

@author: wuzhiqiang
"""
import sql_operation as so
import pandas as pd

num = 10000
sql = so.Sql('chargingdb')
sql.create_connection(as_dict=True)
rows = {}
table_names = ['charger_info']#['charger_detail_table', 'type_info', 'eidev_info']
table_lens = {'type_info': 483, 'his_chargdata': 12655250, 'charger_info': 1594}
for table_name in table_names:
    sql_cmd = 'SELECT * FROM %s' %table_name
    cursor = sql.create_cursor(sql_cmd)
    count = table_lens[table_name]
    f = open(table_name+'.csv', 'w')#, newline='')
    first_time = True
    while count > 0:
        rows[table_name] = cursor.fetchmany(num)
        df = pd.DataFrame(rows[table_name])
        if table_name == 'his_chargdata':
            df = df.drop(['VInfoCode', 'PVIN'], axis=1)
        print('writing the data which num is %d in a file named %s'
                  %(min(num, len(rows[table_name])), table_name))
        #writer.writerows(rows[table_name])
        df.to_csv(f, header=first_time, encoding='gb18030')
        first_time = False
        count = count - num
    f.close()
    cursor.close()
sql.close_connection()
"""   
    df = pd.DataFrame(rows[table_name])
    print('save the data as a file named %s'%table_name)
    df.to_csv(table_name+'.csv', encoding='gb18030')
sql.close_connection()
"""

