# coding: utf-8
# Author：fengchi863
# Date ：2022/11/16 15:45

import pandas as pd

root_path = '/data/user/015614/shared/backtest_result/20221120回测结果_Europa_fac_20221116三个区间上回测结果汇总/'

period1_test = '20191002~20200630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period2_test = '20200401~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period3_test = '20201001~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221120.xlsx'
period1_fit = '20200701~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'
period2_fit = '20210101~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'
period3_fit = '20210701~20211231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221121.xlsx'

bt_res_fpath_list = [period1_test, period2_test, period3_test, period1_fit, period2_fit, period3_fit]
bt_res_name = ['period1_test', 'period2_test', 'period3_test', 'period1_fit', 'period2_fit', 'period3_fit']

#%% 第二块
new_root_path = '/data/user/015614/shared/backtest_result/20221124回测结果_Europa_fac_20221116三个区间上回测结果汇总_o2ul&FSV1/'
new_period1_test = '20191002~20200630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221124.xlsx'
new_period2_test = '20200401~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221124.xlsx'
new_period3_test = '20201001~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221124.xlsx'
new_period1_fit = '20200701~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221124.xlsx'
new_period2_fit = '20210101~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221124.xlsx'
new_period3_fit = '20210701~20211231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221124.xlsx'
new_bt_res_fpath_list = [new_period1_test, new_period2_test, new_period3_test, new_period1_fit, new_period2_fit, new_period3_fit]
new_bt_res_name_list = ['new_period1_test', 'new_period2_test', 'new_period3_test', 'new_period1_fit', 'new_period2_fit', 'new_period3_fit']
new_filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrV8FcModel', 'LgbV1FcModel', 'XgbV1FcModel', 'LrV1FcModel']

# 第三块
new2_root_path = '/data/user/015614/shared/backtest_result/20221126回测结果_Europa_20221116三个区间上回测结果汇总（模型筛选）/'
new_period1_test = '20191002~20200630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221126.xlsx'
new_period2_test = '20200401~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221126.xlsx'
new_period3_test = '20201001~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_test_模型评价_20221126.xlsx'
new_period1_fit = '20200701~20201231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221126.xlsx'
new_period2_fit = '20210101~20210630_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221126.xlsx'
new_period3_fit = '20210701~20211231_Europa_fac_20221116_FSRS_all_pct_graded_all_merge_fit_模型评价_20221126.xlsx'
new2_bt_res_fpath_list = [new_period1_test, new_period2_test, new_period3_test, new_period1_fit, new_period2_fit, new_period3_fit]
new2_bt_res_name_list = ['new_period1_test', 'new_period2_test', 'new_period3_test', 'new_period1_fit', 'new_period2_fit', 'new_period3_fit']
new2_filtered_model_list = ['LgbV8FcModel', 'LrRSFcModel']

res_df = pd.DataFrame()
for bt_res_fpath in bt_res_fpath_list:
    res = pd.read_excel(root_path + bt_res_fpath, sheet_name='不同参与率指标统计', index_col=0)
    res = res.mean(axis=0).reset_index()
    res_df = pd.concat([res_df, res], axis=1)

new_res_df = pd.DataFrame()
for bt_res_fname in new_bt_res_fpath_list:
    res = pd.read_excel(new_root_path + bt_res_fname, sheet_name='不同参与率指标统计', index_col=0)
    res = res.mean(axis=0).reset_index()
    new_res_df = pd.concat([new_res_df, res], axis=1)

new2_res_df = pd.DataFrame()
for bt_res_fname in new2_bt_res_fpath_list:
    res = pd.read_excel(new2_root_path + bt_res_fname, sheet_name='不同参与率指标统计', index_col=0)
    res = res.mean(axis=0).reset_index()
    new2_res_df = pd.concat([new2_res_df, res], axis=1)

from dataApi.sendInfo import send_file
send_file(res_df)
send_file(new_res_df)
send_file(new2_res_df)

pass
