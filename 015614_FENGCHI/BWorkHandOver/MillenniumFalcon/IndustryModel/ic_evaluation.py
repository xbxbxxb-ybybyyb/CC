# @Time : 2021/6/1 18:41
# @Author : Zhichen Lu
# @File : ic_evaluation.py
import pandas as pd
import os
from dataApi.tradeDate import get_pre_trade_date
from tqdm import tqdm
from StrongStockModel.conf.path_config import root_path
import shutil

base_path = '/data/group/800442/800319/HFfactor/DailySW2PreNormalized/'

eval_path = f'{base_path}eval_res/zscore/'
out_path = f'{base_path}eval_res_integration/zscore/'
if not os.path.exists(out_path):
    os.makedirs(out_path)
factor_list = os.listdir(eval_path)
res = {}
for factor_name in tqdm(factor_list):
    temp_res = pd.read_pickle(f'{eval_path}{factor_name}')
    temp_res = pd.DataFrame(temp_res).set_index('end_dates')
    temp_res.index = temp_res.index.map(lambda x : get_pre_trade_date(x,-3))
    res[factor_name] = temp_res.stack().swaplevel(0,1)



res = pd.DataFrame(res)

res = res.loc[[ 'ic_dc', 'ic_d','ic_c']]
items = [  'ic_dc', 'ic_d','ic_c']
for each in items:
    temp = res.loc[each]
    temp[temp>=1] = 0
    temp[temp<=-1] = 0
    pd.to_pickle(temp,f'{out_path}{each}.pkl')
