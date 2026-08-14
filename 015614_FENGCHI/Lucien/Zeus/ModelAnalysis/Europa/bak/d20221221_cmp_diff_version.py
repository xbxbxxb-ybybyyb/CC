# coding: utf-8
# Author：fengchi863
# Date ：2022/12/21 17:14

import pandas as pd
from tqdm import tqdm
from dataApi.sendInfo import send_file

#%% 第一块
# root_path = '/data/user/015614/shared/backtest_result/20221215回测结果_Europa_fac_20221116三个区间测试有无因子筛选的差别2/'
root_path = '/data/user/015614/junkData/回测结果/'
period1_test = '20191001~20200630_Europa_fac_20221116_FSV8_all_pct_graded_period1_all_merge_test_模型评价_20221221.xlsx'
period1_fit = '20200701~20201231_Europa_fac_20221116_FSV8_all_pct_graded_period1_all_merge_fit_模型评价_20221221.xlsx'
period2_test = '20200401~20201231_Europa_fac_20221116_FSV8_all_pct_graded_period2_all_merge_test_模型评价_20221221.xlsx'
period2_fit = '20210101~20210630_Europa_fac_20221116_FSV8_all_pct_graded_period2_all_merge_fit_模型评价_20221221.xlsx'
period3_test = '20201001~20210630_Europa_fac_20221116_FSV8_all_pct_graded_period3_all_merge_test_模型评价_20221221.xlsx'
period3_fit = '20210701~20211231_Europa_fac_20221116_FSV8_all_pct_graded_period3_all_merge_fit_模型评价_20221221.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel']

res_df = pd.DataFrame(index=pd.MultiIndex.from_product([bt_res_name_list, filtered_model_list]))
for bt_res_name in tqdm(bt_res_name_list):
    bt = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='模型结果')
    for filtered_model in filtered_model_list:
        res_df.loc[(bt_res_name, filtered_model), '基础样本数量'] = bt.loc['基础样本数量', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '组合标签胜率'] = bt.loc['组合标签胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '扣费后收益率胜率'] = bt.loc['扣费后收益率胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '样本参与率'] = bt.loc['样本参与率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '实际参与次数'] = bt.loc['实际参与次数', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
send_file(check)