# @Time : 2021/6/23 9:06
# @Author : Zhichen Lu
# @File : FactorEvaluation.py
import numpy as np
import pandas as pd
import os
from StrongStockModel.conf.path_config import root_path
from dataApi.tradeDate import get_pre_trade_date
from tqdm import tqdm

factor_path = '/arch1/group/800442/800319/HFfactor/DTC2021/result/'
eval_path = f'{root_path}external_data/factor5min_eval_revised/'
if not os.path.exists(eval_path):
    os.mkdir(eval_path)
factor_list = os.listdir(factor_path)


eval_indicator = ['ic_half_d', 'ic_half_t', 'ic_half_c', 't_dc_half_ret', 'dc_t_half_ret', 'dt_c_half_ret']

res = {}
for factor_name in tqdm(factor_list):
    eval_res = pd.read_pickle(f'{factor_path}{factor_name}')
    isFactor = True
    for k in eval_indicator:
        if k not in eval_res:
            isFactor=False
            break
    if not isFactor:
        continue
    eval_res = {x:eval_res[x] if eval_res[x].shape.__len__()==1 else np.nanmean(eval_res[x],axis=1) for x in eval_indicator+['date_half_year_ends']}
    eval_res = pd.DataFrame(eval_res).set_index('date_half_year_ends')
    eval_res.index = eval_res.index.map(lambda x : get_pre_trade_date(x,-2))
    res[int(factor_name.replace('.pkl',''))] = eval_res

res = pd.Panel(res)

for each in res.minor_axis:
    if 'ic' in each:
        abs(res.minor_xs(each)).to_pickle(f'{eval_path}{each}.pkl')
    else:
        res.minor_xs(each).to_pickle(f'{eval_path}{each}.pkl')



