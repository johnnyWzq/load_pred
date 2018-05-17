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

def standard_data(data):
    stations = data['station_id']
    data = data.drop(['Unnamed: 0', 'Unnamed: 0.1', 'year', 'station_id'], axis=1)
    data = (data - data.min())/(data.max() - data.min())
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
    filename = 'Loads.csv'
    data_ori = read_csv_file(data_dir, filename)
    data_std, stations = standard_data(data_ori)
    #detect_k(data_std)
    k = 4
    linkage = 'complete'#'ward', 'average', 'complete'
    result = build_cluster_model(data_std, k, linkage)
    result['station_id'] = stations
    res = result[['station_id', '聚类类别']]
    res.to_excel(os.path.join(data_dir, '%s_cluster_stations.xlsx'%linkage))
    xy_dict = {}
    res_gp = result.groupby('聚类类别')
    for i in res_gp.groups:
        k = 'type' + str(i)
        xy_dict[k] = res_gp.get_group(i)
        xy_dict[k] = xy_dict[k].drop(['聚类类别', 'station_id'], axis=1)
        
    draw_loads_type(xy_dict, '%s_loads_'%linkage, data_dir)