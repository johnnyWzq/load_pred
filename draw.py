#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 14 10:52:13 2018

@author: zhiqiangwu
"""

import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from preprocess_charging_data import read_csv_file

def sel_station(data, num):
    df = data[:]
    stations = set(df['station_id'].tolist())#取所有场站id
    if num < len(stations):
        return stations[num]
    else:
        raise ('The num of selection is out of the bound of station_id.')

def sel_xy(data, station_id, *years):
    df = data[:]
    xy = {}
    for year in years:
        xy[year] = df[df['year']==year][df['station_id'] == station_id]#取对应year和station_id的series
    return xy

def draw_loads(xy_dict, file_name, data_dir):
    fig = plt.figure(edgecolor='k',figsize=(16, 9))
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    ax_num = len(xy_dict)
    gs = GridSpec(ax_num)
    ax_num = 0
    for k, xy in xy_dict.items():
        file_name += '_%s'%k
        y_mean = xy.str.contains('mean_', regex=False)
        #y_median = xy.str.contains('median_', regex=False)
        y_max = xy.str.contains('max_', regex=False)
        y_min = xy.str.contains('min_', regex=False)
        x = xy.columns.str.contains('mean_', regex=False)[5:]
        
        ax = plt.subplot(gs[ax_num], facecolor='#383737')
        ax_num += 1
        
        ax.plot(x, y_mean, linestyle='--', label='平均负载')
        ax.plot(x, y_max, linestyle='－－', label='最大负载')
        ax.plot(x, y_min, linestyle='--', label='最小负载')
        
        ax.grid(linestyle=':') #开启网格
        ax.legend(loc='upper right')
        ax.ylabel('负荷分布 kwh')
        ax.title('％s年场站**%s负荷曲线'%(k, station_id[-5:]))  
    
    fig.autofmt_xdate()
    fig.savefig(os.join(data_dir, '%s.jpg'%file_name), dpi=128)
    fig.show()
    

if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    p_data_dir = os.path.join(os.path.abspath('.'), 'load_pic')
    
    data = read_csv_file(data_dir, 'Load.csv')
    num = 3
    station_id = sel_station(data, num)
    years = ('2017')
    xy = sel_xy(data, station_id, *years)
    draw_loads(xy, station_id, p_data_dir)