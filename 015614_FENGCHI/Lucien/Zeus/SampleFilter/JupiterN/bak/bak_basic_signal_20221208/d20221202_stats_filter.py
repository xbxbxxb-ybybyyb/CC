# coding: utf-8
# Author：fengchi863
# Date ：2022/11/30 13:44

import pandas as pd
import numpy as np
from dataApi import getData, tradeDate
from dataApi.indName import citics_level2
from dataApi.stockList import trans_windcode2int as Wc2Int, trans_int2windcode as Int2Wc
from xquant.factordata import FactorData
from tqdm import tqdm

junk_path = '/data/user/015614/junkData/'

basic_zt_fname = '/data/group/800463/sunss/for_fc/数据/jupiterN_basic_20150901_20221125.pkl'
# profit_fname = '/data/group/800463/sunss/for_xly/europa/newProfit/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.pkl'
# profit_fname = '/data/group/800463/xiely/save-file/forFc/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.pkl'
profit_fname = '/data/group/800463/project/project1_prod/LabelProfit/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
basic = pd.read_pickle(basic_zt_fname)
basic['trade_date'] = basic.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
basic['stk_id'] = basic.index.get_level_values(1).map(Wc2Int).tolist()
basic = basic.query('trade_date >= 20160101')
basic['pct'] = pd.read_hdf(profit_fname).reindex(index=basic.index)['pct'] - 0.002
basic2022 = basic.query('trade_date >= 20220101')

signal_fname = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/jupiter成交记录-20221125.xlsx'
signal = pd.read_excel(signal_fname, sheet_name='累计买入明细')
signal = signal.query('last_is_zt == False')    # 这个条件筛选得到jupiterN样本
signal['trade_date'] = signal['发生日期'].map(lambda x: int(x.replace('-', ''))).tolist()
signal['stk_id'] = signal['证券代码'].map(lambda x: Wc2Int(x))
signal = signal.query('trade_date >= 20210101')
signal['dt'] = signal['发生日期'].apply(lambda x: pd.to_datetime(x))
signal = signal.set_index(['dt', '证券代码'])
signal['ZT_Time'] = basic.reindex(index=signal.index)['ZT_Time']
signal['pct'] = pd.read_hdf(profit_fname).reindex(index=signal.index)['pct'] - 0.002
signal['label_pattern'] = basic.reindex(index=signal.index)['label_pattern']
# signal2022 = signal.query('trade_date >= 20220101')

# 20221206 将signal2022的信号进行更换
signal2022_fname = '/data/group/800463/wangj/for_fc/20220101_20221125_JupiterN_votesignal.pkl'
signal2022 = pd.read_pickle(signal2022_fname)
signal2022 = pd.DataFrame(signal2022[signal2022 >= 4])
signal2022['trade_date'] = signal2022.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
signal2022['stk_id'] = signal2022.index.get_level_values(1).map(lambda x: Wc2Int(x))
signal2022['dt'] = signal2022.index.get_level_values(0)
signal2022['ZT_Time'] = basic.reindex(index=signal2022.index)['ZT_Time']
signal2022['pct'] = pd.read_hdf(profit_fname).reindex(index=signal2022.index)['pct'] - 0.002
signal2022['label_pattern'] = basic.reindex(index=signal2022.index)['label_pattern']

#%% 1.1、获取中信二级行业
date_list2014 = tradeDate.get_date_range(20160101, 20211210)
date_list2021 = tradeDate.get_date_range(20160101, 20221125)

#%% 1.2、获取中信二级行业对应关系，使用hsi获取
try:
    citics2_2021 = pd.read_pickle(junk_path + 'citics2_2021.pkl')
except FileNotFoundError:
    fd = FactorData()
    basic_2021sw_stk_list = list(set(basic.query('trade_date >= 20160101')['stk_id'].map(Int2Wc).tolist()))
    citics2_2021 = pd.DataFrame()
    for _date in tqdm(date_list2021):
        tmp = fd.hsi(basic_2021sw_stk_list, _date, 'CITICS', 2)
        tmp['trade_date'] = _date
        citics2_2021 = pd.concat([citics2_2021, tmp], axis=0)
    citics2_2021 = citics2_2021.pivot('trade_date', 'stock', 'industry_name')
    citics2_2021.columns = citics2_2021.columns.map(Wc2Int)
    citics2_2021.to_pickle(junk_path + 'citics2_2021.pkl')
