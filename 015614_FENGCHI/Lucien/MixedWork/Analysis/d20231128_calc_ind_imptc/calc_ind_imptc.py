# coding: utf-8
# Author：fengchi863
# Date ：2023/11/28 16:20

import pandas as pd
import numpy as np
import xgboost as xgb

# 找出哪些因子是行业因子，获得他们的list
ind_factor_list = pd.read_excel('/data/group/800463/sunss/europa/20231102/factor_bank_inf_Industry.xlsx')['factor_name'].tolist()

factor_score = pd.read_excel('/data/user/015614/factor/dig_TallTrans1_20231130100023/check_res_tot_europa_20231123.xlsx')
factor_score = factor_score.query(f'factor_name in {ind_factor_list}')

imptc_df = pd.DataFrame()
period_list = ['period1', 'period2', 'period3', 'period4', 'period5']
for period in period_list:
    for factor_select in ['fsv8', 'fsv10', 'fsv11', 'fsrs']:
        if period == 'period1':
            from Zeus.Europa.v4_0_4.path_conf import *
        elif period == 'period2':
            from Zeus.Europa.v4_0_5.path_conf import *
        elif period == 'period3':
            from Zeus.Europa.v4_0_6.path_conf import *
        elif period == 'period4':
            from Zeus.Europa.v4_0_9.path_conf import *
        elif period == 'period5':
            from Zeus.Europa.v4_0_11.path_conf import *

        if factor_select.startswith('fsv'):
            factor_df = pd.read_excel(eval(f'xgb_imptc_pct_{factor_select}_{period}_fpath'), index_col=0).set_index('factor_name')
            # 获取排名序列
            factor_df['imptc_rank'] = factor_df['count'].rank(method='min', ascending=False)
        else:
            factor_df = pd.read_excel(eval(f'fsrs_imptc_pct_{period}_fpath')).set_index('factor_name')
            factor_df['imptc_rank'] = factor_df['select_num'].rank(method='min', ascending=False)

        imptc_df.loc[f'{period}_{factor_select}', '均值'] = factor_df.loc[ind_factor_list, 'imptc_rank'].mean()
        imptc_df.loc[f'{period}_{factor_select}', '中位值'] = factor_df.loc[ind_factor_list, 'imptc_rank'].median()
        imptc_df.loc[f'{period}_{factor_select}', '最重要'] = factor_df.loc[ind_factor_list, 'imptc_rank'].min()
        imptc_df.loc[f'{period}_{factor_select}', '最不重要'] = factor_df.loc[ind_factor_list, 'imptc_rank'].max()
        imptc_df.loc[f'{period}_{factor_select}', '参与排名因子总数'] = len(factor_df) - factor_df['imptc_rank'].isna().sum()
        imptc_df.loc[f'{period}_{factor_select}', '详细'] = str(factor_df.loc[ind_factor_list, 'imptc_rank'].sort_values().to_dict())

for period in period_list:
    for factor_select in ['fsv8', 'fsv10', 'fsv11', 'fsrs']:
        print(f'{period}_{factor_select}')
        if period == 'period1':
            version = 'v4_0_4'
        elif period == 'period2':
            version = 'v4_0_5'
        elif period == 'period3':
            version = 'v4_0_6'
        elif period == 'period4':
            version = 'v4_0_9'
        elif period == 'period5':
            version = 'v4_0_11'

        model_file_fpath = f'/data/user/015614/Zeus/pred/Europa/{version}/{factor_select}_pct_AllXgbRegModel/model/{period}/seed_0/XgbRegModel.pkl'
        factor_list = f'/data/user/015614/Zeus/pred/Europa/{version}/{factor_select}_pct_AllXgbRegModel/model/{period}/seed_0/_factorName.json'
        factor_list = pd.read_json(factor_list)[0].tolist()
        model = xgb.Booster(model_file=model_file_fpath)
        imptc_list = model.get_fscore()
        model_imptc = pd.Series(list(imptc_list.values()), index=factor_list)
        model_imptc = model_imptc.rank(method='min', ascending=False)
        imptc_df.loc[f'{period}_{factor_select}', '模型均值'] = model_imptc.reindex(ind_factor_list).mean()
        imptc_df.loc[f'{period}_{factor_select}', '模型中位值'] = model_imptc.reindex(ind_factor_list).median()
        imptc_df.loc[f'{period}_{factor_select}', '模型最重要'] = model_imptc.reindex(ind_factor_list).min()
        imptc_df.loc[f'{period}_{factor_select}', '模型最不重要'] = model_imptc.reindex(ind_factor_list).max()
        imptc_df.loc[f'{period}_{factor_select}', '模型参与排名因子总数'] = len(model_imptc) - model_imptc.isna().sum()
        imptc_df.loc[f'{period}_{factor_select}', '模型详细'] = str(model_imptc.reindex(ind_factor_list).sort_values().to_dict())

from dataApi.sendInfo import send_file
send_file(imptc_df)
send_file(factor_score)





