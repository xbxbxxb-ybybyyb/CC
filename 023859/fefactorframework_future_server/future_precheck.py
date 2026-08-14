# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import IO
from xquant.compute.aimr import AIMR
import json
import sys
sys.path.append("/data/user/023859/ProjectF/factor_lib/")

file_path='/dfs/user/023859/factor_zooF/all_factor_inf.xlsx'
override = True
s_xx = '931'

#test_date = 'all'
test_date = 20250605
dock_num = 100
df = pd.read_excel(file_path)

count=df['factor_name'].value_counts().head()
assert count.max()==1
#-----------filter factor--------------------
df = df[~df['factor_type'].str.contains('\[')]
df = df[df['提交时间']==int(test_date)] if test_date!='all' else df
#--------------------------------------------


def index2str(index_arr):
    res = ''
    for index in index_arr:
        res+='%d;'%(index)
    return res[:-1]
def update(file_path, dock_num, index_arr):
    num_arr = np.array(range(len(index_arr)))
    group_arr = num_arr % dock_num
    param_list = []
    for i in range(dock_num):
        dock_index_arr = index_arr[num_arr[group_arr==i]]
        index_str = index2str(dock_index_arr)
        param_list.append('%s-%s-%d-%s'%(file_path, s_xx, int(override), index_str))

    print("start", 'tot_factor_num:%d' % (len(index_arr)))
    print(param_list)
    params = {"parallel_list": param_list,
              "tag": "xquant", "cpu": 1, "gpu": 0, "memory": 50240}
    AIMR.runTasks('future_precheck_aimr.py', json.dumps(params))
    return param_list

dock_num = min(dock_num, len(df))
index_arr = np.array(df.index)
param_list = update(file_path, dock_num, index_arr)

df['pass']=df['factor_name'].apply(lambda x:pd.read_pickle('/data/user/023859/factor_zooF/all_factor_check/%s/%s.pkl' % (s_xx, x))['pass'])
df['check_inf']=df['factor_name'].apply(lambda x:pd.read_pickle('/data/user/023859/factor_zooF/all_factor_check/%s/%s.pkl' % (s_xx, x))['check_inf'])
df1=df[~df['pass']]
print(df1)


