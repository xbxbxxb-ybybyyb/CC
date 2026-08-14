# coding: utf-8
# Author：fengchi863
# Date ：2022/12/5 20:15

import pandas as pd
import numpy as np
from dataApi import getData, tradeDate
from dataApi.indName import sw_level2, sw_level3
from dataApi.stockList import trans_windcode2int as Wc2Int, trans_int2windcode as Int2Wc
from xquant.factordata import FactorData

junk_path = '/data/user/015614/junkData/'

# date_list2014 = tradeDate.get_date_range(20160101, 20211210)
# date_list2021 = tradeDate.get_date_range(20211213, 20221125)
#
# sw2_2014 = getData.get_daily_1factor('SW2', date_list=date_list2014)
# sw2_2014 = sw2_2014.fillna(method='bfill').dropna(how='all', axis=1)
# sw2_2014 = sw2_2014.applymap(lambda x: sw_level2[int(x)] if ~np.isnan(x) else 'None')
# sw2_2021 = pd.read_pickle(junk_path + 'sw2_2021.pkl')
# sw2_2021 = pd.concat([sw2_2014, sw2_2021], axis=0)
#
# sw3_2014 = getData.get_daily_1factor('SW3', date_list=date_list2014)
# sw3_2014 = sw3_2014.fillna(method='bfill').dropna(how='all', axis=1)
# sw3_2014 = sw3_2014.applymap(lambda x: sw_level3[int(x)] if ~np.isnan(x) else 'None')
# sw3_2021 = pd.read_pickle(junk_path + 'sw3_2021.pkl')
# sw3_2021 = pd.concat([sw3_2014, sw3_2021], axis=0)
#
# citics2_2021 = pd.read_pickle(junk_path + 'citics2_2021.pkl')


#%% 基础数据
basic_zt_fname = '/data/group/800463/sunss/for_fc/数据/jupiterN_basic_20150901_20221125.pkl'
# profit_fname = '/data/group/800463/sunss/for_xly/europa/newProfit/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.pkl'
profit_fname0 = '/data/group/800463/xiely/save-file/forFc/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.pkl'
profit_fname = '/data/group/800463/project/project1_prod/LabelProfit/LabelProfit_zt_twap_0.10_800_190_SH450_SZ100.h5'
basic = pd.read_pickle(basic_zt_fname)
basic['trade_date'] = basic.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
basic['stk_id'] = basic.index.get_level_values(1).map(Wc2Int).tolist()
basic = basic.query('trade_date >= 20160101')
basic['pct'] = pd.read_hdf(profit_fname).reindex(index=basic.index)['pct'] - 0.002
basic['pct0'] = pd.read_pickle(profit_fname0).reindex(index=basic.index)['pct'] - 0.002
basic2022_origin = basic.query('trade_date >= 20220101')


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
# signal2022_origin = signal.query('trade_date >= 20220101')

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
signal2022_origin = signal2022.query('trade_date >= 20220101')

# 下面只统计2022的
ZT_time_list = [(93000000, 95959999), (100000000, 102959999), (103000000, 105959999),
                (110000000, 113000000), (130000000, 132959999), (133000000, 135959999),
                (140000000, 142959999), (143000000, 150000000)]

stats_df = pd.DataFrame(index=['样本数量', 'pct均值', 'pct中位数', 'pct标准差', 'pct胜率', '形态4比例'],
                        columns=pd.MultiIndex.from_product([[f'H{idx}' for idx in range(1, 9)], ['basic2022全样本', 'signal2022全样本']]))
for idx, time_tuple in enumerate(ZT_time_list):
    period = f'H{idx + 1}'
    basic2022 = basic2022_origin.query(f'ZT_Time >= {time_tuple[0]} & ZT_Time <= {time_tuple[1]}')
    signal2022 = signal2022_origin.query(f'ZT_Time >= {time_tuple[0]} & ZT_Time <= {time_tuple[1]}')

    # basic2022['CITICS2'] = basic2022[['trade_date', 'stk_id']].apply(lambda x: citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
    # signal2022['CITICS2'] = signal2022[['trade_date', 'stk_id']].apply(lambda x: citics2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
    # basic2022['SW2'] = basic2022[['trade_date', 'stk_id']].apply(lambda x: sw2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
    # signal2022['SW2'] = signal2022[['trade_date', 'stk_id']].apply(lambda x: sw2_2021.loc[x['trade_date'], x['stk_id']], axis=1)
    # basic2022['SW3'] = basic2022[['trade_date', 'stk_id']].apply(lambda x: sw3_2021.loc[x['trade_date'], x['stk_id']], axis=1)
    # signal2022['SW3'] = signal2022[['trade_date', 'stk_id']].apply(lambda x: sw3_2021.loc[x['trade_date'], x['stk_id']], axis=1)

    # for ind in ['SW3', 'SW2', 'CITICS2']:
    stats_df.loc['样本数量', (period, 'basic2022全样本')] = basic2022.shape[0]
    stats_df.loc['pct均值', (period, 'basic2022全样本')] = basic2022['pct'].mean()
    stats_df.loc['pct中位数', (period, 'basic2022全样本')] = basic2022['pct'].median()
    stats_df.loc['pct标准差', (period, 'basic2022全样本')] = basic2022['pct'].std()
    stats_df.loc['pct胜率', (period, 'basic2022全样本')] = basic2022.query('pct > 0').shape[0] / basic2022.shape[0] if signal2022.shape[0] != 0 else 0
    stats_df.loc['形态4比例', (period, 'basic2022全样本')] = basic2022.query('label_pattern == 4').shape[0] / basic2022.shape[0] if signal2022.shape[0] != 0 else 0

    stats_df.loc['样本数量', (period, 'signal2022全样本')] = signal2022.shape[0]
    stats_df.loc['pct均值', (period, 'signal2022全样本')] = signal2022['pct'].mean()
    stats_df.loc['pct中位数', (period, 'signal2022全样本')] = signal2022['pct'].median()
    stats_df.loc['pct标准差', (period, 'signal2022全样本')] = signal2022['pct'].std()
    stats_df.loc['pct胜率', (period, 'signal2022全样本')] = signal2022.query('pct > 0').shape[0] / signal2022.shape[0] if signal2022.shape[0] != 0 else 0
    stats_df.loc['形态4比例', (period, 'signal2022全样本')] = signal2022.query('label_pattern == 4').shape[0] / signal2022.shape[0] if signal2022.shape[0] != 0 else 0

check = stats_df.T
from dataApi.sendInfo import send_file
send_file(check)