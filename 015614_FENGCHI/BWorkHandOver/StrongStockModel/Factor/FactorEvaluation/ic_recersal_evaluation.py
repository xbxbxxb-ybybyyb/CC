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

out_path = f'{root_path}external_data/moon_reversal/'

# shutil.copytree(out_path,out_path[:-1]+'_20210703cp/')
if not os.path.exists(out_path):
    os.mkdir(out_path)
eval_path = '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/ic_reversal/'
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

import pandas as pd
eval_pos = pd.read_pickle(f'/data/group/800442/800319/junkData/StrongStock/external_data/moon_v2/ic_t.pkl')
eval_reversal = pd.read_pickle(f'/data/group/800442/800319/junkData/StrongStock/external_data/moon_reversal/ic_t.pkl')

pos_top200 = eval_pos.loc[20160603].apply(abs).sort_values(ascending=False).index.tolist()[:200]
reversal_top200 = eval_reversal.loc[20160603].sort_values(ascending=False).index.tolist()[:500]

len(set(reversal_top200).intersection(set(pos_top200)))

# for each in items:
#     res1 = pd.read_pickle(f'{root_path}external_data/moon_v2/{each}.pkl')
#     res2 = pd.read_pickle(f'{out_path}{each}.pkl').loc[:20211031]
#     if not np.isclose((res1.fillna(0) - res2.fillna(0)).values.max(),0):
#         print(each,'Wrong')
