# -*- coding: utf-8 -*-
"""
Created on Fri May 11 16:17:57 2018

@author: Admin
"""
import os
import pandas as pd
from dateutil import parser
import datetime
from preprocess_charger_detail import drop_na


def time_list(time1, time2):
    time_list = []
    while time1 <= time2:
        #time_list.append(datetime.datetime.strptime(time1.strftime('%H:%M:%S'), '%H:%M:%S'))
        time_list.append(time1.strftime('%H:%M:%S'))
        time1 += datetime.timedelta(minutes=1)
    return time_list

def power_distribute(df, cols):
    df_power = pd.DataFrame(index=cols)
    t_list = []
    func =  lambda x:parser.parse(x).time()
    for t in cols:
        t_list.append(func(t))
    df_power['time'] = t_list
    df['date'] = df['time_start'].apply(str)
    df['date'] = df['date'].apply(lambda x:x[:10])
    for i in range(len(df)):
        res1 = df.iloc[i]['time_start'].time() <= df_power['time']
        res2 = df_power['time'] <= df.iloc[i]['time_end'].time()
        df_power[i] = res1 & res2
        df_power[i] = df_power[i] * df.iloc[i]['out_power']
        #df.iloc[i]['date'] = df.iloc[i]['date'].date()

    df_power = df_power.drop('time', axis=1)
    df_power = df_power.T
    df['index'] = range(len(df))
    df = df.set_index(['index'])
    res = pd.concat([df, df_power], axis=1)
    cols = ['charger_id', 'date'] + cols
    res = res[cols]
    return res
    
def calc_power(data):
    data = data[:]
    
    data = drop_na(data, 'time_start')
    data = drop_na(data, 'time_end')
    data = data[data['time_start'] < data['time_end']]
    data = data[(data['time_end'] - data['time_start']) < datetime.timedelta(hours=4)]
    data = data[(data['time_end'] - data['time_start']) > datetime.timedelta(minutes=5)]
    
    #data['enengy']的单位为0.01度
    data['out_power'] = data['energy'] * 36.0 / (data['time_end'] - data['time_start']).apply(lambda x:x.seconds)
    data = data[data['out_power'] <= data['power']]
    return data
    
def read_csv_file(data_dir, file_name):
    
    print('reading the %s...'%file_name)
    data = pd.read_csv(os.path.join(data_dir, file_name), error_bad_lines=False,
                                    encoding='gb18030')
    print('The lengths of the data is: %d'%len(data))
    return data

def analyse_data(df):
    stat = df.describe()
    print(stat)
    for column in df.columns:
        print('-----------------')
        print(df[column].isnull().value_counts())
    

def clean_data(data):
    """
    初步清洗,并进行合并
    """
    print('cleaning his_charging data...')
    #data = data_ori[:]
    data = data.rename(columns = {'CardID': 'card_id', 'PVIN': 'VIN',
                                  'NodeNumID': 'charger_id', 'RecStartSOC': 'SOC_start',
                                  'RecEndSOC': 'SOC_end', 'RecTotalPower': 'energy',
                                  'RecStartTime': 'time_start', 'RecEndTime': 'time_end',
                                  })
    data = data[['charger_id', 'time_start', 'time_end', 'SOC_start', 'SOC_end',
                 'energy', 'card_id', 'VIN']]
    
    data_dir = os.path.join(os.path.abspath('.'), 'processed_data')
    file_name = 'processed_charger_info.csv'
    station_info = read_csv_file(data_dir, file_name)
    station_info = station_info[['charger_id', 'station_id', 'station_no', 'power']]
    
    data = data.merge(station_info, on='charger_id', how='inner')
    data = data[['station_no', 'station_id', 'charger_id', 'time_start', 'time_end', 'SOC_start', 'SOC_end',
                 'energy', 'power', 'card_id', 'VIN']]
    data['time_start'] = data['time_start'].apply(str)
    #data['time_start'] = data['time_start'].apply(lambda x: parser.parse(x))
    data['time_start'] = pd.to_datetime(data['time_start'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    data['time_end'] = data['time_end'].apply(str)
    data['time_end'] = data['time_end'].apply(lambda x: x[:19])
    data['time_end'] = pd.to_datetime(data['time_end'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
            #data['time_end'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
    data = calc_power(data)

    return data

def clustering_station_data(data, data_dir, year, first_time_dict, p_first_time_dict):
    data_gp = data.groupby('station_id')

    num = 0
    t1 = '00:00:00'
    t2 = '23:59:59'
    func =  lambda x:parser.parse(x)
    col_list = time_list(func(t1), func(t2))
    print('The numbers of the data clips is: %d'%len(data_gp.groups))

    for i in data_gp.groups:
        first_time_dict[i] = False
        p_first_time_dict[i] = False
    for i in data_gp.groups:
        df = data_gp.get_group(i) #第i组
        print('NO.%d: '%num, i, df.shape)
        num += 1
        df = df.sort_values('time_start')
        filename = os.path.join(data_dir, '%s_%s.csv'%(i, year))
        #附加模式，重复运行会产生重复数据
        df.to_csv(filename, header=first_time_dict[i], mode='a', encoding='gb18030')
        df = df[['charger_id', 'time_start', 'time_end', 'out_power']]
        df = power_distribute(df, col_list)
        filename = os.path.join(data_dir, 'P_%s_%s.csv'%(i, year))
        #附加模式，重复运行会产生重复数据
        df.to_csv(filename, header=p_first_time_dict[i], mode='a', encoding='gb18030')
    
if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'data')
    p_data_dir = os.path.join(os.path.abspath('.'), 'processed_data')
    year = '2017'
    file_name = 'his_chargdata_%s'%year
    station_info = read_csv_file(p_data_dir, 'processed_charger_info.csv')
    first_time_dict = {}
    p_first_time_dict = {}
    for i in station_info['station_id']:
        first_time_dict[i] = True
        p_first_time_dict[i] = True
    for file in os.listdir(data_dir):#获取文件夹内所有文件名
        if file_name in file:
            data_ori = read_csv_file(data_dir, file)
            data = clean_data(data_ori)
            analyse_data(data)
            data = clustering_station_data(data, p_data_dir, year, first_time_dict,
                                           p_first_time_dict)