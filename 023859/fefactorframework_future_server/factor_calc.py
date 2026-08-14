# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from xquant.compute.aimr import AIMR
import json
import datetime

def index2str(index_arr):
    res = ''
    for index in index_arr:
        res+='%d;'%(index)
    return res[:-1]

def update(start_date, end_date, file_path, override, dock_num, index_arr, what_to_do, s_xx, scene):
    num_arr = np.array(range(len(index_arr)))
    group_arr = num_arr % dock_num
    param_list = []
    for i in range(dock_num):
        dock_index_arr = index_arr[num_arr[group_arr==i]]
        index_str = index2str(dock_index_arr)
        if scene is None:
            param_list.append('%s-%d-%d-%d-%s-%s'%(file_path, start_date, end_date, override, s_xx, index_str))
        else:
            param_list.append('%s-%s-%d-%d-%d-%s-%s' % (scene, file_path, start_date, end_date, override, s_xx, index_str))

    print("start", 'tot_factor_num:%d' % (len(index_arr)))
    print(param_list)
    params = {"parallel_list": param_list,
              "tag": "xquant", "cpu": 1, "gpu": 0, "memory": 5240}
    AIMR.runTasks(what_to_do, json.dumps(params))
    return param_list

today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
last_thursday=last_thursday.strftime('%Y%m%d')
#last_thursday='20241205'
print('入库时间为{}'.format(last_thursday))

start_date, end_date = 20220801, 20250430

test_date ='all'  #20230323#'all'
s_xx = '931'
scene = None   #None or other

file_path = f'/data/user/023859/factor_zooF/all_factor_inf_{last_thursday}.xlsx'
override = True
dock_num = 100
what_to_do = 'factor_calc_aimr.py'
df = pd.read_excel(file_path)
print('入库数量：',len(df),list(df['factor_name']))
#--------------------------------------------
dock_num=min(dock_num,len(df))
index_arr = np.array(df.index)
param_list = update(start_date, end_date, file_path, override, dock_num, index_arr, what_to_do, s_xx, scene)
