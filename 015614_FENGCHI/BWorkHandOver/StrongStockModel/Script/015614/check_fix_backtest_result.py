# coding: utf-8
# Author：fengchi863
# Date ：2020/8/13 9:36

import os

import pandas as pd

from StrongStockModel.conf.path_config import root_path

# parse param
holding_day = 1

# backtest_result_path = '/data/user/hanxu/TrueSendStrategy/Fix_test_strong/'
backtest_result_path = root_path + 'factor_test_result/ALL/'
file_name_list = os.listdir(backtest_result_path)
res = pd.DataFrame()
ic_dict = {}
top_ret_mean_dict = {}
top_ret_pos_dict = {}
top_ret_pl_dict = {}
period_sign_num_dict = {}
top_ret_sum_dict = {}


for file_name in file_name_list:
    factor_name = file_name[:-5]
    print('统计中...%s' % factor_name)
    with pd.ExcelFile(backtest_result_path + file_name) as reader:
        sheet_name_list = reader.sheet_names
        df = reader.parse(sheet_name='ic', header=0)
        ic = df[holding_day][0]  # 2014-2016
        ic_dict.update({factor_name: ic})

        df = reader.parse(sheet_name='period_sign_num', header=0)
        period_sign_num = df[0.9][0]
        period_sign_num_dict.update({factor_name: period_sign_num})

        df = reader.parse(sheet_name='top_ret_sum_0.9', header=0)
        top_ret_sum = df[holding_day][0]
        top_ret_sum_dict.update({factor_name: top_ret_sum})

        df = reader.parse(sheet_name='top_ret_mean_0.9', header=0)
        top_ret_mean = df[holding_day][0]
        top_ret_mean_dict.update({factor_name: top_ret_mean})

        df = reader.parse(sheet_name='top_ret_pos_0.9', header=0)
        top_ret_pos = df[holding_day][0]
        top_ret_pos_dict.update({factor_name: top_ret_pos})

        df = reader.parse(sheet_name='top_ret_pl_0.9', header=0)
        top_ret_pl = df[holding_day][0]
        top_ret_pl_dict.update({factor_name: top_ret_pl})

tmp_df1 = pd.DataFrame(ic_dict, index=['ic']).T
tmp_df2 = pd.DataFrame(period_sign_num_dict, index=['period_sign_num']).T
tmp_df3 = pd.DataFrame(top_ret_sum_dict, index=['top_ret_sum']).T
tmp_df4 = pd.DataFrame(top_ret_mean_dict, index=['top_ret_mean']).T
tmp_df5 = pd.DataFrame(top_ret_pos_dict, index=['top_ret_pos']).T
tmp_df6 = pd.DataFrame(top_ret_pl_dict, index=['top_ret_pl']).T

res = pd.concat([tmp_df1, tmp_df2, tmp_df3, tmp_df4, tmp_df5, tmp_df6],
                axis=1)
res['abs_ic'] = res['ic'].map(abs)

print('统计完成')
res_df = res.sort_values(['abs_ic'], ascending=False)
res_df.to_excel(root_path + 'stats_fix.xlsx')
# res_df['abs_ic_mean'].to_pickle(fix_factor_true_send_evaluation_path)
