# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:06:27 2018

@author: wuzhiqiang
"""

import os
import re
import pandas as pd

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

if __name__ == '__main__':
    
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    df = read_files(data_dir, 'cluster')
    df.to_excel(os.path.join(data_dir, 'cluster_result.xlsx'))
                            