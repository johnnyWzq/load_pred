# -*- coding: utf-8 -*-
"""
Created on Tue May  8 15:34:19 2018

@author: wuzhiqiang
"""

import pandas as pd
import numpy as np 
from dateutil import parser
import os
from functools import reduce
import re

df = pd.DataFrame(np.array([[0, 1], [0, 10], [0, 100], [4, 100]]),
                   columns=['a', 'b'])
f = df.quantile(.1, 0)
print(f)
cols = ['a', 'b', 'c', 'd']
p = list(map(lambda x:y+x, cols))
print(p)
c = reduce(lambda x, y: x+y, p)
print(c)

file = 'L_P_CAAHAA000102_2017.csv'
r = re.match(r'(\w\_\w)_(\w+)_(\d+\.csv)', file)
print(r.group(2))

s = np.arange(20).reshape((10, -1))
df = pd.DataFrame(s)
df = df.append(pd.DataFrame([[12, 23]]))
df = df[(df[1] - df[0]) < 4]
df[2] = df[1]-df[0]
a=df.loc[0][1]
print(df)

t1 = '10:12:34'
t2 = '12:45:10'
t3=[t1,t2]
t4=[]
for t in t3:
    t4.append(fun(t))

fun =  lambda x:parser.parse(x)


tt1 = fun(t1)
tt2 = fun(t2)
print(tt1, tt2)
#print((tt2-tt1).hours)
#print((tt2-tt1).minutes)
print((tt2-tt1).seconds)
 
import datetime
def time_list(time1, time2):
    time_list = []
    while time1 <= time2:
        #time_list.append(datetime.datetime.strptime(time1.strftime('%H:%M:%S'), '%H:%M:%S'))
        time_list.append(time1.strftime('%H:%M:%S'))
        time1 += datetime.timedelta(minutes=1)
    print(time_list)
    return time_list

t = time_list(tt1, tt2)
