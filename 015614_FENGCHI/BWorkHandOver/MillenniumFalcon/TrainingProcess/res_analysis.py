# @Time : 2021/11/8 9:58
# @Author : Zhichen Lu
# @File : res_analysis.py
import pandas as pd
import os
from tqdm import tqdm

res_path = '/data/group/800442/800319/MillenniumFalcon/ExpResPreNormalize/eval_res/'

file_list = sorted(os.listdir(f'{res_path}daily_ic/'))

daily_ic = {}
periodicaly_res = {}
all_res = []

for each in tqdm(file_list):
    tag = each.replace('.pkl', '')
    daily_ic[tag] = pd.read_pickle(f'{res_path}daily_ic/{each}')
    period = pd.read_pickle(f'{res_path}periodically_eval/{each}')
    periodicaly_res[tag] = period['corr']
    temp_res = pd.read_pickle(f'{res_path}data/{each}')
    temp_res = temp_res.rename(columns={'actual_label': f'{tag}_label', 'prediction': f'{tag}_pred'})
    all_res.append(temp_res)

daily_ic = pd.DataFrame(daily_ic)
periodicaly_res = pd.DataFrame(periodicaly_res)
all_res = pd.concat(all_res, axis=1)

date_list = all_res.index.levels[0].tolist()

daily_ic_corr = {}
for date in tqdm(date_list):
    daily_ic_corr[date] = all_res.loc[date].corr()
daily_ic_corr = pd.Panel(daily_ic_corr)
year_map = {
    year: list(filter(lambda x: x // 10000, date_list)) for year in range(2015, 2022)
}
year_map['all'] = date_list
label_col_list = list(filter(lambda x: x.endswith('1_label') and '1' in x, all_res.columns.tolist()))
pred_col_list = list(filter(lambda x: x.endswith('_pred'), all_res.columns.tolist()))

daily_ic_corr_mean = {
    year: daily_ic_corr.loc[year_map[year], pred_col_list, label_col_list].mean(axis=0) for year in year_map
}
# daily_ic_corr_mean['all'] =daily_ic_corr.loc[:,pred_col_list,label_col_list].mean(axis=0)

with pd.ExcelWriter(f'{res_path}日均IC矩阵_1d.xlsx') as writer:
    for each in daily_ic_corr_mean:
        daily_ic_corr_mean[each].to_excel(writer, sheet_name=str(each))
writer.close()

from dataApi.sendInfo import send_file

send_file(['015664'], f'{res_path}日均IC矩阵_1d.xlsx')

res = daily_ic_corr_mean.loc[pred_col_list, label_col_list]

