# coding: utf-8
# Author：fengchi863
# Date ：2023/1/4 14:37

"""
20230104:对齐Jup和Eur v101 和 v1031

20230109:对period4再次使用
"""
import pandas as pd
from LucienUtil.FileUtil import FileUtil
from tqdm import tqdm

"""对齐用"""
europa_path = '/data/user/015614/Zeus/pred/Europa/v1_0_31/'
jupiter_path = '/data/user/015614/Zeus/pred/JupiterN/v1_0_1/'
jupiter_europa_path = '/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/'
for model in ['LgbRegModel', 'XgbRegModel', 'LrRegModel']:
    europa = pd.read_csv(europa_path + f'{model}/20200401~20201231_{model}_v1.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20200401~20201231_{model}_v1.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20200401~20201231_{model}_v1_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20200401~20201231_{model}_v1_jupiter.csv')

    europa = pd.read_csv(europa_path + f'{model}/20191001~20200331_{model}_v1.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20191001~20200331_{model}_v1.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20191001~20200331_{model}_v1_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20191001~20200331_{model}_v1_jupiter.csv')

    europa = pd.read_csv(europa_path + f'{model}/20201001~20210630_{model}_v2.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20201001~20210630_{model}_v2.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20201001~20210630_{model}_v2_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20201001~20210630_{model}_v2_jupiter.csv')

    europa = pd.read_csv(europa_path + f'{model}/20200401~20200930_{model}_v2.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20200401~20200930_{model}_v2.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20200401~20200930_{model}_v2_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20200401~20200930_{model}_v2_jupiter.csv')

    europa = pd.read_csv(europa_path + f'{model}/20210401~20211231_{model}_v3.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20210401~20211231_{model}_v3.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20210401~20211231_{model}_v3_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20210401~20211231_{model}_v3_jupiter.csv')

    europa = pd.read_csv(europa_path + f'{model}/20201001~20210331_{model}_v3.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20201001~20210331_{model}_v3.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20201001~20210331_{model}_v3_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20201001~20210331_{model}_v3_jupiter.csv')

    # period4 test
    europa = pd.read_csv(europa_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
    jupiter = pd.read_csv(jupiter_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
    europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
    FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20210701~20211231_{model}_v4_europa.csv')
    FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20210701~20211231_{model}_v4_jupiter.csv')

    if model is not 'LrRegModel':
        europa = pd.read_csv(europa_path + f'{model}/20200401~20201231_{model}_v1_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20200401~20201231_{model}_v1_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20200401~20201231_{model}_v1_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20200401~20201231_{model}_v1_jupiter_hml.csv')

        europa = pd.read_csv(europa_path + f'{model}/20191001~20200331_{model}_v1_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20191001~20200331_{model}_v1_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20191001~20200331_{model}_v1_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20191001~20200331_{model}_v1_jupiter_hml.csv')

        europa = pd.read_csv(europa_path + f'{model}/20201001~20210630_{model}_v2_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20201001~20210630_{model}_v2_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20201001~20210630_{model}_v2_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20201001~20210630_{model}_v2_jupiter_hml.csv')

        europa = pd.read_csv(europa_path + f'{model}/20200401~20200930_{model}_v2_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20200401~20200930_{model}_v2_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20200401~20200930_{model}_v2_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20200401~20200930_{model}_v2_jupiter_hml.csv')

        europa = pd.read_csv(europa_path + f'{model}/20210401~20211231_{model}_v3_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20210401~20211231_{model}_v3_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20210401~20211231_{model}_v3_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20210401~20211231_{model}_v3_jupiter_hml.csv')

        europa = pd.read_csv(europa_path + f'{model}/20201001~20210331_{model}_v3_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20201001~20210331_{model}_v3_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20201001~20210331_{model}_v3_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20201001~20210331_{model}_v3_jupiter_hml.csv')

        # period4 test
        europa = pd.read_csv(europa_path + f'{model}/20210701~20211231_{model}_v4_hml.csv', index_col=0)
        jupiter = pd.read_csv(jupiter_path + f'{model}/20210701~20211231_{model}_v4_hml.csv', index_col=0)
        europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
        FileUtil.save_df2csv(europa_copy, jupiter_europa_path + f'{model}/', f'20210701~20211231_{model}_v4_europa_hml.csv')
        FileUtil.save_df2csv(jupiter_copy, jupiter_europa_path + f'{model}/', f'20210701~20211231_{model}_v4_jupiter_hml.csv')



"""
比较结果
"""
root_path = '/data/user/015614/shared/backtest_result/20230104回测结果_JupiterN_fac_20221220_JupEur对齐_lowCost_5model/'
# root_path = '/data/user/015614/junkData/回测结果/'
period1_test = '20191001~20200331_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period1_all_merge_test_模型评价_20230104.xlsx'
period1_fit = '20200401~20201231_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period1_all_merge_fit_模型评价_20230104.xlsx'
period2_test = '20200401~20200930_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period2_all_merge_test_模型评价_20230104.xlsx'
period2_fit = '20201001~20210630_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period2_all_merge_fit_模型评价_20230104.xlsx'
period3_test = '20201001~20210331_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period3_all_merge_test_模型评价_20230104.xlsx'
period3_fit = '20210401~20211231_Europa_fac_20221220_FSV8_all_pct_graded_lowCost_jup&eur_period3_all_merge_fit_模型评价_20230104.xlsx'
bt_res_fpath_list = [period1_test, period1_fit, period2_test, period2_fit, period3_test, period3_fit]
bt_res_name_list = ['period1_test', 'period1_fit', 'period2_test', 'period2_fit', 'period3_test', 'period3_fit']
filtered_model_list = ['JupLgbV8FcModel', 'JupXgbV8FcModel', 'JupLrRSFcModel', 'JupLgbV8HmlFcModel', 'JupXgbV8HmlFcModel',
                       'EurLgbV8FcModel', 'EurXgbV8FcModel', 'EurLrRSFcModel', 'EurLgbV8HmlFcModel', 'EurXgbV8HmlFcModel']

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
from dataApi.sendInfo import send_file
send_file(check)