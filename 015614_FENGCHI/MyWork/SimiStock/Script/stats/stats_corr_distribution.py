# coding: utf-8
# Author：fengchi863
# Date ：2022/4/22 15:21
"""
统计不同行业的最大相关性的分布情况
"""

import pandas as pd
import numpy as np
from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
from SimiStock.dataApi import getData, indName
from SimiStock.dataApi import tradeDate
from tqdm import tqdm

type = '分年度'
# type = '分行业'
start_date = 20210101
end_date = 20210930

filename = f'新版本_1_(-1, 1)_(-1, 1)_(120, 120)_95_{start_date}_{end_date}_corrResult.pkl'
hedge_list = pd.read_pickle(hedge_path + filename)
sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20161201, tradeDate.get_today()))

ret_list = list()
for hedge in tqdm(hedge_list):
    stk_id = hedge['stk_id']
    trade_date = hedge['date']
    ind_code = sw1.loc[trade_date, stk_id]
    ind_name = indName.sw_level1[ind_code]
    corr_max = hedge['hedge_list'][0]['hedge_value'][0]
    ret_list.append([trade_date, stk_id, ind_name, corr_max])
ret_df = pd.DataFrame(ret_list, columns=['交易日期', '股票代码', '申万一级行业', 'corr_max'])
if type is '分年度':
    ret_df['年份'] = ret_df['交易日期'] // 10000
    corr_perc = ret_df.groupby(['申万一级行业', '年份']).apply(lambda x: np.percentile(x['corr_max'].values, 50))

    corr_perc = corr_perc.unstack()
    tmp2 = ret_df.groupby(['申万一级行业', '年份'])['股票代码'].apply(lambda x: x.count())
    # corr_perc = pd.concat([corr_perc, tmp2], axis=1)

    corr_df = pd.DataFrame()
    for corr_tuple in [(-1, 0), (0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)]:
        tmp = ret_df.groupby(['申万一级行业', '年份'])['corr_max'].apply(
            lambda x: ((x < corr_tuple[1]) & (corr_tuple[0] <= x)).sum()) / tmp2
        corr_df = pd.concat([corr_df, tmp], axis=1)
    corr_df.columns = [(-1, 0), (0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)]
    ret_df6 = corr_df.copy()
else:
    corr_perc = pd.DataFrame()
    for perc in [0, 10, 30, 50, 70, 90, 100]:
        tmp = ret_df.groupby(['申万一级行业']).apply(lambda x: np.percentile(x['corr_max'].values, perc))
        corr_perc = pd.concat([corr_perc, tmp], axis=1)
    tmp2 = ret_df.groupby(['申万一级行业'])['股票代码'].apply(lambda x: x.count())
    corr_perc = pd.concat([corr_perc, tmp2], axis=1)
    corr_perc.columns = [f'{x}%分位数' for x in [0, 10, 30, 50, 70, 90, 100]] + ['个数']
    # util.save_df2xls(corr_perc, other_stats_path, 'corr_distribution.xlsx')
    # print(corr_perc)

    corr_df = pd.DataFrame()
    for corr_tuple in [(-1, 0), (0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)]:
        tmp = ret_df.groupby(['申万一级行业'])['corr_max'].apply(lambda x: ((x < corr_tuple[1]) & (corr_tuple[0] <= x)).sum()) / tmp2
        corr_df = pd.concat([corr_df, tmp], axis=1)
    corr_df.columns = [(-1, 0), (0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 1)]
    ret_df6 = corr_df.copy()
ret_df1 = corr_perc.copy()

#%% 第二种测试
filename = f'新版本_1_(-1, 1)_(-1, 1)_(120, 120)_95_5_{start_date}_{end_date}_corrResultV2.pkl'
hedge_list = pd.read_pickle(hedge_path + filename)
sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20161201, tradeDate.get_today()))

ret_list = list()
for hedge in tqdm(hedge_list):
    stk_id = hedge['stk_id']
    trade_date = hedge['date']
    ind_code = sw1.loc[trade_date, stk_id]
    ind_name = indName.sw_level1[ind_code]
    tmp_list = hedge['hedge_list'][0]['hedge_value']
    ret_list.append([trade_date, stk_id, ind_name] + tmp_list)
ret_df = pd.DataFrame(ret_list, columns=['交易日期', '股票代码', '申万一级行业', '选取个数', '均值', '最小值',
                                         '最大值', '下降大于0.1个数', '所占比例'])
if type is '分年度':
    ret_df['年份'] = ret_df['交易日期'] // 10000
    corr_perc = ret_df.groupby(['申万一级行业', '年份']).apply(lambda x: np.percentile(x['均值'].values, 50))

    corr_perc = corr_perc.unstack()
    # tmp2 = ret_df.groupby(['申万一级行业', '年份'])['股票代码'].apply(lambda x: x.count())
    # corr_perc = pd.concat([corr_perc, tmp2], axis=1)

else:
    corr_perc = pd.DataFrame()
    for perc in [0, 10, 30, 50, 70, 90, 100]:
        tmp = ret_df.groupby(['申万一级行业']).apply(lambda x: np.percentile(x['均值'].values, perc))
        corr_perc = pd.concat([corr_perc, tmp], axis=1)
    tmp2 = ret_df.groupby(['申万一级行业'])['股票代码'].apply(lambda x: x.count())
    corr_perc = pd.concat([corr_perc, tmp2], axis=1)
    corr_perc.columns = [f'{x}%分位数' for x in [0, 10, 30, 50, 70, 90, 100]] + ['个数']
    # util.save_df2xls(ret_df, other_stats_path, 'corr_distribution2.xlsx')