citics2 = citics2_2021

basic['CITICS2'] = basic[['trade_date', 'stk_id']].apply(lambda x: citics2.loc[x['trade_date'], x['stk_id']] if x['trade_date'] <= 20211210 else citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
basic2022['CITICS2'] = basic2022[['trade_date', 'stk_id']].apply(lambda x: citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
signal['CITICS2'] = signal[['trade_date', 'stk_id']].apply(lambda x: citics2.loc[x['trade_date'], x['stk_id']] if x['trade_date'] <= 20211210 else citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
signal2022['CITICS2'] = signal2022[['trade_date', 'stk_id']].apply(lambda x: citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)

#%% 统计全样本的
stats_df = pd.DataFrame(index=['样本数量', 'pct均值', 'pct中位数', 'pct标准差', 'pct胜率', '形态4比例'])
stats_df.loc['样本数量', 'basic全样本'] = basic.shape[0]
stats_df.loc['pct均值', 'basic全样本'] = basic['pct'].mean()
stats_df.loc['pct中位数', 'basic全样本'] = basic['pct'].median()
stats_df.loc['pct标准差', 'basic全样本'] = basic['pct'].std()
stats_df.loc['pct胜率', 'basic全样本'] = basic.query('pct > 0').shape[0] / basic.shape[0]
stats_df.loc['形态4比例', 'basic全样本'] = basic.query('label_pattern == 4').shape[0] / basic.shape[0]

stats_df.loc['样本数量', 'signal全样本'] = signal.shape[0]
stats_df.loc['pct均值', 'signal全样本'] = signal['pct'].mean()
stats_df.loc['pct中位数', 'signal全样本'] = signal['pct'].median()
stats_df.loc['pct标准差', 'signal全样本'] = signal['pct'].std()
stats_df.loc['pct胜率', 'signal全样本'] = signal.query('pct > 0').shape[0] / signal.shape[0]
stats_df.loc['形态4比例', 'signal全样本'] = signal.query('label_pattern == 4').shape[0] / signal.shape[0]

#%% 统计ZT_Time靠前的第一个
basic = basic.sort_values(['trade_date', 'CITICS2', 'ZT_Time'])
# basic_group1  = basic.groupby(['trade_date', 'CITICS2']).agg('first') # 改用head进行筛选
basic_group1  = basic.groupby(['trade_date', 'CITICS2']).head(1)
signal = signal.sort_values(['trade_date', 'CITICS2', 'ZT_Time'])
# signal_group1  = signal.groupby(['trade_date', 'CITICS2']).agg('first')
signal_group1  = signal.groupby(['trade_date', 'CITICS2']).head(1)

stats_df.loc['样本数量', 'basic_first_1'] = basic_group1.shape[0]
stats_df.loc['pct均值', 'basic_first_1'] = basic_group1['pct'].mean()
stats_df.loc['pct中位数', 'basic_first_1'] = basic_group1['pct'].median()
stats_df.loc['pct标准差', 'basic_first_1'] = basic_group1['pct'].std()
stats_df.loc['pct胜率', 'basic_first_1'] = basic_group1.query('pct > 0').shape[0] / basic_group1.shape[0]
stats_df.loc['形态4比例', 'basic_first_1'] = basic_group1.query('label_pattern == 4').shape[0] / basic_group1.shape[0]

stats_df.loc['样本数量', 'signal_first_1'] = signal_group1.shape[0]
stats_df.loc['pct均值', 'signal_first_1'] = signal_group1['pct'].mean()
stats_df.loc['pct中位数', 'signal_first_1'] = signal_group1['pct'].median()
stats_df.loc['pct标准差', 'signal_first_1'] = signal_group1['pct'].std()
stats_df.loc['pct胜率', 'signal_first_1'] = signal_group1.query('pct > 0').shape[0] / signal_group1.shape[0]
stats_df.loc['形态4比例', 'signal_first_1'] = signal_group1.query('label_pattern == 4').shape[0] / signal_group1.shape[0]

#%% 统计ZT_Time靠前的前两个
basic_group2 = basic.groupby(['trade_date', 'CITICS2']).head(2)
signal_group2  = signal.groupby(['trade_date', 'CITICS2']).head(2)
stats_df.loc['样本数量', 'basic_first_2'] = basic_group2.shape[0]
stats_df.loc['pct均值', 'basic_first_2'] = basic_group2['pct'].mean()
stats_df.loc['pct中位数', 'basic_first_2'] = basic_group2['pct'].median()
stats_df.loc['pct标准差', 'basic_first_2'] = basic_group2['pct'].std()
stats_df.loc['pct胜率', 'basic_first_2'] = basic_group2.query('pct > 0').shape[0] / basic_group2.shape[0]
stats_df.loc['形态4比例', 'basic_first_2'] = basic_group2.query('label_pattern == 4').shape[0] / basic_group2.shape[0]

stats_df.loc['样本数量', 'signal_first_2'] = signal_group2.shape[0]
stats_df.loc['pct均值', 'signal_first_2'] = signal_group2['pct'].mean()
stats_df.loc['pct中位数', 'signal_first_2'] = signal_group2['pct'].median()
stats_df.loc['pct标准差', 'signal_first_2'] = signal_group2['pct'].std()
stats_df.loc['pct胜率', 'signal_first_2'] = signal_group2.query('pct > 0').shape[0] / signal_group2.shape[0]
stats_df.loc['形态4比例', 'signal_first_2'] = signal_group2.query('label_pattern == 4').shape[0] / signal_group2.shape[0]

check = stats_df.T

#%% 统计2022年的比例
stats2022_df = pd.DataFrame(index=['样本数量', 'pct均值', 'pct中位数', 'pct胜率', '形态4比例'])

stats2022_df.loc['样本数量', 'basic2022全样本'] = basic2022.shape[0]
stats2022_df.loc['pct均值', 'basic2022全样本'] = basic2022['pct'].mean()
stats2022_df.loc['pct中位数', 'basic2022全样本'] = basic2022['pct'].median()
stats2022_df.loc['pct标准差', 'basic2022全样本'] = basic2022['pct'].std()
stats2022_df.loc['pct胜率', 'basic2022全样本'] = basic2022.query('pct > 0').shape[0] / basic2022.shape[0]
stats2022_df.loc['形态4比例', 'basic2022全样本'] = basic2022.query('label_pattern == 4').shape[0] / basic2022.shape[0]

stats2022_df.loc['样本数量', 'signal2022全样本'] = signal2022.shape[0]
stats2022_df.loc['pct均值', 'signal2022全样本'] = signal2022['pct'].mean()
stats2022_df.loc['pct中位数', 'signal2022全样本'] = signal2022['pct'].median()
stats2022_df.loc['pct标准差', 'signal2022全样本'] = signal2022['pct'].std()
stats2022_df.loc['pct胜率', 'signal2022全样本'] = signal2022.query('pct > 0').shape[0] / signal2022.shape[0]
stats2022_df.loc['形态4比例', 'signal2022全样本'] = signal2022.query('label_pattern == 4').shape[0] / signal2022.shape[0]

basic2022 = basic2022.sort_values(['trade_date', 'CITICS2', 'ZT_Time'])
# basic2022_group1  = basic2022.groupby(['trade_date', 'CITICS2']).agg('first') # 改用head进行筛选
basic2022_group1  = basic2022.groupby(['trade_date', 'CITICS2']).head(1)
signal2022 = signal2022.sort_values(['trade_date', 'CITICS2', 'ZT_Time'])
# signal2022_group1  = signal2022.groupby(['trade_date', 'CITICS2']).agg('first')
signal2022_group1  = signal2022.groupby(['trade_date', 'CITICS2']).head(1)

stats2022_df.loc['样本数量', 'basic2022_first_1'] = basic2022_group1.shape[0]
stats2022_df.loc['pct均值', 'basic2022_first_1'] = basic2022_group1['pct'].mean()
stats2022_df.loc['pct中位数', 'basic2022_first_1'] = basic2022_group1['pct'].median()
stats2022_df.loc['pct标准差', 'basic2022_first_1'] = basic2022_group1['pct'].std()
stats2022_df.loc['pct胜率', 'basic2022_first_1'] = basic2022_group1.query('pct > 0').shape[0] / basic2022_group1.shape[0]
stats2022_df.loc['形态4比例', 'basic2022_first_1'] = basic2022_group1.query('label_pattern == 4').shape[0] / basic2022_group1.shape[0]

stats2022_df.loc['样本数量', 'signal2022_first_1'] = signal2022_group1.shape[0]
stats2022_df.loc['pct均值', 'signal2022_first_1'] = signal2022_group1['pct'].mean()
stats2022_df.loc['pct中位数', 'signal2022_first_1'] = signal2022_group1['pct'].median()
stats2022_df.loc['pct标准差', 'signal2022_first_1'] = signal2022_group1['pct'].std()
stats2022_df.loc['pct胜率', 'signal2022_first_1'] = signal2022_group1.query('pct > 0').shape[0] / signal2022_group1.shape[0]
stats2022_df.loc['形态4比例', 'signal2022_first_1'] = signal2022_group1.query('label_pattern == 4').shape[0] / signal2022_group1.shape[0]

basic2022_group2 = basic2022.groupby(['trade_date', 'CITICS2']).head(2)
signal2022_group2  = signal2022.groupby(['trade_date', 'CITICS2']).head(2)
stats2022_df.loc['样本数量', 'basic2022_first_2'] = basic2022_group2.shape[0]
stats2022_df.loc['pct均值', 'basic2022_first_2'] = basic2022_group2['pct'].mean()
stats2022_df.loc['pct中位数', 'basic2022_first_2'] = basic2022_group2['pct'].median()
stats2022_df.loc['pct标准差', 'basic2022_first_2'] = basic2022_group2['pct'].std()
stats2022_df.loc['pct胜率', 'basic2022_first_2'] = basic2022_group2.query('pct > 0').shape[0] / basic2022_group2.shape[0]
stats2022_df.loc['形态4比例', 'basic2022_first_2'] = basic2022_group2.query('label_pattern == 4').shape[0] / basic2022_group2.shape[0]

stats2022_df.loc['样本数量', 'signal2022_first_2'] = signal2022_group2.shape[0]
stats2022_df.loc['pct均值', 'signal2022_first_2'] = signal2022_group2['pct'].mean()
stats2022_df.loc['pct中位数', 'signal2022_first_2'] = signal2022_group2['pct'].median()
stats2022_df.loc['pct标准差', 'signal2022_first_2'] = signal2022_group2['pct'].std()
stats2022_df.loc['pct胜率', 'signal2022_first_2'] = signal2022_group2.query('pct > 0').shape[0] / signal2022_group2.shape[0]
stats2022_df.loc['形态4比例', 'signal2022_first_2'] = signal2022_group2.query('label_pattern == 4').shape[0] / signal2022_group2.shape[0]

#%% 只算2022年的行业内的第一个涨停的，前10个行业
basic2022_group1_first10ind = basic2022_group1.sort_values(['trade_date', 'ZT_Time']).groupby('trade_date').head(10)
signal2022_group1_first10ind = signal2022_group1.sort_values(['trade_date', 'ZT_Time']).groupby('trade_date').head(10)

stats2022_df.loc['样本数量', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind.shape[0]
stats2022_df.loc['pct均值', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind['pct'].mean()
stats2022_df.loc['pct中位数', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind['pct'].median()
stats2022_df.loc['pct标准差', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind['pct'].std()
stats2022_df.loc['pct胜率', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind.query('pct > 0').shape[0] / basic2022_group1_first10ind.shape[0]
stats2022_df.loc['形态4比例', 'basic2022_group1_first10ind'] = basic2022_group1_first10ind.query('label_pattern == 4').shape[0] / basic2022_group1_first10ind.shape[0]

stats2022_df.loc['样本数量', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind.shape[0]
stats2022_df.loc['pct均值', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind['pct'].mean()
stats2022_df.loc['pct中位数', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind['pct'].median()
stats2022_df.loc['pct标准差', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind['pct'].std()
stats2022_df.loc['pct胜率', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind.query('pct > 0').shape[0] / signal2022_group1_first10ind.shape[0]
stats2022_df.loc['形态4比例', 'signal2022_group1_first10ind'] = signal2022_group1_first10ind.query('label_pattern == 4').shape[0] / signal2022_group1_first10ind.shape[0]

check2 = stats2022_df.T

# 20221206 统计first10ind 不同时间段分布
time_dist_df = pd.DataFrame(index=['basic2022_group1_first10ind', 'signal2022_group1_first10ind',
                                   'basic2022_group1_first10ind_num', 'signal2022_group1_first10ind_num',
                                   'basic2022_group1_first10ind_pct_mean', 'signal2022_group1_first10ind_pct_mean'])
ZT_time_list = [(93000000, 95959999), (100000000, 102959999), (103000000, 105959999),
                (110000000, 113000000), (130000000, 132959999), (133000000, 135959999),
                (140000000, 142959999), (143000000, 150000000)]
for idx, time_tuple in enumerate(ZT_time_list):
    period = f'H{idx + 1}'
    tmp_basic2022 = basic2022_group1_first10ind.query(f'ZT_Time >= {time_tuple[0]} & ZT_Time <= {time_tuple[1]}')
    tmp_signal2022 = signal2022_group1_first10ind.query(f'ZT_Time >= {time_tuple[0]} & ZT_Time <= {time_tuple[1]}')
    time_dist_df.loc['basic2022_group1_first10ind', period] = len(tmp_basic2022) / len(basic2022_group1_first10ind)
    time_dist_df.loc['signal2022_group1_first10ind', period] = len(tmp_signal2022) / len(basic2022_group1_first10ind)
    time_dist_df.loc['basic2022_group1_first10ind_num', period] = len(tmp_basic2022)
    time_dist_df.loc['signal2022_group1_first10ind_num', period] = len(tmp_signal2022)
    time_dist_df.loc['basic2022_group1_first10ind_pct_mean', period] = tmp_basic2022['pct'].mean()
    time_dist_df.loc['signal2022_group1_first10ind_pct_mean', period] = tmp_signal2022['pct'].mean()

check3 = time_dist_df.T

res = pd.concat([check, check2], axis=0)
from dataApi.sendInfo import send_file
send_file(res)
send_file(check3)

"""
#%% 20221130统计二级行业的数量
fd = FactorData()
check = fd.hind('CITICS', 2)
check2021 = fd.hind('CITICS', 2)

# 统计行业成分股数量，沈老师负责落地
# result1 = fd.hset('INDUSTRY', '20220702', 'CITICS.46')   # 需要参考行业说明表

# 统计所有个股的行业
# 2021
from dataApi import stockList
has_appear_stk_list = stockList.get_all_stock_ever_appear(20221130)
has_appear_stk_code_list = list(map(Int2Wc, has_appear_stk_list))
citics2_2021 = pd.DataFrame()
for _date in tqdm([20221124, 20221125]):
    tmp = fd.hsi(has_appear_stk_code_list, _date, 'CITICS', 2)
    tmp['trade_date'] = _date
    citics2_2021 = pd.concat([citics2_2021, tmp], axis=0)
citics2_2021 = citics2_2021.pivot('trade_date', 'stock', 'industry_name')
citics2_2021.columns = citics2_2021.columns.map(Wc2Int)
check2021 = pd.DataFrame(citics2_2021.stack().reset_index()).groupby(['trade_date', 0])['stock'].count()
check2021 = check2021.reset_index().query('trade_date==20221125')
print('大于20个成分股的概念数量有：', (check2021['stock'] > 20).sum())
print('大于10个成分股的概念数量有：', (check2021['stock'] > 10).sum())
print('大于5个成分股的概念数量有：', (check2021['stock'] > 5).sum())
"""