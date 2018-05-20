#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 20 11:12:00 2018

@author: zhiqiangwu
"""

import os
import re
import pandas as pd
from dateutil import parser

from preprocess_charging_data import read_csv_file, time_list

def calc_diff_mean(data):
    """
    计算mean值的diff，diff2，并添加进原data中
    """
    t1 = '00:00:00'
    t2 = '23:59:59'
    func =  lambda x:parser.parse(x)
    cols = time_list(func(t1), func(t2))
    data = data.drop(['Unnamed: 0', 'Unnamed: 0.1'], axis=1)
    y_mean = data[list(map(lambda x:'mean_'+x, cols))]
    y_mean_diff = y_mean.diff(axis=1)
    y_mean_diff2 = y_mean_diff.diff(axis=1)
    y_mean_diff.columns = list(map(lambda x:'diff_'+x, cols))
    y_mean_diff2.columns = list(map(lambda x:'diff2_'+x, cols))
    data = pd.concat([data, y_mean_diff], axis=1)
    data = pd.concat([data, y_mean_diff2], axis=1)
    data = data.fillna(0)
    return data
    
if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    filename = 'Loads.csv'
    data_ori = read_csv_file(data_dir, filename)
    data = calc_diff_mean(data_ori)
    data.to_csv(os.path.join(data_dir, 'Loads_d.csv'), encoding='gb18030')