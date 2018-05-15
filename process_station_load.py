#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 12 12:38:11 2018

@author: zhiqiangwu
"""
import os
import re
import pandas as pd
from functools import reduce
from preprocess_charging_data import analyse_data, read_csv_file


def process_data(data_ori):
    cols = data_ori.columns
    data_gp = data_ori.groupby('date')
    result = pd.DataFrame()
    num = 0
    print('The numbers of the data clips is: %d'%len(data_gp.groups))
    for i in data_gp.groups:
        df = data_gp.get_group(i) #第i组
        print('NO.%d: '%num, i, df.shape)
        num += 1
        df = df.drop('date', axis=1)
        power = df.sum()
        power = power.append(pd.Series({'date': i}))
        power = pd.DataFrame(power).T
        result = result.append(power, ignore_index=True)
    result = result[cols]
    return result

def calc_load(data_dir, file, data=None):
    if data is None:
        data = pd.read_csv(os.path.join(data_dir, file), error_bad_lines=False,
                                    encoding='gb18030')
    s = re.match(r'(\w\_\w)_(\w+)_(\d+\.csv)', file)
    station_id = s.group(2)
    print('calculate the load_data of station %s.'%station_id)
    year = data['date'].iloc[1][:4]
    data = data.drop('date', axis=1)
    cols = data.columns.tolist()
    paras = ['mean_', 'median_', 'max_', 'min_', 'std_', '25%_', '75%_', \
            'count_']
    recols = {}
    for para in paras:
        recols[para[:-1]] = list(map(lambda x:para+x, cols))
    load_cols= reduce(lambda x,y:x+y, [col for col in recols.values()])
    load_cols.insert(0, 'station_id')
    load_cols.insert(0, 'year')
    load = pd.DataFrame(index=[len(data)], columns=load_cols)
    load['year'] = year
    load['station_id'] = station_id
    load = load.fillna(0)
    print('calculate the mean of station: %s.'%station_id)
    load[recols['mean']] = data.mean(skipna=True).values
    print('calculate the std of station: %s.'%station_id)
    load[recols['std']] = data.std(skipna=True).values
    print('calculate the max of station: %s.'%station_id)
    load[recols['max']] = data.max(skipna=True).values
    print('calculate the min of station: %s.'%station_id)
    load[recols['min']] = data.min(skipna=True).values
    print('calculate the median of station: %s.'%station_id)
    load[recols['median']] = data.median(skipna=True).values
    print('calculate the 25%% of station: %s.'%station_id)
    load[recols['25%']] = [data[col].quantile(.25) for col in data.columns]#data[data.columns.tolist].quantile(0.25, 1)
    print('calculate the 75%% of station: %s.'%station_id)
    load[recols['75%']] = [data[col].quantile(.75) for col in data.columns]
    print('calculate the count of station: %s.'%station_id)
    load[recols['count']] = data.count().values

    return load
    
if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'processed_data')
    p_data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    years = ['2017']
    first_time = True
    for year in years:
        file_name = r'P_\w+\_%s.csv'%year
        load_data = pd.DataFrame()
        for file in os.listdir(data_dir):#获取文件夹内所有文件名
            if re.search(file_name, file):
                data_ori = read_csv_file(data_dir, file)
                data_ori = data_ori.drop(['index', 'charger_id'], axis=1)
                #analyse_data(data_ori)
                if len(data_ori) > 100:
                    data = process_data(data_ori)
                    print(len(data))
                    data.to_csv(os.path.join(p_data_dir, 'L_'+file), encoding='gb18030')
                    
                    load_data = load_data.append(calc_load(p_data_dir, 'L_'+file,
                                                           data=data))
        load_data.to_csv(os.path.join(p_data_dir, 'Loads.csv'), mode='a',
                                 header=first_time, encoding='gb18030')
        first_time = False