# -*- coding: utf-8 -*-
"""
Created on Tue May  8 10:59:42 2018

@author: wuzhiqiang
"""
import pymssql
import pandas as pd

class Sql():
    
    def __init__(self, db_name):
        
        self.db_name = db_name
        self.config = {'s': 'localhost', 'u': 'sa', 'p': '123456', 'db': db_name}
        
    def create_connection(self, as_dict=False):
        """
        create a connection
        """
        #尝试数据库连接
        print('conneting the database...')
        try:
            self.conn = pymssql.connect(server=self.config['s'], user=self.config['u'],
                                   password=self.config['p'], database=self.config['db'],
                                   as_dict=as_dict)
        except pymssql.OperationalError:
            print ("error: Could not Connection SQL Server!please check your dblink configure!")
        else:
            print('the connetion is sucessful.')

    def close_connection(self):
        """
        close the connection
        """
        self.conn.close()
        print('the connetion is closed.')

    def create_cursor(self, query_cmd):
        """
        """
        print("start querying...")
        self.cursor = self.conn.cursor()
        self.cursor.execute(query_cmd)
        return self.cursor
        
    def close_cursor(self):
        if self.cursor:
            self.cursor.close()
            
    def get_count(self, query_cmd):
        cursor = self.create_cursor(query_cmd)
        cursor.execute(query_cmd)
        row = cursor.fetchall()
        count = cursor.rowcount
        cursor.close()
        return count
        
    def query_many_rows(self, query_cmd, num):
        """
        query and fetch the num of row
        """
        print("start querying...")
        self.cursor = self.conn.cursor()
        self.cursor.execute(query_cmd)
        row = self.cursor.fetchmany(size=num)
        print(row)
        row = self.cursor.fetchmany(size=num)
        print(row)
        self.cursor.close()
        return row
    
    def query_all_rows(self, query_cmd):
        """
        query and fetch all
        """
        print("start querying...")
        self.cursor = self.conn.cursor()
        self.cursor.execute(query_cmd)
        row = self.cursor.fetchall()
        self.cursor.close()
        return row
        
def main():

    sql = Sql('chargingdb')
    sql.create_connection(as_dict=True)
    #query_cmd = 'SELECT * FROM charger_detail_table'
    #row = sql.query_one_row(query_cmd)
    #rows = sql.query_all_rows(query_cmd)
    #df = pd.DataFrame(rows)
    #df.to_csv('cd.csv', encoding='gb18030')
    #print('----------------------------------')
    sql_cmd = 'select count(*) from type_info'
    cnt = sql.get_count(sql_cmd)
    print(cnt)
    #print(len(rows))
    sql.close_connection()

if __name__ == '__main__':
    main()