ret_df2 = corr_perc.copy()

if type is '分年度':
    ret_df['年份'] = ret_df['交易日期'] // 10000
    corr_perc = ret_df.groupby(['申万一级行业', '年份']).apply(lambda x: np.percentile(x['均值'].map(abs).values, 50))

    corr_perc = corr_perc.unstack()
    # tmp2 = ret_df.groupby(['申万一级行业', '年份'])['股票代码'].apply(lambda x: x.count())
    # corr_perc = pd.concat([corr_perc, tmp2], axis=1)
else:
    corr_perc = pd.DataFrame()
    for perc in [0, 10, 30, 50, 70, 90, 100]:
        tmp = ret_df.groupby(['申万一级行业']).apply(lambda x: np.percentile(x['均值'].map(abs).values, perc))
        corr_perc = pd.concat([corr_perc, tmp], axis=1)
    tmp2 = ret_df.groupby(['申万一级行业'])['股票代码'].apply(lambda x: x.count())
    corr_perc = pd.concat([corr_perc, tmp2], axis=1)
    corr_perc.columns = [f'{x}%分位数' for x in [0, 10, 30, 50, 70, 90, 100]] + ['个数']
ret_df3 = corr_perc.copy()
# util.save_df2xls(ret_df, other_stats_path, 'corr_distribution2abs.xlsx')

#%% 第三种测试
filename = f'新版本_1_(-1, 1)_(-1, 1)_(120, 120)_95_5_{start_date}_{end_date}_corrResultV3.pkl'
hedge_list = pd.read_pickle(hedge_path + filename)
sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20161201, tradeDate.get_today()))

ret_list = list()
for hedge in tqdm(hedge_list):
    stk_id = hedge['stk_id']
    trade_date = hedge['date']
    ind_code = sw1.loc[trade_date, stk_id]
    ind_name = indName.sw_level1[ind_code]
    tmp_list = hedge['hedge_list'][0]['hedge_value']
    ret_list.append([trade_date, stk_id, ind_name] + tmp_list)
ret_df = pd.DataFrame(ret_list, columns=['交易日期', '股票代码', '申万一级行业', '选取个数', 
                                         '历史未来corr', '历史未来rank_corr'])
corr_perc = pd.DataFrame()
for perc in [0, 10, 30, 50, 70, 90, 100]:
    tmp = ret_df.groupby(['申万一级行业']).apply(lambda x: np.percentile(x['历史未来rank_corr'].values, perc))
    corr_perc = pd.concat([corr_perc, tmp], axis=1)
tmp2 = ret_df.groupby(['申万一级行业'])['股票代码'].apply(lambda x: x.count())
corr_perc = pd.concat([corr_perc, tmp2], axis=1)
corr_perc.columns = [f'{x}%分位数' for x in [0, 10, 30, 50, 70, 90, 100]] + ['个数']
# util.save_df2xls(ret_df, other_stats_path, 'corr_distribution2.xlsx')
ret_df4 = corr_perc.copy()


#%% 第三种测试
filename = f'新版本_1_(-1, 1)_(-1, 1)_(120, 120)_95_5_{start_date}_{end_date}_corrResultV4.pkl'
hedge_list = pd.read_pickle(hedge_path + filename)
sw1 = getData.get_daily_1factor('SW1', date_list=tradeDate.get_date_range(20161201, tradeDate.get_today()))

ret_list = list()
for hedge in tqdm(hedge_list):
    stk_id = hedge['stk_id']
    trade_date = hedge['date']
    ind_code = sw1.loc[trade_date, stk_id]
    ind_name = indName.sw_level1[ind_code]
    tmp_list = hedge['hedge_list'][0]['hedge_value']
    ret_list.append([trade_date, stk_id, ind_name] + tmp_list)
ret_df = pd.DataFrame(ret_list, columns=['交易日期', '股票代码', '申万一级行业', '选取个数',
                                         '前后交集', '交集所占比例'])
corr_perc = pd.DataFrame()
for perc in [0, 10, 30, 50, 70, 90, 100]:
    tmp = ret_df.groupby(['申万一级行业']).apply(lambda x: np.percentile(x['交集所占比例'].values, perc))
    corr_perc = pd.concat([corr_perc, tmp], axis=1)
tmp2 = ret_df.groupby(['申万一级行业'])['股票代码'].apply(lambda x: x.count())
corr_perc = pd.concat([corr_perc, tmp2], axis=1)
corr_perc.columns = [f'{x}%分位数' for x in [0, 10, 30, 50, 70, 90, 100]] + ['个数']
# util.save_df2xls(ret_df, other_stats_path, 'corr_distribution2.xlsx')
ret_df5 = corr_perc.copy()

ret_dict = {'1': ret_df1,
            '2_正负': ret_df2,
            '2_绝对值': ret_df3,
            '3': ret_df4,
            '4': ret_df5,
            '5': ret_df6}
util.save_dict2xls(ret_dict, other_stats_path, '20220517相关性统计结果_分年度3.xlsx')
