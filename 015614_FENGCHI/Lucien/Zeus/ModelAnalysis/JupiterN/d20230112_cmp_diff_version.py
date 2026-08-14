# coding: utf-8
# Author：fengchi863
# Date ：2023/1/12 9:11

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from tqdm import tqdm

"""
root_path = '/data/user/015614/shared/backtest_result/20230111回测结果_JupiterN_fac_20221220_lowCost_5model_period4/'
# period4_test = '20210701~20211231_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period4_all_merge_test_模型评价_20230111.xlsx'
# bt_res_fpath_list = [period4_test]
# bt_res_name_list = ['period4_test']
# filtered_model_list = ['LgbV8FcModel', 'XgbV8FcModel', 'LrRSFcModel', 'LgbV8HmlFcModel', 'XgbV8HmlFcModel']

period4_test = '20210701~20211231_JupiterN_fac_20221220_FSV8_all_pct_graded_lowCost_period4_all_merge_test_模型评价_cmp_20230111.xlsx'
bt_res_fpath_list = [period4_test]
bt_res_name_list = ['period4_test']
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
"""

# 对比成交率
europa_path = '/data/user/015614/Zeus/pred/Europa/v1_0_31/'
jupiter_path = '/data/user/015614/Zeus/pred/JupiterN/v1_0_1/'
jupiter_europa_path = '/data/user/015614/Zeus/pred/JupiterN/v1_0_1/jupiter_europa_cmp/'

model = 'LrRegModel'
europa = pd.read_csv(europa_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
jupiter = pd.read_csv(jupiter_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
"""测试全部样本"""
# europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
# jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
europa_copy = europa.loc[list(set(europa.query('prediction == 1').index).intersection(set(jupiter.query('prediction == 1').index)))]
jupiter_copy = jupiter.loc[list(set(europa.query('prediction == 1').index).intersection(set(jupiter.query('prediction == 1').index)))]

europa_label_path = '/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20211231_train.pkl'
europa_profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'

jupiter_label_path = '/data/group/800463/project/project1_prod/factor_manager_v2/all_factor_bank/raw/all_factor_20150101_20220225.pkl'
jupiter_profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'

europa_label = pd.read_pickle(europa_label_path)
jupiter_label = pd.read_pickle(jupiter_label_path)
europa_profit = pd.read_hdf(europa_profit_path)
jupiter_profit = pd.read_hdf(jupiter_profit_path)
europa_bt = pd.concat([europa_label, europa_profit], axis=1)
jupiter_bt = pd.concat([jupiter_label, jupiter_profit], axis=1)
europa_bt['datelist'] = europa_bt.index.get_level_values(0).strftime('%Y%m%d').tolist()
jupiter_bt['datelist'] = jupiter_bt.index.get_level_values(0).strftime('%Y%m%d').tolist()
europa_bt = europa_bt.reset_index()
jupiter_bt = jupiter_bt.reset_index()
europa_bt['Indexs'] = europa_bt['Ticker'] + ' ' + europa_bt['datelist']
jupiter_bt['Indexs'] = jupiter_bt['Ticker'] + ' ' + jupiter_bt['datelist']
europa_bt = europa_bt.set_index('Indexs')
jupiter_bt = jupiter_bt.set_index('Indexs')

europa_check = europa_bt.loc[europa_copy.index]
jupiter_check = jupiter_bt.loc[europa_copy.index]

europa_check = europa_check.query('datelist >= "20210701" & datelist <= "20211231"')
jupiter_check = jupiter_check.query('datelist >= "20210701" & datelist <= "20211231"')

(europa_check['buy_vol'] > 0).sum() / len(europa_check)
(jupiter_check['buy_vol'] > 0).sum() / len(jupiter_check)

europa_cannot_buy = europa_check.query('buy_vol == 0')
jupiter_cannot_buy = jupiter_check.query('buy_vol == 0')

europa_selfcanbuy = set(jupiter_cannot_buy.index).difference(set(europa_cannot_buy.index))
europa_check.loc[europa_selfcanbuy]['pct'].mean()

### 检查占比
europa_bt = europa_bt.reindex(index=europa.query('datelist >= 20210701 & datelist <= 20211231').index)
check = europa_bt.query('buy_vol == 0 & pct != label_TN_o2ul')[['pct', 'label_TN_o2ul']]

europa_bt_pred1 = europa_bt.reindex(europa.query('prediction == 1 & datelist >= 20210701 & datelist <= 20211231').index)
europa_bt_pred1 = europa_bt.reindex(index=europa_bt_pred1.index)
desc = europa_bt_pred1.query('buy_vol == 0').describe()
check = europa_bt_pred1.query('buy_vol == 0 & pct != label_TN_o2ul')[['pct', 'label_TN_o2ul']]