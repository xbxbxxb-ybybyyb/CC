# @Time : 2021/6/3 0:16
# @Author : Zhichen Lu
# @File : ret_evaluation.py

import pandas as pd
import os
from dataApi.tradeDate import get_pre_trade_date
from tqdm import tqdm
from conf.path_config import root_path

out_path = f'{root_path}external_data/moon_v2/'
if not os.path.exists(out_path):
    os.mkdir(out_path)
eval_path = '/data/group/800319/HFfactor/RealTimeFixRollRobust/ret_month/'
ic_path = '/data/group/800319/HFfactor/RealTimeFixRollRobust/ic_month/'
factor_list = os.listdir(eval_path)
res = {}
for factor_name in tqdm(factor_list):
    temp_res = pd.read_pickle(f'{eval_path}{factor_name}')
    low = pd.Series(temp_res['ret_low'][4],index=temp_res['end_dates']).rolling(12).mean()
    high = pd.Series(temp_res['ret_high'][4],index=temp_res['end_dates']).rolling(12).mean()
    res[factor_name] = pd.DataFrame({'high':high,'low':low}).max(axis=1).sort_values(ascending=False)

res = pd.DataFrame(res)[12:]
pd.to_pickle(res,f'{out_path}top_ret.pkl')

