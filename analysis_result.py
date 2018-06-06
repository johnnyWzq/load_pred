# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:06:27 2018

@author: wuzhiqiang
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def read_files(data_dir, keyword):
    temp = []
    for file in os.listdir(data_dir):
        if re.search(keyword, file):
            df0 = pd.read_excel(os.path.join(data_dir, file))
            t = re.match(r'(\w+)_(cluster)_(\w+)', file)
            df0 = df0.rename(columns={'聚类类别': t.group(1)})
            temp.append(df0)
           # df = df.merge(df0, on='station_id')
    temp = pd.concat(tuple(temp), axis=1)
    t = temp['station_id']
    temp = temp.drop('station_id', axis=1)
    cols = temp.columns
    temp['station_id'] = t.iloc[:, [0]]
    temp = temp[['station_id'] + list(cols)]
    return temp

def analysis_data(df, file_name):
    print(df.describe())
    print('----------------------------------------------')
    
   # data.sort_values(ascending = False)
    fig = plt.figure()#(figsize=(16,4))
    if df.shape[0] > 25:
        count = 0
        l = df.shape[0]
        while l > 0:
            data = df[0:min(25, len(df))]
            data = data.T
            data.plot(kind='box')
            df = df[(25*count+min(25,len(df))):]
            plt.savefig(file_name+'_%d.jpg'%count, dpi=128)
            count += 1
            l = df.shape[0]
    else:
        data = df[:].T
        data.plot(kind='box')
        plt.savefig(file_name+'.jpg', dpi=128)
    fig.show()
       
if __name__ == '__main__':
    """
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    df = read_files(data_dir, 'cluster')
    df.to_excel(os.path.join(data_dir, 'cluster_result.xlsx'))
    """             
    data_dir = os.path.join(os.path.abspath('.'), 'result_med')
    print('reading the excel...')
    data_dict = pd.read_excel(os.path.join(data_dir, 'ward_stations_data_med.xlsx'), 
                       sheet_name=None, index_col='station_id')
    for k, v in data_dict.items():
        analysis_data(v, os.path.join(data_dir, k))