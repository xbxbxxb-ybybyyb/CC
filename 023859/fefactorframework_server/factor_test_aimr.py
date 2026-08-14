# -*- coding: utf-8 -*-
import datetime as dt
from xfactor.factor_test.NeptuneFactorTest import FactorTest
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
override = bool(int(param_list[1]))
s_xx = param_list[2]
index_list = param_list[3].split(';')
index_list = [int(index) for index in index_list]
factor_inf = pd.read_excel(file_path)

factor_inf['start_date_in_sample'] = factor_inf.apply(lambda x: 20170101 if ('Tickfull' in x['factor_type'] or 'Tick1s' in x['factor_type'] or "Cancel" in x['factor_type']) \
    else 20170110 if ("xdb_tickfull" in x['factor_type'] or "xdb_tick1s" in x['factor_type'] or "xdb_cancel" in x['factor_type'] or 'xdb_tick1m' in x['factor_type'] or 'xdb_order1m' in x['factor_type'])\
                                                else 20160101, axis=1)
factor_inf['end_date_in_sample'] = 20191231
factor_inf['start_date_out_sample'] = 20200101
factor_inf['end_date_out_sample'] = 20201231

factor_inf = factor_inf.reindex(index_list)

factor_data_path='/data/user/023859/factor_zooZZ/all_factor'
factor_test_path='/data/user/023859/factor_zooZZ/all_factor_test/all_scene'

for index, inf in factor_inf.iterrows():
    print(index, 'in', list(factor_inf.index))
    factor_name, factor_type, factor_owner, start_date_in_sample, end_date_in_sample, start_date_out_sample, end_date_out_sample = inf['factor_name'], inf['factor_type'], inf['factor_owner'], inf['start_date_in_sample'], inf['end_date_in_sample'], inf['start_date_out_sample'], inf['end_date_out_sample']
    factor_date = inf['提交时间']
    print(factor_name, factor_type, factor_date, dt.datetime.now().strftime('%Y%m%d %H:%M:%S'))

    result_path_in_sample = '%s/%s/%d_%d/' % (factor_test_path, s_xx, start_date_in_sample, end_date_in_sample)
    result_path_out_sample = '%s/%s/%d_%d/' % (factor_test_path, s_xx, start_date_out_sample, end_date_out_sample)

    cost_path = f'/data/user/023859/factor_zooZZ/all_cost/931/{factor_name}/{factor_name}_{start_date_in_sample}_{end_date_out_sample}.pkl'

    if not os.path.exists(result_path_in_sample):
        os.makedirs(result_path_in_sample)
    if (not override) and os.path.exists(result_path_in_sample+factor_name+'.pkl'):
        print('exists and not override:',result_path+factor_name+'.pkl')
        continue
    if not os.path.exists(result_path_out_sample):
        os.makedirs(result_path_out_sample)
    if (not override) and os.path.exists(result_path_out_sample+factor_name+'.pkl'):
        print('exists and not override:',result_path+factor_name+'.pkl')
        continue

    try:
        factor_df = pd.read_hdf(factor_data_path+'/%s/%s/%s.h5'%(s_xx,factor_name, factor_name))
        factor_list_in_sample = list(pd.read_pickle(cost_path).loc[pd.to_datetime(str(start_date_in_sample)):pd.to_datetime(str(end_date_in_sample))])
        factor_list_out_sample = list(pd.read_pickle(cost_path).loc[pd.to_datetime(str(start_date_out_sample)):pd.to_datetime(str(end_date_out_sample))])
        sft_in = FactorTest(start_date_in_sample, end_date_in_sample, style_list=['Circu_Mkt'], cal_mi=False)
        sft_in.factor_test(factor_df[[factor_name]], factor_list_in_sample, result_path=result_path_in_sample, factor_corr_test=False, generate_pdf=False)
        sft_out = FactorTest(start_date_out_sample, end_date_out_sample, style_list=['Circu_Mkt'], cal_mi=False)
        sft_out.factor_test(factor_df[[factor_name]], factor_list_out_sample, result_path=result_path_out_sample, factor_corr_test=False, generate_pdf=False)
    except Exception as e:
        print(e, '!'*100)