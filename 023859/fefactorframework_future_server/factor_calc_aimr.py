# -*- coding: utf-8 -*-
import datetime as dt
import run_factor_demo_parallel_im
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
s_xx = param_list[4]
index_list = param_list[5].split(';')
index_list = [int(index) for index in index_list]
factor_inf = pd.read_excel(file_path)
factor_inf = factor_inf.reindex(index_list)

result_path=f'/data/user/023859/factor_zooF/all_factor/{s_xx}'
interval_res = False
basic_path = '/data/user/023859/factor_zooF/factor_lib/Basic_future_20220801_20250430.h5'

for index, inf in factor_inf.iterrows():
    factor_name, factor_type, factor_date = inf['factor_name'], inf['factor_type'], inf['提交时间']
    try:
        print(index, 'in', list(factor_inf.index))
        print(factor_name, factor_type, factor_date)

        modname = 'factor_lib.factor_%d.factor_%s' % (factor_date, factor_name)
        module = importlib.import_module(modname)
        func = getattr(module, 'factor_%s' % (factor_name)) # 因子计算函数

        factor_file_path = result_path + '%s/' % (factor_name)
        if not os.path.exists(factor_file_path):
            os.makedirs(factor_file_path)

        if interval_res == False:
            factor_file = factor_file_path + '%s.h5' % (factor_name)
        else:
            factor_file = factor_file_path + '%s_%d_%d.h5' % (factor_name, start_date, end_date)

        if (not (os.path.exists(factor_file))) or (os.path.exists(factor_file) and override):
            factor_df = run_factor_demo_parallel_im.run_factor(func, factor_name, factor_type, start_date, end_date, basic_path,
                                                  factor_file_path,
                                                  interval_res=interval_res)
            print('update %s-%s-%s' % (dt.datetime.now().strftime('%Y%m%d %H:%M:%S'), factor_name, factor_type))
        else:
            print('already exist, not update %s-%s-%s' % (
            dt.datetime.now().strftime('%Y%m%d %H:%M:%S'), factor_name, factor_type))
    except Exception as e:
        print('\nException %s-%s-%s' % (dt.datetime.now().strftime('%Y%m%d %H:%M:%S'), factor_name, factor_type))
        print(e)