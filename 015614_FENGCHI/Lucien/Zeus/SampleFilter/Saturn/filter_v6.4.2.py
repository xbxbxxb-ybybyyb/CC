# coding: utf-8
# Author：fengchi863
# Date ：2022/10/27 11:24

"""
根据概念进行划分
板块内close相对于limit_max的跌幅超过0.03的部分进行剔除
"""

from Zeus.Saturn.v3_0_23.path_conf import saturn_data_test_fpath
import pandas as pd
import numpy as np
from LucienUtil import IO
from dataApi import getData, stockList, tradeDate

# 这里可以设置多个参数，0.01 0.02 0.03 0.04 0.05 分别run一次程序
LIMIT_DOWN = -0.03

def calc_limit_max(pre_close):
    cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3'), pre_close.columns.tolist()))
    not_cyb = list(filter(lambda x: stockList.trans_int2windcode(x).startswith('3') - 1, pre_close.columns.tolist()))
    if pre_close.index[0] >= 20200824:
        pre_close_cyb = pre_close[cyb]
        pre_close_not_cyb = pre_close[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]
        return limit_max
    elif pre_close.index[-1] < 20200824:
        limit_max = (pre_close * 100 * 1.1 + 0.5).apply(np.floor) / 100
        return limit_max
    else:
        after_20200824 = pre_close.loc[20200824:]
        before_20200824 = pre_close.loc[:20200823]
        limit_max_before_20200824 = (before_20200824 * 100 * 1.1 + 0.5).apply(np.floor) / 100

        pre_close_cyb = after_20200824[cyb]
        pre_close_not_cyb = after_20200824[not_cyb]
        limit_max_cyb = (pre_close_cyb * 100 * 1.2 + 0.5).apply(np.floor) / 100
        limit_max_not_cyb = (pre_close_not_cyb * 100 * 1.1 + 0.5).apply(np.floor) / 100
        limit_max_after_20200824 = pd.concat([limit_max_cyb, limit_max_not_cyb], axis=1)[pre_close.columns]

        limit_max = pd.concat([limit_max_before_20200824, limit_max_after_20200824], axis=0)
    return limit_max

# profit
profit = pd.read_hdf('/data/group/800463/project/project2_prod/profit_backtest/p2_profit_931_0.20_0.10_500_1500.h5')
label = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/sft/sft_basic_origin.h5')

saturn_sample = pd.read_pickle(saturn_data_test_fpath)
saturn_sample = saturn_sample[['saturn_dt_last_zt_1', 'saturn_Lzt_ZT_Time', 'label_v2o10d1']]
saturn_sample = saturn_sample.join(label[['label_T_close_is_zt']])
saturn_sample = saturn_sample.join(profit[['pct']] - 0.004)  # 这里设置了交易费率
saturn_sample['trade_date'] = saturn_sample.index.get_level_values(0)
saturn_sample['trade_date'] = saturn_sample['trade_date'].map(lambda x: int(x.strftime('%Y%m%d')))
saturn_sample['stk_code'] = saturn_sample.index.get_level_values(1)
saturn_sample['last_trade_date'] = saturn_sample['saturn_dt_last_zt_1'].map(lambda x: str(int(x)))
saturn_sample['last_trade_dt'] = saturn_sample['saturn_dt_last_zt_1'].map(lambda x: pd.to_datetime(str(int(x))))
saturn_sample = saturn_sample.set_index(['last_trade_dt', 'stk_code'])
saturn_sample.index.names = ['dt', 'Ticker']

jupiter_sample = IO.read_data([20150101, 20201231], alt='/data/group/800463/fengc/daily/concept/jupiter_concept.h5')
saturn_sample = saturn_sample.join(jupiter_sample)
origin_saturn_sample = saturn_sample.copy() # 原始的saturn全样本
saturn_sample['stk_code'] = saturn_sample.index.get_level_values(1)

# 计算一些基础数据，统计是否炸板
start_date, end_date = 20141201, 20201231
stk_pool = stockList.clean_stock_list(no_ST=True, least_live_days=1, least_normal_days=1, no_pause=True, least_recover_days=0, start_date=start_date, end_date=end_date)
stk_list = stk_pool.iloc[-1].index.tolist()
date_list = tradeDate.get_date_range(start_date, end_date)
pre_close = getData.get_daily_1factor('pre_close', date_list=date_list, code_list=stk_list)
limit_max = calc_limit_max(pre_close)
high = getData.get_daily_1factor('high', date_list=date_list, code_list=stk_list)
close = getData.get_daily_1factor('close', date_list=date_list, code_list=stk_list)
zb = pd.DataFrame(((close != limit_max) & (high == limit_max))) & stk_pool
limit_down = (close - high) / pre_close

# 是否炸板
jupiter_sample['stk_id'] = jupiter_sample.index.get_level_values(1).map(lambda x: stockList.trans_windcode2int(x))
jupiter_sample['trade_date'] = jupiter_sample.index.get_level_values(0).map(lambda x: x.strftime('%Y%m%d'))
jupiter_sample['is_zb'] = jupiter_sample[['trade_date', 'stk_id']].apply(lambda x: zb.loc[int(x['trade_date']), x['stk_id']]
                           if x['stk_id'] in zb.columns.tolist() else np.nan, axis=1)
jupiter_sample['limit_down'] = jupiter_sample[['trade_date', 'stk_id']].apply(lambda x: limit_down.loc[int(x['trade_date']), x['stk_id']]
                           if x['stk_id'] in limit_down.columns.tolist() else np.nan, axis=1)
