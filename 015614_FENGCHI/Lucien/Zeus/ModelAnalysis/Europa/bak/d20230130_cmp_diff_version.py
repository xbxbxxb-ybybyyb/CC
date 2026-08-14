# coding: utf-8
# Author：fengchi863
# Date ：2023/1/30 11:18

"""开始对比"""
import pandas as pd
from tqdm import tqdm
from dataApi.sendInfo import send_file

# 第五个区间 period4
# root_path = '/data/user/015614/shared/backtest_result/20230130回测结果_Europa_fac_20221116_lowCost_5model_period5/'
# # root_path = '/data/user/015614/junkData/回测结果/'
# period5_test = '20220101~20220630_Europa_fac_20221116_FSV8_all_label_pct_graded_lowCost_period5_all_merge_test_模型评价_20230130_cmp.xlsx'

root_path = '/data/user/015614/shared/backtest_result/20230130回测结果_JupiterN_fac_20221220_lowCost_5model_period5/'
# root_path = '/data/user/015614/junkData/回测结果/'
period5_test = '20220101~20220630_JupiterN_fac_20221220_FSV8_all_label_pct_graded_lowCost_period5_all_merge_test_模型评价_20230130_cmp.xlsx'

bt_res_fpath_list = [period5_test]
bt_res_name_list = ['period5_test']
filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel',
                       'lastLgbV8FcModel', 'lastXgbV8FcModel', 'lastLrRSFcModel', 'lastLgbV8HmlFcModel', 'lastXgbV8HmlFcModel']

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
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
send_file(check)