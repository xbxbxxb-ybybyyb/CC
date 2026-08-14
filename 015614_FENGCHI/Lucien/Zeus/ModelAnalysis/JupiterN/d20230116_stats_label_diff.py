# coding: utf-8
# Author：fengchi863
# Date ：2023/1/16 8:42

import pandas as pd
from tqdm import tqdm
from LucienUtil.FileUtil import FileUtil

"""统计Europa更换信号前后的差异"""
europa_path = '/data/user/015614/Zeus/pred/Europa/v1_0_31/'
model = 'XgbRegModel'
europa = pd.read_csv(europa_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
europa = europa.query('prediction == 1')

label_path = '/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20211231_train.pkl'
profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
label = pd.read_pickle(label_path)
profit = pd.read_hdf(profit_path)
check = pd.concat([profit, label], axis=1).reindex(index=label.index)
check['datelist'] = check.index.get_level_values(0).strftime('%Y%m%d').tolist()
check = check.reset_index()
check['Indexs'] = check['Ticker'] + ' ' + check['datelist']
check = check.set_index('Indexs')
# TODO: 注意根据buy_vol设置是 可成交的 还是 不可成交的
check.query('datelist >= "20210701" & datelist <= "20211231" & buy_vol > 0')['pct'].describe()
check.query('datelist >= "20210701" & datelist <= "20211231" & buy_vol > 0')['label_TN_o2ul'].describe()

# 只筛选jupiter信号为1的样本
check2 = check.reindex(index=europa.index)
check2.query('datelist >= "20210701" & datelist <= "20211231" & buy_vol == 0')['pct'].describe()
check2.query('datelist >= "20210701" & datelist <= "20211231" & buy_vol == 0')['label_TN_o2ul'].describe()

# 测日内涨停的比例和收盘涨停的比例
from dataApi.tradeDate import get_date_range
from dataApi import getData, stockList
check = check.query('datelist >= "20210701" & datelist <= "20211231" & buy_vol == 0')
check = check[['sell_date', 'datelist', 'Ticker']]
check['first_sell_date'] = check['sell_date'].apply(lambda x: int(x[1:9]))
check['stk_id'] = check['Ticker'].map(stockList.trans_windcode2int)
date_list = get_date_range(20210701, 20220120)
stk_list = list(check['Ticker'].map(stockList.trans_windcode2int).unique())
high = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list)
limit_max = getData.get_daily_1factor('limit_max', date_list=date_list, code_list=stk_list)
close = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list)
zt = high == limit_max
final_zt = close == limit_max
# 买入日，未成交部分样本都是100%，是由于买入日成交数量的计算逻辑的原因
check['zt'] = check[['datelist', 'stk_id']].apply(lambda x: zt.loc[int(x['datelist']), x['stk_id']], axis=1)
check['final_zt'] = check[['datelist', 'stk_id']].apply(lambda x: final_zt.loc[int(x['datelist']), x['stk_id']], axis=1)
a = check[['datelist', 'stk_id', 'zt', 'final_zt']]
a['zt'].sum() / len(a)
a['final_zt'].sum() / len(a)
# 卖出日
check['zt'] = check[['first_sell_date', 'stk_id']].apply(lambda x: zt.loc[int(x['first_sell_date']), x['stk_id']], axis=1)
check['final_zt'] = check[['first_sell_date', 'stk_id']].apply(lambda x: final_zt.loc[int(x['first_sell_date']), x['stk_id']], axis=1)
a = check[['first_sell_date', 'stk_id', 'zt', 'final_zt']]
a['zt'].sum() / len(a)
a['final_zt'].sum() / len(a)

