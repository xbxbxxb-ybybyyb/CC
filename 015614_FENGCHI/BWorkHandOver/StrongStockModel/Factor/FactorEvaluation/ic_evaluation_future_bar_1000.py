# @Time : 2021/6/1 18:41
# @Author : Zhichen Lu
# @File : ic_evaluation.py
import pandas as pd
import os
from dataApi.tradeDate import get_pre_trade_date
from tqdm import tqdm
from StrongStockModel.conf.path_config import root_path
import numpy as np
import shutil

# bar_num = 1
def future_bar_eval(bar_num):
    out_path = f'{root_path}external_data/FutureBarBy30Min/Future_{bar_num}_bar_1000_v2/'
    eval_path =  f'/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/ic_future_{bar_num}_bar_only_to_1000_v2/'

    # shutil.copytree(out_path,out_path[:-1]+'_20210703cp/')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    factor_list = os.listdir(eval_path)
    res = {}
    for factor_name in tqdm(factor_list):
        temp_res = pd.read_pickle(f'{eval_path}{factor_name}')
        _ = temp_res.pop('factor_sample')
        _ = temp_res.pop('start_dates')
        temp_res = pd.DataFrame(temp_res).set_index('end_dates')
        temp_res.index = temp_res.index.map(lambda x : get_pre_trade_date(x,-3))
        res[factor_name] = temp_res.stack().swaplevel(0,1)



    res = pd.DataFrame(res)

    res = res.loc[[ 'ic_dtc', 'ic_dt', 'ic_tc', 'ic_dc', 'ic_d', 'ic_t', 'ic_c']]
    items = [ 'ic_dtc', 'ic_dt', 'ic_tc', 'ic_dc', 'ic_d', 'ic_t', 'ic_c']
    for each in items:
        temp = res.loc[each]
        temp[temp>=1] = 0
        temp[temp<=-1] = 0
        pd.to_pickle(temp,f'{out_path}{each}.pkl')

for b_num in tqdm(list(range(1,7))):
    future_bar_eval(b_num)

ic_c,ic_d,ic_c_every_bar,ic_d_every_bar = {},{},{},{}

for b_num in range(1,8):
    if b_num==7:
        out_path_1000 = f'{root_path}external_data/moon_v2/'
        out_path_everybar = f'{root_path}external_data/moon_v2/'
    else:
        out_path_1000 = f'{root_path}external_data/FutureBarBy30Min/Future_{b_num}_bar_1000/'
        out_path_everybar = f'{root_path}external_data/FutureBarBy30Min/Future_{b_num}_bar/'
    ic_c[b_num] = abs(pd.read_pickle(f'{out_path_1000}ic_c.pkl')).mean(axis=1)
    ic_d[b_num] = abs(pd.read_pickle(f'{out_path_1000}ic_d.pkl')).mean(axis=1)

    ic_c_every_bar[b_num] = abs(pd.read_pickle(f'{out_path_everybar}ic_c.pkl')).mean(axis=1)
    ic_d_every_bar[b_num] = abs(pd.read_pickle(f'{out_path_everybar}ic_d.pkl')).mean(axis=1)

ic_c = pd.DataFrame(ic_c)
ic_d = pd.DataFrame(ic_d)

ic_d_every_bar = pd.DataFrame(ic_d_every_bar)
ic_c_every_bar = pd.DataFrame(ic_c_every_bar)

check1 = abs(pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/external_data/FutureBarBy30Min/Future_1_bar_1000/ic_c.pkl')).mean(axis=1)
check2 = abs(pd.read_pickle('/data/group/800442/800319/junkData/StrongStock/external_data/FutureBarBy30Min/Future_1_bar_1000_v2/ic_c.pkl')).mean(axis=1)
# for each in items:
#     res1 = pd.read_pickle(f'{root_path}external_data/moon_v2/{each}.pkl')
#     res2 = pd.read_pickle(f'{out_path}{each}.pkl').loc[:20211031]
#     if not np.isclose((res1.fillna(0) - res2.fillna(0)).values.max(),0):
#         print(each,'Wrong')
