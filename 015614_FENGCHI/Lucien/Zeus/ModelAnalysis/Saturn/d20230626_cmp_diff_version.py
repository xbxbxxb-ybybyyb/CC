# coding: utf-8
# Author：fengchi863
# Date ：2023/6/26 17:37

import pandas as pd
from tqdm import tqdm

root_path = '/data/user/015614/junkData/回测结果/'

period1_test = '20191001~20200331_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period1_all_merge_test_模型评价_20230615.xlsx'
period1_fit  = '20200401~20201231_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period1_all_merge_fit_模型评价_20230615.xlsx'
period2_test = '20200401~20200930_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period2_all_merge_test_模型评价_20230615.xlsx'
period2_fit  = '20201001~20210630_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period2_all_merge_fit_模型评价_20230615.xlsx'
period3_test = '20201001~20210331_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period3_all_merge_test_模型评价_20230615.xlsx'
period3_fit  = '20210401~20211231_SaturnS1_fac_20230524_FSV8_all_label_pct_graded_lowCost_period3_all_merge_fit_模型评价_20230615.xlsx'
period4_test = '20210401~20210930_SaturnS1_fac_20230526_FSV8_all_label_v2o10d1_graded_period4_all_merge_test_模型评价_20230626.xlsx'
period5_test = '20211001~20220331_SaturnS1_fac_20230526_FSV8_all_label_v2o10d1_graded_period5_v406_all_merge_test_模型评价_20230628.xlsx'
period6_test = '20220401~20220930_SaturnS1_fac_20230626_FSV8_all_label_v2o10d1_graded_period6_v413_all_merge_test_模型评价_20230630.xlsx'
bt_res_fpath_list = [period6_test]
bt_res_name_list = ['period6_test']
# filtered_model_list = ['fsv8_AllXgbRegModel', 'fsv10_AllXgbRegModel', 'fsv11_AllXgbRegModel', 'rffs_AllXgbRegModel', 'fsrs_AllXgbRegModel']
# filtered_model_list = ['fsv8_XgbRegModel', 'fsv10_XgbRegModel', 'fsv11_XgbRegModel', 'rffs_XgbRegModel', 'fsrs_XgbRegModel',
#                        'fsv8_abs_XgbRegModel', 'fsv10_abs_XgbRegModel', 'fsv11_abs_XgbRegModel', 'rffs_abs_XgbRegModel', 'fsrs_abs_XgbRegModel',
#                        'fsv8_LgbRegModel', 'fsv10_LgbRegModel', 'fsv11_LgbRegModel', 'rffs_LgbRegModel', 'fsrs_LgbRegModel',
#                        'fsv8_abs_LgbRegModel', 'fsv10_abs_LgbRegModel', 'fsv11_abs_LgbRegModel', 'rffs_abs_LgbRegModel', 'fsrs_abs_LgbRegModel']
filtered_model_list = ['fsv8_XgbRegModel', 'fsv10_XgbRegModel', 'fsv11_XgbRegModel', 'rffs_XgbRegModel', 'fsrs_XgbRegModel',
                       'fsv8_LgbRegModel', 'fsv10_LgbRegModel', 'fsv11_LgbRegModel', 'rffs_LgbRegModel', 'fsrs_LgbRegModel']

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
        res_df.loc[(bt_res_name, filtered_model), '基础样本胜率'] = bt.loc['基础样本胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '扣费收益率胜率'] = bt.loc['扣费收益率胜率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '样本参与率'] = bt.loc['样本参与率', filtered_model]
        # res_df.loc[(bt_res_name, filtered_model), '实际参与次数'] = bt.loc['实际参与次数', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益率均值'] = bt.loc['收益率均值', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '去极值总收益'] = bt.loc['累计扣费总收益(极端值调整后)', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        # res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
from dataApi.sendInfo import send_file
send_file(check)