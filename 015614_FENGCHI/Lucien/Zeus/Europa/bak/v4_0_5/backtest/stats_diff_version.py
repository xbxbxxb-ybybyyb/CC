# coding: utf-8
# Author：fengchi863
# Date ：2023/8/18 16:08

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from tqdm import tqdm

strategy_name = 'Europa'
version = 'v4_0_5'

root_path = '/data/user/015614/Zeus/backtest/Europa/v4_0_5/回测结果/'

bt_date = '20231109'
period1_test = f'20191001~20200331_Europa_period1_all_merge_test_模型评价_{bt_date}.xlsx'
# period1_fit =  f'20200401~20201231_Europa_period1_all_merge_fit_模型评价_{bt_date}.xlsx'
# period2_test = f'20200401~20200930_Europa_period2_all_merge_test_模型评价_{bt_date}.xlsx'
# period2_fit =  f'20201001~20210630_Europa_period2_all_merge_fit_模型评价_{bt_date}.xlsx'
# period3_test = f'20201001~20210331_Europa_period3_all_merge_test_模型评价_{bt_date}.xlsx'
# period3_fit =  f'20210401~20211231_Europa_period3_all_merge_fit_模型评价_{bt_date}.xlsx'
bt_res_fpath_list = [period1_test]
bt_res_name_list = ['period1_test']
filtered_model_list = ['fsv8_pct_AllXgbRegModel', 'fsv10_pct_AllXgbRegModel', 'fsv11_pct_AllXgbRegModel', 'fsrs_pct_AllXgbRegModel', 'rffs_pct_AllXgbRegModel',
                       'fsv8_pct_AllLgbRegModel', 'fsv10_pct_AllLgbRegModel', 'fsv11_pct_AllLgbRegModel', 'fsrs_pct_AllLgbRegModel', 'rffs_pct_AllLgbRegModel',
                       ]

# period5_test = f'20211001~20220331_Europa_period5_all_merge_test_模型评价_{bt_date}.xlsx'
# bt_res_fpath_list = [period5_test]
# bt_res_name_list = ['period5_test']

# period6_test = f'20220401~20220930_Europa_period6_all_merge_test_模型评价_{bt_date}.xlsx'
# bt_res_fpath_list = [period6_test]
# bt_res_name_list = ['period6_test']
# filtered_model_list = ['fsv8_pct_XgbRegModel', 'fsv10_pct_XgbRegModel', 'fsv11_pct_XgbRegModel', 'fsrs_pct_XgbRegModel', 'rffs_pct_XgbRegModel', 'rffs2_pct_XgbRegModel',
#                        'fsv8_pct_LgbRegModel', 'fsv10_pct_LgbRegModel', 'fsv11_pct_LgbRegModel', 'fsrs_pct_LgbRegModel', 'rffs_pct_LgbRegModel', 'rffs2_pct_LgbRegModel',
#                        ]

res_df = pd.DataFrame(index=pd.MultiIndex.from_product([bt_res_name_list, filtered_model_list]))
for bt_res_name in tqdm(bt_res_name_list):
    bt = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='模型结果')
    bt_attend = pd.read_excel(root_path + eval(bt_res_name), index_col=0, sheet_name='不同参与率指标统计')
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
        res_df.loc[(bt_res_name, filtered_model), '去极值总收益'] = bt.loc['累计扣费总收益(极端值调整后)', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '最大回撤'] = bt.loc['最大回撤', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益风险比'] = bt.loc['收益风险比', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '夏普比率'] = bt.loc['夏普比率', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '收益夏普比率'] = bt.loc['收益夏普比率', filtered_model]
        # res_df.loc[(bt_res_name, filtered_model), '预测值与标签IC'] = bt.loc['预测值与标签IC', filtered_model]
        res_df.loc[(bt_res_name, filtered_model), '预测值与标签RankIC'] = bt.loc['预测值与标签RankIC', filtered_model]

check = pd.concat([res_df.T], axis=1).T
stats_copy = check.copy()
stats_copy.index.names = ['period', 'model_name']

stats_rank = stats_copy.groupby(['period']).apply(lambda x: x.rank())   # 数值越大排名越大

output_dict = dict()
output_dict['汇总结果'] = check
output_dict['各区间排名'] = stats_rank

stats_rank_sum = stats_rank.groupby('model_name').mean()
output_dict['testfit排名求和'] = stats_rank_sum

stats_rank['testfit'] = stats_rank.index.get_level_values(0).map(lambda x: x.split('_')[-1])
stats_fit_rank_sum = stats_rank.query('testfit == "fit"').groupby('model_name').mean()
output_dict['fit排名求和'] = stats_fit_rank_sum

FileUtil.save_dict2xls(output_dict, root_path, f'{strategy_name}_{version}_汇总结果.xlsx')
from dataApi.sendInfo import send_file
send_file(root_path + f'{strategy_name}_{version}_汇总结果.xlsx')