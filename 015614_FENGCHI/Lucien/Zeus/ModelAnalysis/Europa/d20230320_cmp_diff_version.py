# coding: utf-8
# Author：fengchi863
# Date ：2023/3/15 16:10

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from dataApi.sendInfo import send_file
from tqdm import tqdm

root_path = '/data/user/015614/junkData/回测结果/'

period1_test = '20191001~20200331_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period1_all_merge_test_模型评价_20230320.xlsx'
period1_fit = '20200401~20201231_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period1_all_merge_fit_模型评价_20230320.xlsx'
period2_test = '20200401~20200930_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period2_all_merge_test_模型评价_20230320.xlsx'
period2_fit = '20201001~20210630_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period2_all_merge_fit_模型评价_20230320.xlsx'
period3_test = '20201001~20210331_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period3_all_merge_test_模型评价_20230320.xlsx'
period3_fit = '20210401~20211231_Europa_fac_20230314_FSV8_all_label_pct_graded_lowCost_period3_all_merge_fit_模型评价_20230320.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['newModel', 'rffsModel', 'oldModel']

model_rep_fpath_list = [
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModel/Europa_v2_0_9_LgbRegModel_v1_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModel/Europa_v2_0_9_LgbRegModel_v2_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModel/Europa_v2_0_9_LgbRegModel_v3_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModelV2/Europa_v2_0_9_LgbRegModelV2_v1_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModelV2/Europa_v2_0_9_LgbRegModelV2_v2_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_9/LgbRegModelV2/Europa_v2_0_9_LgbRegModelV2_v3_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_4/LgbRegModelV3/Europa_v2_0_4_LgbRegModelV3_v1_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_4/LgbRegModelV3/Europa_v2_0_4_LgbRegModelV3_v2_.xlsx',
    '/data/user/015614/Zeus/logs/Europa/v2_0_4/LgbRegModelV3/Europa_v2_0_4_LgbRegModelV3_v3_.xlsx',
]

check = dict()

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
        # res_df.loc[(bt_res_name, filtered_model), '实际参与次数'] = bt.loc['实际参与次数', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益率均值'] = bt.loc['收益率均值', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '累计扣费总收益'] = bt.loc['累计扣费总收益', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        # res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

model_list = ['newModel', 'rffsModel', 'oldModel']
model_ref_valid_df = pd.DataFrame(index=pd.MultiIndex.from_product([model_list, ['valid_auc', 'valid_precision', 'valid_rmse', 'valid_ic']]), columns=['period1', 'period2', 'period3'])
model_ref_test_df = pd.DataFrame(index=pd.MultiIndex.from_product([model_list, ['test_auc', 'test_precision', 'test_rmse', 'test_ic']]), columns=['period1', 'period2', 'period3'])
model_ref_fit_df = pd.DataFrame(index=pd.MultiIndex.from_product([model_list, ['fit_auc', 'fit_precision', 'fit_rmse', 'fit_ic']]), columns=['period1', 'period2', 'period3'])

for idx, model_rep_fpath in enumerate(model_rep_fpath_list):
    period = f'period{idx % 3 + 1}'
    model_idx = idx // 3
    model = model_list[model_idx]
    rep_df = pd.read_excel(model_rep_fpath, index_col=0)
    chosen_row = rep_df.iloc[0]
    for vtf in ['valid', 'test', 'fit']:
        auc = chosen_row[f'{vtf}_auc']
        precision = chosen_row[f'{vtf}_precision']
        rmse = chosen_row[f'{vtf}_rmse']
        ic = chosen_row[f'{vtf}_ic']
        if vtf is 'valid':
            model_ref_valid_df.loc[(model, slice(None)), period] = [auc, precision, rmse, ic]
        if vtf is 'test':
            model_ref_test_df.loc[(model, slice(None)), period] = [auc, precision, rmse, ic]
        if vtf is 'fit':
            model_ref_fit_df.loc[(model, slice(None)), period] = [auc, precision, rmse, ic]

check['回测结果'] = pd.concat([res_df.T], axis=1).T
check['model_valid'] = model_ref_valid_df
check['model_test'] = model_ref_test_df
check['model_fit'] = model_ref_fit_df

FileUtil.save_dict2xls(check, '/data/user/015614/junkData/', '模型对比.xlsx')
send_file('/data/user/015614/junkData/模型对比.xlsx')