"""对比Europa和Jupiter的"""
# europa_path = '/data/user/015614/Zeus/pred/Europa/v1_0_31/'
# jupiter_path = '/data/user/015614/Zeus/pred/JupiterN/v1_0_1/'
# other_path = '/data/group/800463/wangj/for_fc/'
#
# model = 'XgbRegModel'
# europa = pd.read_csv(europa_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
# jupiter = pd.read_csv(jupiter_path + f'{model}/20210701~20211231_{model}_v4.csv', index_col=0)
# # 测试全部重合样本
# # europa_copy = europa.loc[list(set(europa.index).intersection(set(jupiter.index)))]
# # jupiter_copy = jupiter.loc[list(set(europa.index).intersection(set(jupiter.index)))]
# # 测试prediction为1的样本
# europa_copy = europa.loc[list(set(europa.query('prediction == 1').index).intersection(set(jupiter.query('prediction == 1').index)))]
# jupiter_copy = jupiter.loc[list(set(europa.query('prediction == 1').index).intersection(set(jupiter.query('prediction == 1').index)))]
#
# europa_label_path = '/data/group/800463/sunss/for_xly/europa/20221116_new/factor_df_all_20160101_20211231_train.pkl'
# europa_profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/001/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
#
# jupiter_label_path = '/data/group/800463/project/project1_prod/factor_manager_v2/all_factor_bank/raw/all_factor_20150101_20220225.pkl'
# jupiter_profit_path = '/data/group/800463/project/project1_prod/LabelProfit_fixvol/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
#
# europa_label = pd.read_pickle(europa_label_path)
# jupiter_label = pd.read_pickle(jupiter_label_path)
# europa_profit = pd.read_hdf(europa_profit_path)
# jupiter_profit = pd.read_hdf(jupiter_profit_path)
# europa_bt = pd.concat([europa_label, europa_profit], axis=1).reindex(index=europa_label.index)
# jupiter_bt = pd.concat([jupiter_label, jupiter_profit], axis=1).reindex(index=jupiter_label.index)
# europa_bt['datelist'] = europa_bt.index.get_level_values(0).strftime('%Y%m%d').tolist()
# jupiter_bt['datelist'] = jupiter_bt.index.get_level_values(0).strftime('%Y%m%d').tolist()
# europa_bt = europa_bt.reset_index()
# jupiter_bt = jupiter_bt.reset_index()
# europa_bt['Indexs'] = europa_bt['Ticker'] + ' ' + europa_bt['datelist']
# jupiter_bt['Indexs'] = jupiter_bt['Ticker'] + ' ' + jupiter_bt['datelist']
# europa_bt = europa_bt.set_index('Indexs')
# jupiter_bt = jupiter_bt.set_index('Indexs')
#
# europa_check = europa_bt.loc[europa_copy.index]
# jupiter_check = jupiter_bt.loc[europa_copy.index]
#
# europa_check = europa_check.query('datelist >= "20210701" & datelist <= "20211231"')
# jupiter_check = jupiter_check.query('datelist >= "20210701" & datelist <= "20211231"')
#
# # 成交率
# (europa_check['buy_vol'] > 0).sum() / len(europa_check)
# (jupiter_check['buy_vol'] > 0).sum() / len(jupiter_check)
#
# europa_cannot_buy = europa_check.query('buy_vol == 0')
# jupiter_cannot_buy = jupiter_check.query('buy_vol == 0')
#
# europa_selfcanbuy = set(jupiter_cannot_buy.index).difference(set(europa_cannot_buy.index))
# europa_check.loc[europa_selfcanbuy]['pct'].mean()
#
# # 看全部基础样本的pct均值
# europa_check['pct'].mean()
# jupiter_check['pct'].mean()
# # 看全部可以买的基础样本的均值
# europa_can_buy = europa_check.query('buy_vol > 0')
# jupiter_can_buy = jupiter_check.query('buy_vol > 0')
# europa_check.loc[europa_can_buy.index]['pct'].mean()
# jupiter_check.loc[jupiter_can_buy.index]['pct'].mean()
# europa_check.loc[europa_cannot_buy.index]['pct'].mean()
# jupiter_check.loc[jupiter_cannot_buy.index]['pct'].mean()
#
#
# ### 检查占比
# europa_bt = europa_bt.reindex(index=europa.query('datelist >= 20210701 & datelist <= 20211231').index)
# check = europa_bt.query('buy_vol == 0 & pct != label_TN_o2ul')[['pct', 'label_TN_o2ul']]
#
# europa_bt_pred1 = europa_bt.reindex(europa.query('prediction == 1 & datelist >= 20210701 & datelist <= 20211231').index)
# europa_bt_pred1 = europa_bt.reindex(index=europa_bt_pred1.index)
# desc = europa_bt_pred1.query('buy_vol == 0').describe()
# check = europa_bt_pred1.query('buy_vol == 0 & pct != label_TN_o2ul')[['pct', 'label_TN_o2ul']]