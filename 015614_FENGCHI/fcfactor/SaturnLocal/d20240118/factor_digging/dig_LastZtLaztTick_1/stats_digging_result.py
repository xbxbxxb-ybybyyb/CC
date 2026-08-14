# coding: utf-8
# Author：fengchi863
# Date ：2023/4/18 9:20

import os
import pandas as pd
import json
import requests
from scipy import stats
import time
from SaturnLocal.TestTool.project_2_factor_test_origin import pj2FactorTest


def save_dict2xls(data: dict, path=None, filename=None, verbose=True):
    os.makedirs(path, exist_ok=True)
    with pd.ExcelWriter(path + filename) as writer:
        for each in data:
            data[each].to_excel(writer, each)
    if verbose:
        print(f'{filename} has been saved in {path + filename}')

start_date = 20160101
end_date = 20191231
sft = pj2FactorTest(start_date, end_date)

root_path = '/data/user/015614/factor/dig_20240118_Saturn_LastZtLastTick_1_20240123112747/'
note = root_path.split('_')[-1][:-1] + '_part1'
file_list = os.listdir(root_path)
xlsx_list = list(filter(lambda x: x.endswith('.xlsx') and not x.startswith('因子'), sorted(file_list)))[:]
factor_fpath_list = list(filter(lambda x: x.endswith('.pkl'), sorted(file_list)))[:]
res_list = []
for xlsx in xlsx_list:
    tmp = pd.read_excel(root_path + xlsx, index_col=0)
    res_list.append(tmp)
res_df = pd.concat(res_list, axis=0)

# factor_df_list = []
# for factor_fpath in factor_fpath_list:
#     if factor_fpath != 'factor.pkl':
#         tmp = pd.read_pickle(root_path + factor_fpath)
#         factor_df_list.append(tmp)
#
# all_factor = pd.concat(factor_df_list, axis=1)

factor_df_list = []
for factor_fpath in factor_fpath_list:
    if factor_fpath != 'factor.pkl':
        tmp = pd.read_pickle(root_path + factor_fpath)
        tmp = tmp.reindex(index=sft.basic_df.index)
        factor_df_list.append(tmp)

week_submit_date = 20240125
week_root_path = f'/data/user/015614/factor/d{week_submit_date}_Saturn/'
week_submit_factor_fpath_list = os.listdir(week_root_path)
for factor_fpath in week_submit_factor_fpath_list:
    if factor_fpath.endswith('h5'):
        tmp = pd.read_hdf(week_root_path + factor_fpath)
        tmp = tmp.reindex(index=sft.basic_df.index)
        factor_df_list.append(tmp)

print(f'开始拼接{len(factor_df_list)}个因子')
all_factor = pd.concat(factor_df_list, axis=1)
print('拼接完成')

res_df['highest_corr'] = res_df['high_corr_factor_corr'].map(lambda x: float(x.split('，')[0]))
# 计算相关性
corr_res = pd.DataFrame(index=all_factor.columns.tolist(), columns=all_factor.columns.tolist())
for idx1, factor_name1 in enumerate(all_factor.columns.tolist()):
    for idx2, factor_name2 in enumerate(all_factor.columns.tolist()):
        if idx1 > idx2:
            corr_res.iloc[idx1, idx2] = stats.spearmanr(all_factor[factor_name1].fillna(0), all_factor[factor_name2].fillna(0))[0]
            corr_res.iloc[idx2, idx1] = corr_res.iloc[idx1, idx2]

# corr_res = all_factor.corr()  # 计算耗时太高，采用分批计算方案

corr_res = corr_res.applymap(abs)
for index in res_df.index:
    self_highest_corr = corr_res.loc[index.replace('/', '%')].sort_values(ascending=False)
    res_df.loc[index, 'self_high_corr'] = ','.join(self_highest_corr[self_highest_corr > 0.685].index.tolist())
    res_df.loc[index, 'self_high_factor'] = ','.join(self_highest_corr[self_highest_corr > 0.685].map(lambda x: str(round(x, 3))).tolist())

# 挑选样本
res_df2 = res_df.copy()
import operator
res_df2 = res_df2.loc[res_df2['self_high_corr'].apply(lambda x: not operator.contains(x, 'fc'))]
res_df2 = res_df2.sort_values('score', ascending=False).query('score > 12.5 & highest_corr < 0.695 & high_corr_s_num == 0')
res_df2['drop'] = 0
res_df2['commit'] = 0
while True:
    tmp_res_df = res_df2.query('drop == 0 & commit == 0')

    if len(tmp_res_df) > 0:
        name = tmp_res_df.iloc[0].name
        res_df2.loc[name, 'commit'] = 1
        for idx2 in range(1, len(tmp_res_df)):
            row = tmp_res_df.iloc[idx2]
            name2 = tmp_res_df.iloc[idx2].name
            if name in row['self_high_corr']:
                res_df2.loc[name2, 'drop'] = 1
    else:
        break

output_dict = {'score': res_df,
               'corr': corr_res,
               'filter': res_df2}
save_dict2xls(output_dict, root_path, f'因子寻优结果_{note}.xlsx')