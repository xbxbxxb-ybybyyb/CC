# -*- coding: utf-8 -*-
import sys
sys.path.append("/data/user/023859/fefactorframework_future_server/")
import datetime as dt
from future_factor_test import FactorTest
import pandas as pd
import importlib
import os
import time
from xquant.compute.aimr import AIMR
from xquant.factordata import FactorData


s = FactorData()
param = AIMR.getParam()
#param = '/data/user/018107/factor_zooS/all_factor_inf.xlsx-20181001-20190930-1-930-1187;1240;1292;1345;1395;1449;1502;1555'
print(param)

param_list = param.split('-')
file_path = param_list[0]
start_date, end_date = int(param_list[1]), int(param_list[2])
override = bool(int(param_list[3]))
index_list = param_list[4].split(';')
index_list = [int(index) for index in index_list]
factor_inf = pd.read_excel(file_path)
factor_inf = factor_inf.reindex(index_list)

factor_data_path='/data/user/023859/factor_zooF/all_factor'
factor_test_path='/data/user/023859/factor_zooF/all_factor_test/all_scene'

result_path = '%s/%d_%d/'%(factor_test_path, start_date, end_date)
if not os.path.exists(result_path):
    os.makedirs(result_path)

sft = FactorTest(start_date, end_date, cal_mi=True)

for index, inf in factor_inf.iterrows():
    print(index, 'in', list(factor_inf.index))
    factor_name, factor_type, factor_owner = inf['factor_name'], inf['factor_type'], inf['factor_owner']
    factor_date = inf['提交时间']
    print(factor_name, factor_type, factor_date, dt.datetime.now().strftime('%Y%m%d %H:%M:%S'))

    if (not override) and os.path.exists(result_path+factor_name+'.pkl'):
        print('exists and not override:',result_path+factor_name+'.pkl')
        continue

    try:
        factor_df = pd.read_hdf(factor_data_path+'/%s/%s.h5'%(factor_name, factor_name))
        sft.factor_test(factor_df[[factor_name]], result_path=result_path, factor_corr_test=False, generate_pdf=False)
    except Exception as e:
        print(e, '!'*100)