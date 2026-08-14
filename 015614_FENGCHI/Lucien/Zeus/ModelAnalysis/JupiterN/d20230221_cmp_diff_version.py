# coding: utf-8
# Author：fengchi863
# Date ：2023/2/21 15:19

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from tqdm import tqdm

# root_path = '/data/user/015614/shared/backtest_result/20230208回测结果_JupiterN_fac_20221220_lowCost_测试10点前的样本V2/'
root_path = '/data/user/015614/junkData/回测结果/'

period3_test = '20201001~20210331_JupiterN_fac_20221220_FSV8_all_label_pct_graded_lowCost_period3_all_merge_test_模型评价_20230221.xlsx'
period3_fit = '20210401~20211231_JupiterN_fac_20221220_FSV8_all_label_pct_graded_lowCost_period3_all_merge_fit_模型评价_20230221.xlsx'
period4_test = '20210401~20210930_JupiterN_fac_20221220_FSV8_all_label_pct_graded_lowCost_period4_all_merge_test_模型评价_20230221.xlsx'
period4_fit = '20211001~20220630_JupiterN_fac_20221220_FSV8_all_label_pct_graded_lowCost_period4_all_merge_fit_模型评价_20230221.xlsx'
bt_res_fpath_list = [period3_test, period3_fit, period4_test, period4_fit]
bt_res_name_list = ['period3_test', 'period3_fit', 'period4_test', 'period4_fit']
# filtered_model_list = ['newLgbFcModel', 'oldLgbFcModel_before10', 'oldLgbFcModel_after10']
filtered_model_list = ['newLgbModel', 'newLgbModelAttend40', 'newLgbModelAttend50', 'newLgbModelAttend60', 'oldLgbModel_before935', 'oldLgbModel_after935']

res_df = pd.DataFrame(index=pd.MultiIndex.from_product([bt_res_name_list, filtered_model_list]))
for bt_res_name in tqdm(bt_res_name_list):
    bt = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='模型结果')
    bt_attend = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='不同参与率指标统计')
    bt_idx_list = [1 + idx * len(filtered_model_list) for idx in range(0, 4)]
    res_df.loc[(bt_res_name, slice(None)), '平均累计盈利'] = bt_attend.iloc[:, 1: 1 + len(filtered_model_list)].mean().values
    res_df.loc[(bt_res_name, slice(None)), '平均最大回撤'] = bt_attend.iloc[:, 2 + len(filtered_model_list): 2 + 2 * len(filtered_model_list)].mean().values
    res_df.loc[(bt_res_name, slice(None)), '平均收益风险比'] = bt_attend.iloc[:, 3 + 2 * len(filtered_model_list): 3 + 3 * len(filtered_model_list)].mean().values
    res_df.loc[(bt_res_name, slice(None)), '平均收益夏普比率'] = bt_attend.iloc[:, 4 + 3 * len(filtered_model_list): 4 + 4 * len(filtered_model_list)].mean().values
    res_df.loc[(bt_res_name, slice(None)), '平均扣费收益率'] = bt_attend.iloc[:, 5 + 4 * len(filtered_model_list): 5 + 5 * len(filtered_model_list)].mean().values
    for filtered_model in filtered_model_list:
        res_df.loc[(bt_res_name, filtered_model), '基础样本数量'] = bt.loc['基础样本数量', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '组合标签胜率'] = bt.loc['组合标签胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '扣费后收益率胜率'] = bt.loc['扣费后收益率胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '样本参与率'] = bt.loc['样本参与率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '实际参与次数'] = bt.loc['实际参与次数', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益率均值'] = bt.loc['收益率均值', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
from dataApi.sendInfo import send_file
send_file(check)