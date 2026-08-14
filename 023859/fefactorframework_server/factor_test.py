# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from xquant.compute.aimr import AIMR
import json

def index2str(index_arr):
    res = ''
    for index in index_arr:
        res+='%d;'%(index)
    return res[:-1]

def update(file_path, override, dock_num, index_arr, what_to_do, s_xx, scene):
    num_arr = np.array(range(len(index_arr)))
    group_arr = num_arr % dock_num
    param_list = []
    for i in range(dock_num):
        dock_index_arr = index_arr[num_arr[group_arr==i]]
        index_str = index2str(dock_index_arr)
        if scene is None:
            param_list.append('%s-%d-%s-%s'%(file_path, override, s_xx, index_str))
        else:
            param_list.append('%s-%s-%d-%s-%s' % (scene, file_path, override, s_xx, index_str))

    print("start", 'tot_factor_num:%d' % (len(index_arr)))
    print(param_list)
    params = {"parallel_list": param_list,
              "tag": "xquant", "cpu": 1, "gpu": 0, "memory": 5240}
    AIMR.runTasks(what_to_do, json.dumps(params))
    return param_list

test_date ='all'  #20230323#'all'
s_xx = '931'
scene = None   #None or other

file_path = '/data/user/023859/factor_zooZZ/all_factor_inf.xlsx'
override = True
dock_num = 100
what_to_do = 'factor_test_aimr.py'
df = pd.read_excel(file_path)
df['pre_check'] = df['factor_name'].apply(lambda x:pd.read_pickle('/data/user/023859/factor_zooZZ/all_factor_check/%s/%s.pkl'%(s_xx if s_xx!='930' else '931', x))['预检测']=='pass')
df = df[df['pre_check']]
#--------------------------------------------
dock_num=min(dock_num,len(df))
index_arr = np.array(df.index)
param_list = update(file_path, override, dock_num, index_arr, what_to_do, s_xx, scene)
