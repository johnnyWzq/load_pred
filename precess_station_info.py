# -*- coding: utf-8 -*-
"""
Created on Thu May 17 18:17:39 2018

@author: wuzhiqiang
"""
import pandas as pd
import os

def merge_station_info(stations0, stations1):
    #对每一张表进行转换
    #stations_info_temp
    print('transfering stations_info_temp data...')
    stations = []#pd.DataFrame(columns=['city_code', 'station_id', 'station_name', 'service_type'])
    for data in stations0.values():
        df = data[['station_id', 'city_code']]
        data = data.drop(['city_code', 'station_id', 'station_name'], axis=1)
        service_type = []
        for col in data.columns:
            temp = data[data[col] == 1][[col]]#代表服务类型的列值等于1
            temp = temp.rename(columns={col: 'service_type'})
            temp['service_type'] = col#将此列等于1的值替换为服务类型
            service_type.append(temp)
        service_type = pd.concat(tuple(service_type))
        st_gp = service_type.groupby(service_type.index)
        s = {}
        for i in st_gp.groups:
            df0 = st_gp.get_group(i)
            if len(df0) <= 1:
                continue
            s[i] = ''
            for cnt in range(len(df0)):
                s[i] = s[i] + '-' + df0.iloc[cnt][0]#获取所有服务类型
        for k, v in s.items():#将收集的服务类型赋给对应的场站index
            service_type.loc[k, 'service_type'] = v
        service_type = service_type.reset_index(drop=False)
        service_type = service_type.drop_duplicates('index')
        service_type = service_type.set_index('index')
        df = df.merge(service_type, left_index=True, right_index=True, sort=True)
        stations.append(df)
    stations = pd.concat(tuple(stations))
        
    #processed_charger_info
    print('transfering processed_charger_info data...')
    stations1 = stations1.drop(['city_code', 'service_type'], axis=1)
    stations1 = stations1.merge(stations, on='station_id', how='inner')
    print(len(stations1))
    stations1 = stations1.drop_duplicates('charger_id')
    print(len(stations1))
    #stations1['service_type'] = stations1['service_type'].fillna('机场')
    #temp = stations1['city_code']
    #temp[stations1['service_type'] == '机场'] = '机场'#将service_type为机场的城市名改为机场
    #stations1['city_code'] = temp
    
    stations = []
    stations_gp = stations1.groupby('station_id')
    for i in stations_gp.groups:
        df = stations_gp.get_group(i)
        power_total = df['power'].sum()
        ac_charger_num = len(df['charger_type'][df['charger_type'] == '交流'])
        dc_charger_num = len(df['charger_type'][df['charger_type'] == '直流'])
        df = df.head(1)
        df['operation_time'] = df.iloc[0]['operation_time'][:11]
        df['power'] = power_total
        df['ac_charger_num'] = ac_charger_num
        df['dc_charger_num'] = dc_charger_num
        df = df.drop(['Unnamed: 0', 'charger_id', 'productor', 'charger_type',
                      'cp_service_type', 'station_no'], axis=1)
        stations.append(df)
    stations = pd.concat(tuple(stations))
    return stations
            
            
    
if  __name__ == '__main__':
    
    data_dir = os.path.join(os.path.abspath('.'), 'processed_data')
    stations0 = pd.read_excel(os.path.join(data_dir, 'station_info_temp.xlsx'),
                              sheet_name=None)
    stations1 = pd.read_csv(os.path.join(data_dir, 'processed_charger_info.csv'),
                            error_bad_lines=False,  encoding='gb18030')
    stations_info = merge_station_info(stations0, stations1)
    stations_info.to_excel(os.path.join(data_dir, 'stations_info.xlsx'))
