# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime
from xquant.compute.aimr import AIMR
import json

def index2str(index_arr):
    res = ''
    for index in index_arr:
        res+='%d;'%(index)
    return res[:-1]

def update(start_date, end_date, file_path, override, dock_num, index_arr, what_to_do, scene):
    num_arr = np.array(range(len(index_arr)))
    group_arr = num_arr % dock_num
    param_list = []
    for i in range(dock_num):
        dock_index_arr = index_arr[num_arr[group_arr==i]]
        index_str = index2str(dock_index_arr)
        if scene is None:
            param_list.append('%s-%d-%d-%d-%s'%(file_path, start_date, end_date, override, index_str))
        else:
            param_list.append('%s-%s-%d-%d-%d-%s' % (scene, file_path, start_date, end_date, override, index_str))

    print("start", 'tot_factor_num:%d' % (len(index_arr)))
    print(param_list)
    params = {"parallel_list": param_list,
              "tag": "xquant", "cpu": 1, "gpu": 0, "memory": 5240}
    AIMR.runTasks(what_to_do, json.dumps(params))
    return param_list

# start_date, end_date = 20220801, 20230731
start_date, end_date = 20230801, 20250430

today=datetime.date.today()
today_weekday=today.weekday()
if today_weekday>=3:
    last_thursday=today-datetime.timedelta(days=today_weekday-3)
else:
    last_thursday = today - datetime.timedelta(days=today_weekday +7- 3)
test_date = last_thursday.strftime('%Y%m%d')
print(f'test_date:{test_date}')
# test_date = 'all'
scene = None   #None or other

file_path = '/data/user/023859/factor_zooF/all_factor_inf.xlsx'
override = True
dock_num = 100
what_to_do = 'factor_test_aimr.py'
df = pd.read_excel(file_path)
df = df[df['提交时间']==int(test_date)] if test_date!='all' else df
df['pre_check'] = df['factor_name'].apply(lambda x:pd.read_pickle('/data/user/023859/factor_zooF/all_factor_check/%s.pkl'%(x))['预检测']=='pass')
df = df[df['pre_check']]
#--------------------------------------------
dock_num=min(dock_num,len(df))
index_arr = np.array(df.index)
param_list = update(start_date, end_date, file_path, override, dock_num, index_arr, what_to_do, scene)
