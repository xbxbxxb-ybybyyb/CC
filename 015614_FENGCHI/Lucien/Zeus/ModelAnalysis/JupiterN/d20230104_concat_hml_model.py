# coding: utf-8
# Author：fengchi863
# Date ：2023/1/4 11:40

"""
给JupiterN进行分场景测试
"""

import pandas as pd
from LucienUtil.FileUtil import FileUtil
PERIOD_LIST = ['period1', 'period2', 'period3']
SUB_VERSION = [[10, 11, 12], [20, 21, 22], [30, 31, 32]]

for model_name in ['XgbRegModel', 'LgbRegModel']:
    root_path = f'/data/user/015614/Zeus/pred/JupiterN/v1_0_1/{model_name}/'
    from Zeus.JupiterN.v1_0_1.path_conf import date_config
    for idx, PERIOD in enumerate(PERIOD_LIST):
        sub_versions = SUB_VERSION[idx]
        test_data = pd.DataFrame()
        pred_type = 'test'  # test fit
        date_dict = date_config[f'{PERIOD}_{pred_type}']
        out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
        for sub_version in sub_versions:
            print(sub_version)
            test_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_v{sub_version}.csv'
            tmp_test_data = pd.read_csv(test_fpath)
            test_data = test_data.append(tmp_test_data)

        test_data = test_data.set_index('Indexs')
        FileUtil.save_df2csv(test_data, root_path, f'{out_begin}~{out_end}_{model_name}_v{idx+1}_hml.csv')

        fit_data = pd.DataFrame()
        pred_type = 'fit'  # test fit
        date_dict = date_config[f'{PERIOD}_{pred_type}']
        out_begin, out_end = date_dict['test_start_date'], date_dict['test_end_date']
        for sub_version in sub_versions:
            print(sub_version)
            fit_fpath = root_path + f'{out_begin}~{out_end}_{model_name}_v{sub_version}.csv'
            tmp_fit_data = pd.read_csv(fit_fpath)
            fit_data = fit_data.append(tmp_fit_data)

        fit_data = fit_data.set_index('Indexs')
        FileUtil.save_df2csv(fit_data, root_path, f'{out_begin}~{out_end}_{model_name}_v{idx+1}_hml.csv')

"""统计HML效果"""
import pandas as pd
from tqdm import tqdm
from dataApi.sendInfo import send_file

#%% 第一块
# root_path = '/data/user/015614/shared/backtest_result/20221226回测结果_Europa_fac_20221116_FSV8_all_pct_graded_hml_lowCost/'
root_path = '/data/user/015614/junkData/回测结果/'
period1_test = '20191001~20200331_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period1_all_merge_test_模型评价_20230104.xlsx'
period1_fit = '20200401~20201231_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period1_all_merge_fit_模型评价_20230104.xlsx'
period2_test = '20200401~20200930_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period2_all_merge_test_模型评价_20230104.xlsx'
period2_fit = '20201001~20210630_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period2_all_merge_fit_模型评价_20230104.xlsx'
period3_test = '20201001~20210331_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period3_all_merge_test_模型评价_20230104.xlsx'
period3_fit = '20210401~20211231_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period3_all_merge_fit_模型评价_20230104.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel']

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

"""统计HML各个场景效果"""
import pandas as pd
from tqdm import tqdm
from dataApi.sendInfo import send_file

#%% 第一块
root_path = '/data/user/015614/shared/backtest_result/20221226回测结果_Europa_fac_20221116_FSV8_all_pct_graded_hml_lowCost/XGB分场景/'
# root_path = '/data/user/015614/junkData/回测结果/'
period1_test = '20191001~20200331_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period1_all_merge_test_模型评价_20221228.xlsx'
period1_fit = '20200401~20201231_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period1_all_merge_fit_模型评价_20221228.xlsx'
period2_test = '20200401~20200930_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period2_all_merge_test_模型评价_20221228.xlsx'
period2_fit = '20201001~20210630_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period2_all_merge_fit_模型评价_20221228.xlsx'
period3_test = '20201001~20210331_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period3_all_merge_test_模型评价_20221228.xlsx'
period3_fit = '20210401~20211231_Europa_fac_20221116_FSV8_all_pct_graded_hml012_lowCost_period3_all_merge_fit_模型评价_20221228.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['XgbV8Hml0FcModel', 'XgbV8Hml1FcModel', 'XgbV8Hml2FcModel']

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