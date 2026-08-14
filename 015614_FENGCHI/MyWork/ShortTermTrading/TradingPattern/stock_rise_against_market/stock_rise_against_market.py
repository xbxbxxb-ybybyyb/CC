# coding: utf-8
# Author：fengchi863
# Date ：2020/9/24 13:24

'''
模式一：逆势上涨个股
大盘指标：
1、	大盘近一段时期日间位于下跌趋势（涨跌幅<0且下跌天数>上涨天数）
个股指标：
2、	个股近一段时间逆势上涨
3、	个股价格在20日均线上方，多头排列（当日价格>5日均线>10日均线>20日均线）
4、	大盘开盘低开，日内分时大跌时买入/大跌后企稳时买进
'''

import numpy as np
import pandas as pd

from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date

start_date = 20170101
end_date = 20191231
shift_start_date = get_pre_trade_date(start_date, offset=30)
date_list = get_date_range(shift_start_date, end_date)


def get_amplt(s: pd.Series, mkt_pct_chg_rel_open):
    res = pd.Series(index=s.index)
    res[:31] = s.expanding().max().apply(lambda x: x + 1 if x > 1 else 1)[:31] - s.expanding().min().apply(
        lambda x: x + 1 if x < 1 else 1)[:31]
    res[31:] = (mkt_pct_chg_rel_open.expanding().max() - mkt_pct_chg_rel_open.expanding().min())[31:]
    return res


def get_pct_chg_5min(s: pd.Series, mkt_pct_chg_rel_open):
    res = pd.Series(index=s.index)
    res[0] = mkt_pct_chg_rel_open[0]
    res[1:] = (s - s.shift(5))[1:]


# 1、大盘近一段时期日间位于下跌趋势/压力位/震荡（涨跌幅<0且下跌天数>上涨天数）
_rolling_day = 10  # 大盘下跌天数
mkt_close = get_daily_1factor('close', code_list=['SZZZ'], date_list=date_list, type='bench')
mkt_pct_chg = mkt_close.pct_change(1)
cum_pct_chg = mkt_pct_chg.rolling(_rolling_day).sum()
judge1 = cum_pct_chg < 0
rise_day_num = cum_pct_chg.rolling(_rolling_day).apply(lambda x: (x > 0).sum())
down_day_num = cum_pct_chg.rolling(_rolling_day).apply(lambda x: (x < 0).sum())
judge2 = rise_day_num > down_day_num

# 2、个股是近期活跃过的股票，（活跃过：定义出现过涨停，或近期成交量比较大）——暂不用管

# 3、个股近一段时间涨势较好，
stk_close = get_daily_1factor('close_badj', date_list=date_list)
ma5 = stk_close.rolling(5).mean()
ma10 = stk_close.rolling(10).mean()
ma20 = stk_close.rolling(20).mean()

judge3 = (stk_close > ma20) & (ma5 > ma10) & (ma10 > ma20)

# 日间信息集合
daily_judge = (judge3.T & judge1.iloc[:, 0]).T & (judge3.T & judge2.iloc[:, 0]).T
daily_judge = daily_judge.shift(1)

# 4、大盘日内分时跌幅较大，跌幅较大后企稳或反弹
start_datetime = start_date * 10000 + 930
end_datetime = end_date * 10000 + 1500
mkt_minute_open = get_minute_1factor('open', code_list=['SZZZ'], type='bench').loc[
                  (shift_start_date, 930):(end_date, 1500), :]
mkt_minute_open.index.name = 'date', 'time'
yes_mkt_close = mkt_close.shift(1)
mkt_close_copy = pd.DataFrame(np.array(yes_mkt_close.loc[mkt_minute_open.index.get_level_values('date')]), \
                              index=mkt_minute_open.index, columns=['SZZZ'])
daily_judge_copy = pd.DataFrame(np.array(daily_judge.loc[mkt_minute_open.index.get_level_values('date')]), \
                                index=mkt_minute_open.index, columns=daily_judge.columns)
mkt_minute_pct_chg = mkt_minute_open / mkt_close_copy - 1
mkt_minute_pct_chg = mkt_minute_pct_chg.rename({'SZZZ': 'pct_chg'}, axis=1)
mkt_minute_pct_chg['mkt_pct_chg_rel_open'] = mkt_minute_open.apply(lambda x: x / x.iloc[0] - 1)

