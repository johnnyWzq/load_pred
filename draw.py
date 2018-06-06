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
from dateutil import parser 
import re
from matplotlib.gridspec import GridSpec
from matplotlib.dates import HourLocator, MinuteLocator
from functools import reduce

from preprocess_charging_data import time_list

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
        y_median = xy.iloc[0][xy.apply(str).str.contains('median_',regex=False)]
        y_max = xy.iloc[0][xy.apply(str).str.contains('max_',regex=False)]
        y_75 = xy.iloc[0][xy.apply(str).str.contains('75%_',regex=False)]
        y_25 = xy.iloc[0][xy.apply(str).str.contains('25%_',regex=False)]
        x = y_mean.index.tolist()
        x = list(map(lambda k:k[5:], x))
        x = pd.to_datetime(x, format='%H:%M:%S')
        
        #df = pd.DataFrame({'x':x, 'y_mean':y_mean.values, 'y_max':y_max.values})
        #df.to_csv(os.path.join(p_data_dir, '%s.csv'%station_id), encoding='gb18030')
        """
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
        
        ax.plot(x, y_mean, label='平均负载')
        ax.plot(x, y_max, color='silver', label='最大负载')
        ax.plot(x, y_median, label='中位数负载')
        ax.plot(x, y_75, label='75%位数负载')
        ax.plot(x, y_25, label='25%位数负载')
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
    
def draw_loads_type(xy_dict, file_name, data_dir, *args):
    fig = plt.figure(edgecolor='k',figsize=(16, 28))
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
    
    ax_num = len(xy_dict)
    gs = GridSpec(ax_num, 1)
    ax_num = 0
    #fixed = []
    for k, xy in xy_dict.items():
        file_name += '_%s'%k 
        print('calculating the data of axis_y...')
        t1 = '00:00:00'
        t2 = '23:59:59'
        func =  lambda x:parser.parse(x)
        cols = time_list(func(t1), func(t2))
        y_mean = xy[list(map(lambda x:'mean_'+x, cols))]
        y_median = xy[list(map(lambda x:'median_'+x, cols))]
        y_max = xy[list(map(lambda x:'max_'+x, cols))]
        y_25 = xy[list(map(lambda x:'25%_'+x, cols))]
        y_75 = xy[list(map(lambda x:'75%_'+x, cols))]
        y_diff = xy[list(map(lambda x:'diff_'+x, cols))]
        y_diff2 = xy[list(map(lambda x:'diff2_'+x, cols))]
            
        x = pd.to_datetime(cols, format='%H:%M:%S')
        first_time = True
        for cnt in range(len(xy)):
            
            print('drawing the part%d of %s picture...'%(cnt, file_name))
            if first_time:
                ax = plt.subplot(gs[ax_num, 0], facecolor='#383737')
                if 'mean' in args:
                    ax.plot(x, y_mean.iloc[cnt], color='r', label='平均负载')
                if 'max' in args:
                    ax.plot(x, y_max.iloc[cnt], color='g',label='最大负载')
                if 'median' in args:
                    ax.plot(x, y_median.iloc[cnt], color='y',label='中位数负载')
                if '25%' in args:
                    ax.plot(x, y_25.iloc[cnt], color='c',label='25%位负载')
                if '75%' in args:
                    ax.plot(x, y_75.iloc[cnt], color='m',label='75%位负载')
                if 'diff' in args:
                    ax.plot(x, y_diff.iloc[cnt], color='b',label='负载一阶导')
                if 'diff2' in args:
                    ax.plot(x, y_diff2.iloc[cnt], color='silver',label='负载二阶导')
                if 'fixed' in args:
                    ax.fill_between(x, 0, y_mean.iloc[cnt], color='g', alpha=0.3, label='平均负载')
                    
                ax.legend(loc='upper right')
                
                first_time = False
            else:
                ax = plt.subplot(gs[ax_num, 0], facecolor='#383737')
                if 'mean' in args:
                    ax.plot(x, y_mean.iloc[cnt], color='r', label='平均负载')
                if 'max' in args:
                    ax.plot(x, y_max.iloc[cnt], color='g',label='最大负载')
                if 'median' in args:
                    ax.plot(x, y_median.iloc[cnt], color='y',label='中位数负载')
                if '25%' in args:
                    ax.plot(x, y_25.iloc[cnt], color='c',label='25%位负载')
                if '75%' in args:
                    ax.plot(x, y_75.iloc[cnt], color='m',label='75%位负载')
                if 'diff' in args:
                    ax.plot(x, y_diff.iloc[cnt], color='b',label='负载一阶导')
                if 'diff2' in args:
                    ax.plot(x, y_diff2.iloc[cnt], color='silver',label='负载二阶导')
                if 'fixed' in args:
                    ax.fill_between(x, 0, y_mean.iloc[cnt], color='g', alpha=0.3, label='平均负载')
        ax.grid(linestyle=':') #开启网格
        ax.set_ylabel('负荷功率 (kwh)')
        ax.set_title('%s场站24小时负荷曲线'%k)
        ax.set_xlim(x[0], x[-1])
        ax.xaxis.set_major_locator(HourLocator())
        ax.xaxis.set_minor_locator(MinuteLocator(range(0, 60, 15)))
        ax.xaxis.set_major_formatter(dt.DateFormatter('%H:%M:%S'))

        ax_num += 1
    file_name += '_' + reduce(lambda x,y:x+'_'+y, [s for s in args])
    fig.autofmt_xdate()
    fig.savefig(os.path.join(data_dir, '%s.jpg'%file_name), dpi=128)
    fig.show()

if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    p_data_dir = os.path.join(os.path.abspath('.'), 'load_pic')
    data = pd.read_csv(os.path.join(data_dir, 'Loads.csv'), error_bad_lines=False,
                                    encoding='gb18030')
    #num = 3
    #for num in range(1):#range(10, 50):
    for station_id in data['station_id'].tolist():
        #station_id = sel_station(data, num)
        if re.match(r'PHCAGDB\d+', station_id):
            years = [2017]
            xy = sel_xy(data, station_id, *years)
            
            draw_loads(xy, station_id, p_data_dir)