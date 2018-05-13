# -*- coding: utf-8 -*-
"""
Created on Wed May  9 16:17:34 2018

@author: wuzhiqiang
"""
"""
对表charger_detail_table进行预处理
将有用的列保留，去除坏值空值
将eidev_info表中对应站或桩的电价和服务类型合并进来
"""
import pandas as pd
import os
import re

data_dir = 'data/'

def drop_na(data, colname):
    data = data.drop(data[data[colname].isnull()].index.tolist())
    return data

def read_csv_files(data_dir, keyword):
    temp = []
    
    for file in os.listdir(data_dir):#获取文件夹内所有文件名
        if keyword in file:
            print(file)
            open(data_dir + file)
            temp.append(pd.read_csv(data_dir+file, error_bad_lines=False,
                                    encoding='gb18030'))
    temp = pd.concat(tuple(temp))
    return temp

def read_data(data_dir):
    """
    读取数据
    """
    data_dict = {}
    
    data_dict['charger_info'] = read_csv_files(data_dir, 'charger_detail_table')
    data_dict['charger_info_1'] = read_csv_files(data_dir, 'eidev_info')
    data_dict['charger_info_2'] = read_csv_files(data_dir, 'charger_info')
    
    return data_dict 

def analyse_data(data_dict_ori):
    statistics = {}
    for key, df in data_dict_ori.items():
        print(key)
        statistics[key] = df.describe()

def clean_data(data_dict_ori):
    """
    初步清洗,并进行合并
    """
    data_dict = {}
    #对每一张表进行清洗
    #charger_info
    print('cleaning charger_info data...')
    data = data_dict_ori['charger_info']
    data = data.rename(columns = {'CityCode': 'city_code', 'DevID': 'charger_id',
                                  'CompanyName': 'productor', 'cdzlx': 'charger_type',
                                  'PowerV': 'power', 'Connectors': 'plug_num',
                                  'cdywlz': 'operator', 'CreateTime': 'operation_time',
                                  })
    data = data[['city_code', 'charger_id', 'productor', 'charger_type', 'power', 'operation_time']]
    data = data.drop_duplicates(['charger_id']) #去重
    print(len(data))
    data = drop_na(data, 'charger_id') #去na
    print(len(data))
    data['charger_type'] = data['charger_type'].fillna('交流')
    tmp = data['charger_type'].copy()
    for key in set(data['charger_type'].tolist()):
        if re.search('交流', key):
            tmp[tmp == key] = '交流'
        elif re.search('直流', key) or re.search('交直流', key) or \
                    re.search('宽电压', key) or re.search('放电', key):
            tmp[tmp == key] = '直流'
        else:
            tmp[tmp == key] = '交流'
    data['charger_type'] = tmp
    print(set(data['charger_type'].tolist()))
    data['power'] = data['power'].fillna(10)
    data = data[data['power'] > 1]
    print(len(data))
    print(set(data['power'].tolist()))
    tmp = data['operation_time'].copy()
    tmp[tmp < '2010'] = '2010-01-01'
    data['operation_time'] = tmp
    data_dict['cp_info'] = data
    #charger_info_1
    print('cleaning charger_info_1 data...')
    data = data_dict_ori['charger_info_1']
    data = data.rename(columns = {'DevID': 'charger_id', 'SUBServiceType': 'cp_service_type',
                                  'TotalMode': 'power_price', 'BelongToID': 'station_no'})
    data = data[['charger_id', 'cp_service_type', 'power_price', 'station_no']]
    print(len(data))
    data = data.drop_duplicates(['charger_id']) #去重
    print(len(data))
    data = drop_na(data, 'charger_id') #去na
    print(len(data))
    tmp = data['power_price'].copy()
    tmp[tmp < 0] = 0
    data['power_price'] = tmp
    data['cp_service_type'] = data['cp_service_type'].fillna(0) #空值填0
    print(len(data))
    data = drop_na(data, 'station_no') #去na
    print(len(data))
    data_dict['cp_info_1'] = data
    
    #charger_info_2
    print('cleaning charger_info_2 data...')
    data = data_dict_ori['charger_info_2']
    data = data.rename(columns = {'StationID': 'station_no', 'StationNo': 'station_id',
                                  'StationName': 'station_name', 'StationType': 'service_type',
                                  'StationX': 'pos_X', 'StationY': 'pos_Y'})
    data = data[['station_no', 'service_type', 'station_id',
                 'station_name', 'pos_X', 'pos_Y']]
    print(len(data))
    data = data.drop_duplicates(['station_id']) #去重
    data = drop_na(data, 'station_no') #去na
    print(len(data))
    data_dict['cp_info_2'] = data
    
    data = data_dict['cp_info'].merge(data_dict['cp_info_1'], on=['charger_id'], how='inner')
    data = data.merge(data_dict['cp_info_2'], on=['station_no'], how='outer')
    data = drop_na(data, 'charger_id') #去na
    
    BASE_DIR = os.path.join(os.path.abspath('.'), 'processed_data')

    data.to_csv(os.path.join(BASE_DIR, 'processed_charger_info.csv'), encoding='gb18030')
    return data

def main():
    data_dict_ori = read_data(data_dir)
    analyse_data(data_dict_ori)
    charger_info = clean_data(data_dict_ori)
    print('------------------')
    print(len(charger_info))
    
if __name__ == '__main__':    
    main()