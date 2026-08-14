# @Time : 2021/3/29 17:15
# @Author : Zhichen Lu
# @File : dailyFactorEvalAnalysis.py
import pandas as pd
import os
from tqdm import tqdm
eval_res_path =  '/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2/'

eval_res_list = os.listdir(eval_res_path)
windows_keys = {'year':2,'half_year':4,'quater':8,'month':24,'all':1}
res = {}
for each in tqdm(eval_res_list):
    factor_name = each.replace('.pkl','')
    temp_res = pd.read_pickle(eval_res_path+each)
    stat = pd.Series()

    for items in ['ic_c','ic_d']:
        for freq in temp_res[items]:
            stat = stat.append(temp_res[items][freq].rolling(windows_keys[freq],min_periods=1).mean().rename(index={x:f'{items}_{freq}_{x}' for x in temp_res[items][freq].index}))

    for items in ['ic_c_fix','ic_d_fix']:
        for freq in temp_res[items]:
            temp_freq_res = temp_res[items][freq].rolling(windows_keys[freq],min_periods=1).mean().stack(dropna=False)
            temp_freq_res.index = [f'{items}_{freq}_{tuple(x)[0]}_{tuple(x)[1]}' for x in temp_freq_res.index]
            stat = stat.append(temp_freq_res)

    res[factor_name] = stat

res = pd.DataFrame(res).T

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/DailyFactotrFixEvaluation2_res/结果汇总.xlsx') as writer:
    res.to_excel(writer,'ic')
    abs(res).to_excel(writer,'ic_abs')
writer.close()
res = abs(res)


col = list(filter(lambda x : 'half' in x,res.columns.tolist()))

check_daily = res[col]

from conf.path_config import root_path
fix_res = {}
factor_evaluation = pd.read_pickle(root_path+'external_data/ic_half.pkl')
factor_evaluation = pd.DataFrame(factor_evaluation)

fix_ic_d = abs(factor_evaluation.loc['ic_half_d'])
fix_ic_c = abs(factor_evaluation.loc['ic_half_c'])

fix_ic_c.quantile(0.8,axis=1)

check = pd.read_pickle(root_path+'external_data/ic_all.pkl')
check = pd.DataFrame(check).T
abs(check).quantile(0.8)

abs(check['ic_all_c']).sort_values(ascending=False).iloc[200:400].mean(),abs(check['ic_all_d']).sort_values(ascending=False).iloc[200:400].mean()
abs(check_daily['ic_c_all_all']).sort_values(ascending=False).iloc[:200].mean(),abs(check_daily['ic_d_all_all']).sort_values(ascending=False).iloc[:200].mean()