jupiter_sample = jupiter_sample.query('概念涨停数量 >= 3')
jupiter_sample['is_zb'] = jupiter_sample['is_zb'].astype(int)
group_limit_down_mean = jupiter_sample.groupby(['trade_date', '概念名称'])['limit_down'].mean()

def wrapper(limit_down):
    drop_indexes = group_limit_down_mean[group_limit_down_mean < limit_down].index
    filtered_jupiter_sample = jupiter_sample.reset_index().set_index(['trade_date', '概念名称']).drop(drop_indexes)

    # TODO: warning!!! saturn中的trade_date是策略触发日期，不是涨停那一天，不能拿这个日期取筛选概念
    # 这里原本写了个BUG，就是用触发日期来进行的炸板筛选，这就导致选择的都是当天炸板率低的板块进行的触发，所以结果会异常的好，也符合逻辑
    saturn_sample['last_trade_date'] = saturn_sample['last_trade_date'].astype(int).astype(str) # 如果把last_trade_date改成trade_date, 那就是用当天的概念进行筛选了
    saturn_reindexed = saturn_sample.reset_index().set_index(['last_trade_date', '概念名称'])
    saturn_indexes = saturn_reindexed.index
    filtered_jupiter_sample_indexes = filtered_jupiter_sample.index
    common_indexes = list(set(saturn_indexes).intersection(set(filtered_jupiter_sample_indexes)))
    saturn_reindexed = saturn_reindexed.loc[common_indexes]
    filtered_saturn_sample = saturn_reindexed.reset_index().set_index(['dt', 'Ticker']).sort_index()

    #%% 进行样本统计 date20220930
    stats_df = pd.DataFrame(index=['FilterV6.4.2', '全样本'])
    stats_df.loc['FilterV6.4.2', '样本个数'] = len(filtered_saturn_sample)
    stats_df.loc['FilterV6.4.2', 'pct胜率'] = (filtered_saturn_sample['pct'] > 0).sum() / len(filtered_saturn_sample)
    stats_df.loc['FilterV6.4.2', 'pct均值'] = filtered_saturn_sample['pct'].mean()
    stats_df.loc['FilterV6.4.2', 'pct中位数'] = filtered_saturn_sample['pct'].median()
    stats_df.loc['FilterV6.4.2', 'pct_std'] = filtered_saturn_sample['pct'].std()
    stats_df.loc['FilterV6.4.2', 'label胜率'] = (filtered_saturn_sample['label_v2o10d1'] > 0).sum() / len(filtered_saturn_sample)
    stats_df.loc['FilterV6.4.2', 'label均值'] = filtered_saturn_sample['label_v2o10d1'].mean()
    stats_df.loc['FilterV6.4.2', 'label中位数'] = filtered_saturn_sample['label_v2o10d1'].median()
    stats_df.loc['FilterV6.4.2', 'label_std'] = filtered_saturn_sample['label_v2o10d1'].std()
    stats_df.loc['FilterV6.4.2', 'T日收盘涨停比例'] = filtered_saturn_sample['label_T_close_is_zt'].sum() / len(filtered_saturn_sample)

    stats_df.loc['全样本', '样本个数'] = len(origin_saturn_sample)
    stats_df.loc['全样本', 'pct胜率'] = (origin_saturn_sample['pct'] > 0).sum() / len(origin_saturn_sample)
    stats_df.loc['全样本', 'pct均值'] = origin_saturn_sample['pct'].mean()
    stats_df.loc['全样本', 'pct中位数'] = origin_saturn_sample['pct'].median()
    stats_df.loc['全样本', 'pct_std'] = origin_saturn_sample['pct'].std()
    stats_df.loc['全样本', 'label胜率'] = (origin_saturn_sample['label_v2o10d1'] > 0).sum() / len(origin_saturn_sample)
    stats_df.loc['全样本', 'label均值'] = origin_saturn_sample['label_v2o10d1'].mean()
    stats_df.loc['全样本', 'label中位数'] = origin_saturn_sample['label_v2o10d1'].median()
    stats_df.loc['全样本', 'label_std'] = origin_saturn_sample['label_v2o10d1'].std()
    stats_df.loc['全样本', 'T日收盘涨停比例'] = origin_saturn_sample['label_T_close_is_zt'].sum() / len(origin_saturn_sample)

    stats_df = stats_df.T
    return stats_df

limit_down_list = [-0.02, -0.05, -0.1, -0.15, -0.2]
stats_df = pd.DataFrame()
for limit_down in limit_down_list:
    tmp_stats_df = wrapper(limit_down)
    stats_df = pd.concat([stats_df, pd.DataFrame(index=[limit_down]), tmp_stats_df], axis=0)

""" 测试用，这种拼接方式可以执行
limit_down_list = [0, -0.05, -0.1, -0.15, -0.2, -0.25, -0.3, -0.35, -0.4]
stats_df = pd.DataFrame()
for limit_down in limit_down_list:
    # tmp_stats_df = wrapper(limit_down)
    tmp_stats_df = pd.DataFrame(np.zeros_like([[2,2], [2, 2]]), index=[1,2], columns=[1,2])
    stats_df = pd.concat([stats_df, pd.DataFrame([0.03, np.nan]).T, tmp_stats_df], axis=0)
"""
stats_df = stats_df.set_index(0)
from dataApi.sendInfo import send_file
send_file(stats_df)