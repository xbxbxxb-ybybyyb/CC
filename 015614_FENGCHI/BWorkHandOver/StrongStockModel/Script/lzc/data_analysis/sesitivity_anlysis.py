# @Time : 2020/11/13 15:57
# @Author : Zhichen Lu
# @File : sesitivity_anlysis.py


import sys
import os

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
import gc
import matplotlib.pyplot as plt
import seaborn as sns
from multiprocessing import Pool, Manager
from StrongStockModel.conf.path_config import root_path
from dataApi.getData import get_daily_1factor
from xquant.factordata import FactorData

file_list = os.listdir('/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/')

file_list = list(filter(lambda x : x.endswith('.xlsx'),file_list))


profit_list, daily_stat_list, signaly_stat_list, cash_occupy_list, daily_buy, daily_holding, daily_profit_list,daily_profit_rate_list = [], [], [], [], [], [], [], []

base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/敏感性分析/'  # root_path + 'backtest_result_all_mkt_10bp_cost_revised_framework20201013/'
# file_list = sorted(list(filter(lambda x: x.endswith('.xlsx') and 'twap' in x, file_list)))
key_word = ['10min','insample']

file_list = sorted(list(filter(lambda x: x.endswith('.xlsx') and key_word[0] in x and key_word[1] in x, file_list)))#[:2]

for file_name in file_list:
    clf_name = file_name
    all_data = pd.read_excel(base_path + file_name, sheet_name=None, index_col=0)
    data = all_data['每日持仓统计']  # pd.read_excel(root_path + 'backtest_result_all_mkt_10bp_cost/' + file_name, sheet_name='每日持仓统计', index_col=0)
    profit_list.append(data[['累积收益']].rename(columns={'累积收益': clf_name}))
    cash_occupy_list.append(data[['占用资金']].rename(columns={'占用资金': clf_name}))
    daily_profit_list.append(data[['当日收益']].rename(columns={'当日收益': clf_name}))
    daily_profit_rate_list.append(data[['当日收益率']].rename(columns={'当日收益率': clf_name}))

    daily_cout = data[['买入股票数', '卖出股票数']]
    daily_buy.append(daily_cout[['买入股票数']].rename(columns={'买入股票数': clf_name}))
    daily_holding.append(pd.DataFrame({clf_name: (daily_cout['买入股票数'] - daily_cout['卖出股票数']).cumsum()}))
    daily_cout['year'] = [x // 10000 for x in daily_cout.index]
    yealy_stat = daily_cout.groupby('year').mean()
    yealy_stat.loc['全时段'] = daily_cout.mean()
    yealy_stat.columns = ['平均每天买入股票数', '平均每天卖出股票数']

    data = all_data['持仓综合统计']  # pd.read_excel(base_path + file_name, sheet_name='持仓综合统计', index_col=0)
    data = data.append(yealy_stat.T)
    data['模型'] = clf_name
    daily_stat_list.append(data)

    data = all_data['逐笔持仓综合统计']  # pd.read_excel(base_path + file_name, sheet_name='逐笔持仓综合统计', index_col=0)
    data['模型'] = clf_name
    signaly_stat_list.append(data)

    print(clf_name)


daily_profit_compare = pd.concat(daily_profit_list,axis=1)
daily_profit_rate_compare = pd.concat(daily_profit_rate_list,axis=1)
daily_profit_compare.index = pd.to_datetime(daily_profit_compare.index.astype(str))
daily_profit_rate_compare.index = pd.to_datetime(daily_profit_rate_compare.index.astype(str))


cash_occupy_compare = pd.concat(cash_occupy_list, axis=1)  # .fillna(0)
cash_occupy_compare.index = pd.to_datetime(cash_occupy_compare.index.astype(str))
daily_stat = pd.concat(daily_stat_list).reset_index().set_index(['index', '模型']).sort_index()
daily_vol = (daily_stat.loc['收益率均值'] / daily_stat.loc['收益率波动']).reset_index()
daily_vol['index'] = '收益均值/收益波动率'
daily_vol = daily_vol.set_index(['index', '模型'])
daily_stat = pd.concat([daily_stat, daily_vol])
signaly_stat = pd.concat(signaly_stat_list).reset_index().set_index(['index', '模型']).sort_index()
daily_holding = pd.concat(daily_holding, axis=1)
daily_holding.index = pd.to_datetime(daily_holding.index.astype(str))
daily_buy = pd.concat(daily_buy, axis=1)
daily_buy.index = pd.to_datetime(daily_buy.index.astype(str))
profit_compare = pd.concat(profit_list, axis=1).fillna(method='pad')
profit_compare.index = pd.to_datetime(profit_compare.index.astype(str))

# cum_MDD = (profit_compare.cummax() - profit_compare).cummax()
# check =


# pd.to_pickle([profit_list,daily_stat_list,signaly_stat_list],'/data/user/015664/AFuckingTrigger/XGB回归滚动阈值结果汇总.pkl')
with pd.ExcelWriter(base_path+'result_compare/%s对比.xlsx'%'_'.join(key_word)) as writer:
    profit_compare.to_excel(writer, sheet_name='累计收益')
    daily_profit_compare.to_excel(writer, sheet_name='单日收益')
    daily_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='日收益综合统计')
    signaly_stat.reset_index().set_index(['index', '模型']).sort_index().to_excel(writer, sheet_name='按信号综合统计')

writer.close()