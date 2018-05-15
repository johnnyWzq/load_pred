#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 10:52:13 2018

@author: zhiqiangwu
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dt
import matplotlib.ticker as mtick
import datetime
from matplotlib.gridspec import GridSpec

from matplotlib.dates import DayLocator, HourLocator, MinuteLocator

from preprocess_charging_data import read_csv_file

def sel_station(data, num):
    df = data[:]
    stations = df['station_id'].tolist()#取所有场站id
    if num < len(stations):
        return stations[num]
    else:
        raise ('The num of selection is out of the bound of station_id.')

def sel_xy(data, station_id, *years):
    df = data[:]
    xy = {}
    for year in years:
        xy[year] = df[df['year'] == year][df['station_id'] == station_id]#取对应year和station_id的series
    return xy

def draw_loads(xy_dict, file_name, data_dir):
    fig = plt.figure(edgecolor='k',figsize=(16, 9))
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    ax_num = len(xy_dict)
    gs = GridSpec(ax_num, 1)
    ax_num = 0
    for k, xy in xy_dict.items():
        file_name += '_%d'%k
        
        y_mean = xy.iloc[0][xy.apply(str).str.contains('mean_',regex=False)]#取所有column为mean_的列
        #y_median = xy.str.contains('median_', regex=False)
        y_max = xy.iloc[0][xy.apply(str).str.contains('max_',regex=False)]
        #y_min = xy.iloc[0][xy.apply(str).str.contains('min_',regex=False)]
        x = y_mean.index.tolist()
        x = list(map(lambda k:k[5:], x))
        x = pd.to_datetime(x, format='%H:%M:%S')
        """
        #df = pd.DataFrame({'x':x, 'y_mean':y_mean.values, 'y_max':y_max.values, 'y_min':y_min.values})
        #df.to_csv(os.path.join(p_data_dir, 'CAAHAA000102.csv'), encoding='gb18030')
    
        xy = pd.read_csv(os.path.join(p_data_dir, 'CAAHAA000102.csv'), encoding='gb18030')
        y_mean = xy['y_mean']
        y_max = xy['y_max']
        y_min = xy['y_min']
        
        x = xy['x']
        def f(x):
            return datetime.datetime.strptime('2017-01-02 ' + x[11:], '%Y-%m-%d %H:%M:%S')
        x = list(map(f, x.tolist()))#.time().tolist()
        """
        ax = plt.subplot(gs[ax_num, 0], facecolor='#383737')
        ax_num += 1
        
        ax.plot(y_mean, label='平均负载')
        ax.plot(y_max, label='最大负载')
        #ax.plot(x, y_min, label='最小负载')
        ax.legend(loc='upper right')
        ax.set_xlim(x[0], x[-1])
        ax.grid(linestyle=':') #开启网格
        ax.set_ylabel('负荷功率 (kwh)')
        ax.set_title('%d年***%s场站24小时负荷曲线'%(k, station_id[-6:]))

        ax.xaxis.set_major_locator(HourLocator())
        ax.xaxis.set_minor_locator(MinuteLocator(range(0, 60, 15)))
        ax.xaxis.set_major_formatter(dt.DateFormatter('%H:%M:%S'))
        
    fig.autofmt_xdate()
    fig.savefig(os.path.join(data_dir, '%s.jpg'%file_name), dpi=128)
    fig.show()
    

if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    p_data_dir = os.path.join(os.path.abspath('.'), 'load_pic')
    
    data = read_csv_file(data_dir, 'Loads.csv')

    #num = 3
    for num in range(1):
        station_id = sel_station(data, num)
        #station_id = 'CAAHAA000102'
        years = [2017]
        xy = sel_xy(data, station_id, *years)
        
        draw_loads(xy, station_id, p_data_dir)