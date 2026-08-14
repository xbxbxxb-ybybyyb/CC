# 检查xdb\xquant数据是否和basic_file有缺失的情形
import pandas as pd
import os
import numpy as np
from loguru import logger
import math
import copy
from multiprocessing import Pool
from xquant.factordata import FactorData
from h5data.IO import IO
jupiter_basic = pd.read_hdf('/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_20150901_20191231.h5')
saturn_basic = pd.read_hdf(
    '/data/group/800463/data/project2_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
sell_basic = pd.read_hdf(
    '/data/group/800463/data/projectS_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5')
europa_basic = pd.read_hdf(
    '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5')
metis_basic = pd.read_hdf(
    '/dfs/group/800463/data/project1_public/factor_lib_metis/Basic_metis_20160101_20191231.h5')
mimas_basic = pd.read_hdf(
    '/data/group/800463/data/project2_public/next_factor_lib/Basic_next_hf_finish_20160101_20191231.h5')
data_types = ["xdb_order",'xdb_trade',"xdb_tick1s", "xdb_tickfull",'xdb_tickex']
dic_basic = {'jupiter':jupiter_basic,
             'europa':europa_basic,
             'sell_basic':sell_basic,
             'saturn_basic':saturn_basic,
             'metis':metis_basic,
             'mimas':mimas_basic
             }
dic_strategy_path = {'jupiter':'europa_jupiter',
             'europa':'europa_jupiter',
             'sell_basic':'saturn_sell',
             'saturn_basic':'saturn_sell',
             'metis':'metis',
             'mimas':'mimas'
             }
start = '20160101'
end = '20191231'
base_path = "/dfs/group/800463/data/xdb_data_lag3/"
res = {}
for strategy in dic_basic:
    print(strategy)
    basic_strategy = dic_basic[strategy].loc[pd.Timestamp(start):pd.Timestamp(end)]
    date_list = list(set(basic_strategy.index.get_level_values(0)))
    date_list = [i.strftime('%Y%m%d') for i in date_list ]
    print('date_list length = {}'.format(len(date_list)))
    for data_type in data_types:
        path = base_path + dic_strategy_path[strategy] + '/' + data_type + '/'
        file_list = [x.replace('.pkl','') for x in list(os.listdir(path))]
        res_i = list(set(date_list) - set(file_list))
        res_i.sort()
        if data_type in ['xdb_tick1s','xdb_tickfull']:
            res_i = [x for x in res_i if int(x) >= 20170110]
        res[strategy + '_' + data_type] = res_i





