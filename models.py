#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 11:30:17 2018

@author: zhiqiangwu
"""
import os
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering

from preprocess_charging_data import read_csv_file
from draw import draw_loads_type

def stations_info_type(df1, df2_dir):
    df2 = pd.read_excel(df2_dir)
    df1 = df1.merge(df2, on='station_id')
    return df1
    
def standard_data(data_ori, method='normalize'):
    data = data_ori[:]
    stations = data['station_id']
    data = data.drop(['Unnamed: 0', 'year', 'station_id'], axis=1)
    if method == 'normalize':
        data = (data - data.min())/(data.max() - data.min())
    elif method == 'med':
        data = (data - data.mean()) / (data.std())
    data = data.replace(np.inf, np.nan)
    data = data.replace(-np.inf, np.nan)
    data = data.fillna(0)
    return data.round(8), stations

def detect_k(data):
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import linkage,dendrogram
    #使用scipy的层次聚类函数
    Z = linkage(data_std, method = 'ward', metric = 'euclidean') #谱系聚类图
    P = dendrogram(Z, 0) #画谱系聚类图
    plt.show()
    
def build_cluster_model(data, k, linkage):
    
    model = AgglomerativeClustering(n_clusters=k, linkage=linkage)
    model.fit(data)
    
    r = pd.concat([data, pd.Series(model.labels_, index=data.index)], axis=1)
    r.columns = list(data.columns) + [u'聚类类别']
    
    return r

if __name__ == '__main__':
    data_dir = os.path.join(os.path.abspath('.'), 'load_data')
    filename = 'Loads_d.csv'
    data_ori = read_csv_file(data_dir, filename)
    method = 'med'
    data_std, stations = standard_data(data_ori, method)
    #detect_k(data_std)
    k = 4
    linkage = 'ward'#'ward', 'average', 'complete'
    result = build_cluster_model(data_std, k, linkage)
    result['station_id'] = stations
    res = result[['station_id', '聚类类别']]
    data_ori = data_ori.merge(res, on='station_id')
    
    file_name0 = 'result_' + method
    p_data_dir = os.path.join(os.path.abspath('.'), file_name0)
    
    res = stations_info_type(res, os.path.join(os.path.join(os.path.abspath('.'), 'processed_data'),
                                              'stations_info.xlsx'))
    res.to_excel(os.path.join(p_data_dir, '%s_cluster_stations_%s.xlsx'%(linkage, method)))
    
    xy_dict = {}
    res_gp = data_ori.groupby('聚类类别')
    
    writer = pd.ExcelWriter(os.path.join(p_data_dir, 
                          '%s_stations_data_%s.xlsx'%(linkage, method)))
    for i in res_gp.groups:
        k = 'type' + str(i)
        xy_dict[k] = res_gp.get_group(i)
        cols = xy_dict[k].columns.tolist()
        xy_mean = xy_dict[k][[col for col in cols if 'mean' in col]]
        xy_mean['station_id'] = xy_dict[k]['station_id']
        xy_mean = xy_mean.set_index('station_id', drop=True)
        xy_mean.to_excel(writer, k)
        
        xy_dict[k] = xy_dict[k].drop(['聚类类别', 'station_id'], axis=1)
    writer.save()
    
    draw_loads_type(xy_dict, '%s_loads_'%linkage, p_data_dir,
             'mean', \
             'median', \
             'max', \
             'min', \
             '25%', \
             '75%', \
             #'diff', \
             #'diff2' \
             )