# 方式一：日内信息：大跌
mkt_minute_pct_chg['down_pct_5min'] = mkt_minute_pct_chg['pct_chg'].groupby(['date']).apply(lambda x: x - x.shift(5))
mkt_minute_pct_chg['down_pct_4min'] = mkt_minute_pct_chg['pct_chg'].groupby(['date']).apply(lambda x: x - x.shift(4))
mkt_minute_pct_chg['down_pct_3min'] = mkt_minute_pct_chg['pct_chg'].groupby(['date']).apply(lambda x: x - x.shift(3))
mkt_minute_pct_chg['down_pct_2min'] = mkt_minute_pct_chg['pct_chg'].groupby(['date']).apply(lambda x: x - x.shift(2))
mkt_minute_pct_chg['down_pct_1min'] = mkt_minute_pct_chg['pct_chg'].groupby(['date']).apply(lambda x: x - x.shift(1))
mkt_minute_judge1 = (mkt_minute_pct_chg['down_pct_5min'] < -0.004) | \
                    (mkt_minute_pct_chg['down_pct_4min'] < -0.004) | \
                    (mkt_minute_pct_chg['down_pct_3min'] < -0.004) | \
                    (mkt_minute_pct_chg['down_pct_2min'] < -0.004) | \
                    (mkt_minute_pct_chg['down_pct_1min'] < -0.004)

# mkt_minute = get_minute_1stock('SZZZ', factor_list=['open', 'high', 'low', 'close'], type='bench').loc[(start_date,930):(end_date,1500), :]
# mkt_minute_rolling_high_5min = mkt_minute['high'].groupby('date').rolling(5).max()
# mkt_minute_rolling_low_5min = mkt_minute['low'].groupby('date').rolling(5).max()
# mkt_minute_amplt = (mkt_minute_rolling_high_5min - mkt_minute_rolling_low_5min) / mkt_minute_rolling_low_5min

# 方式二：日内信息：大盘五分钟跌幅在当前振幅的40%
# mkt_minute_pct_chg['down_pct_5min'] = mkt_minute_pct_chg[['pct_chg', 'mkt_pct_chg_rel_open']].groupby(['date']).apply(
#     lambda x: get_pct_chg_5min(x['pct_chg'], x['mkt_pct_chg_rel_open'])).values
mkt_minute_pct_chg['amplt'] = mkt_minute_pct_chg[['pct_chg', 'mkt_pct_chg_rel_open']].groupby(['date']).apply(
    lambda x: get_amplt(x['pct_chg'], x['mkt_pct_chg_rel_open'])).values
# mkt_minute_judge2 = (mkt_minute_pct_chg['down_pct_5min'].map(abs) > (mkt_minute_pct_chg['amplt'] * 0.4))
mkt_minute_judge3 = (mkt_minute_pct_chg['amplt'] > 0.01)

index_judge = mkt_minute_judge1 & mkt_minute_judge3

# 个股日内拉升
param_stk_rolling_window = 3
param_stk_qrr_rolling_window = 20
stk_minute_open = get_minute_1factor('open').loc[(shift_start_date, 930):(end_date, 1500), :]
pctchg_speed = stk_minute_open.pct_change(param_stk_rolling_window)
stk_amt = get_minute_1factor('amt').loc[(shift_start_date, 930):(end_date, 1500), :]
stk_amt.index.name = 'date', 'time'
stk_qrr_rolling10 = stk_amt.shift(10).rolling(param_stk_qrr_rolling_window).mean()
stk_qrr_rolling = stk_amt.rolling(param_stk_qrr_rolling_window).mean()
stk_qrr = stk_qrr_rolling / stk_qrr_rolling10

stk_judge = (pctchg_speed > 0.006) & (stk_qrr > 1.1)

signal = (stk_judge.T & index_judge).T & (daily_judge.T & index_judge).T

# 保存
signal.to_pickle()

# 测试
dd = mkt_minute_judge1 & mkt_minute_judge3
mkt_minute_judge1.sum() / len(mkt_minute_judge1)
mkt_minute_judge3.sum() / len(mkt_minute_judge3)

mkt_minute_judge1_daily = mkt_minute_judge1.groupby('date').sum()
mkt_minute_judge1_daily_ = mkt_minute_judge1_daily != 0
mkt_minute_judge3_daily = mkt_minute_judge3.groupby('date').sum()
mkt_minute_judge3_daily_ = mkt_minute_judge3_daily != 0
dd_daily = dd.groupby('date').sum()
dd_daily_ = dd_daily != 0

mkt_minute_judge1_daily_.sum() / len(mkt_minute_judge1_daily_)
mkt_minute_judge3_daily_.sum() / len(mkt_minute_judge3_daily_)
dd_daily_.sum() / len(dd_daily_)

# 特定日期
dd = dd[dd == True]
aa = mkt_minute_pct_chg.loc[(20160912, 930):(20160912, 1500)]

pass
# 日内分时大跌后

# 日内分时大跌企稳后