import psutil
import pandas as pd
import numpy as np
from config import *
from QuickFactorEvaluationBackTest import FactorBackTest
import time
import sys
sys.path.append('/data/group/800319')
from dataApi.getData import get_minute_1factor,get_daily_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date

e1 = time.time()

def _rolling_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

##1参数部分
#日期
start_date = 20170103
end_date = 20191231
#因子参数
roll_window = 30
#信号参数
sign_percent_low = 0.1
sign_percent_high = 0.8

#日间股票池参数
daily_ret_period = 60
least_live_days = 120
least_recover_days = 5
daily_ret_low_band = 0.1
daily_ret_high_band = 0.8
pe_low_band = 0
pe_high_band = 300
close_low_limit = 3

##2日内因子部分
#提取数据
close = get_minute_1factor('close', start_date, end_date)
close_bench = get_minute_1factor('close', start_date, end_date, code_list=['ZZ500'], type='bench')

#准备矩阵运算
index, columns = close.index.map(lambda x: x[0] * 10000 + x[1]), close.columns
close = close.values.reshape(close.shape[0] // 242, 242, close.shape[1]).transpose(1, 0, 2)
close_bench = close_bench.values.reshape(close_bench.shape[0] // 242, 242).transpose(1, 0)

#计算日内超额收益
profit = close / close[0]
profit_bench = close_bench / close_bench[0]
del close, close_bench

alpha = profit.transpose(2, 0, 1) - profit_bench
alpha[np.isnan(alpha)] = 0
alpha = alpha.transpose(1, 2, 0)
del profit, profit_bench

#计算因子
rank_sect = alpha.argsort().argsort() # (241,731,3814)
rank_sect_roll = _rolling_windows(rank_sect[1:], roll_window) # (212,30,731,3814)
rank_sect_min = rank_sect_roll.min(axis=1) # (212,731,3814)
rank_sect_max = rank_sect_roll.max(axis=1)
score = (rank_sect[roll_window:] - rank_sect_min) / (rank_sect_max - rank_sect_min)
del alpha, rank_sect, rank_sect_roll, rank_sect_max , rank_sect_min

# alpha_expand_max = np.maximum.accumulate(alpha[1:], axis=0)
# alpha_expand_min = np.minimum.accumulate(alpha[1:], axis=0)
#
# alpha_move_average = np.apply_along_axis(np.convolve, 0, alpha[1:], np.ones(roll_window) / roll_window, 'valid')
#
# alpha_expand_max_id = np.arange(alpha_expand_max.shape[0]).repeat(alpha.shape[1] * alpha.shape[2]
#                                                                   ).reshape(alpha_expand_max.shape)
# alpha_expand_max_id[alpha[1:] < alpha_expand_max] = 0
# alpha_expand_max_id = np.maximum.accumulate(alpha[1:], axis=0)
#
# alpha_expand_min_id = np.arange(alpha_expand_min.shape[0]).repeat(alpha.shape[1] * alpha.shape[2]
#                                                                   ).reshape(alpha_expand_min.shape)
# alpha_expand_min_id[alpha[1:] > alpha_expand_min] = 0
# alpha_expand_min_id = np.maximum.accumulate(alpha[1:], axis=0)
#
# rank_sect_roll_max_id = rank_sect_roll.argmax(axis=1)
# rank_sect_roll_min_id = rank_sect_roll.argmin(axis=1)

##3日内信号部分
#计算阈值
low_band = np.quantile(score, sign_percent_low, axis=-1)
high_band = np.quantile(score, sign_percent_high, axis=-1)

#计算信号
score = score.transpose(2, 0, 1) # (3814,212,731)
sign = np.zeros((score.shape[0], 242, score.shape[2]))
sign[:, roll_window:, :][score < low_band] = 1
sign[:, roll_window:, :][score > high_band] = -1
del low_band, high_band, score

##4日间股票池部分
#清洗股票池
# daily_cleaned_stock_list = clean_stock_list(least_live_days=least_live_days, least_recover_days=least_recover_days).\
#     reindex(index=get_date_range(get_pre_trade_date(start_date), get_pre_trade_date(end_date)), columns=columns)

daily_cleaned_stock_list = clean_stock_list(stock_list= 'COMMON',least_live_days=least_live_days, least_recover_days=least_recover_days).\
    reindex(index=get_date_range(get_pre_trade_date(start_date), get_pre_trade_date(end_date)), columns=columns)
daily_cleaned_stock_list.fillna(False,inplace = True)

daily_close = get_daily_1factor(
    factor='close',
    date_list=get_date_range(get_pre_trade_date(start_date, 2), get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_close = daily_close.shift(1).iloc[1:]

#收益分位数
daily_adj_close = get_daily_1factor(
    factor='close_badj',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_ret_period + 1), get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_ret = daily_adj_close.pct_change(60).iloc[daily_ret_period-1:].fillna(0)
daily_ret_rank = daily_ret.rank(pct=True, axis=1)
daily_ret_rank = daily_ret_rank.shift(1).iloc[1:]

#市盈率范围
daily_pe = get_daily_1factor(
    factor='pe_ttm',
    date_list= get_date_range(get_pre_trade_date(start_date,2), get_pre_trade_date(end_date)),
    code_list=columns.to_list(),
)
daily_pe = daily_pe.shift(1).iloc[1:]


#计算日间股票池
daily_filter = (
        True
        & (daily_ret_rank > daily_ret_low_band)
        & (daily_ret_rank < daily_ret_high_band)
        & (daily_pe > pe_low_band)
        & (daily_pe < pe_high_band)
        & daily_cleaned_stock_list
        & (daily_close > close_low_limit)
)
del daily_adj_close, daily_ret, daily_ret_rank, daily_pe, daily_cleaned_stock_list

##5综合信号部分
sign = sign.transpose(1, 2, 0)
#只对买入信号进行日间筛选
sign = (sign == 1)*daily_filter.values - (sign == -1).astype(int)
sign = pd.DataFrame(sign.transpose(1, 0, 2).reshape(sign.shape[0] * sign.shape[1], sign.shape[2]),
                    index=index, columns=columns)

# 查验无信号股票
check = (sign > 0).any(0)
# check.sum()
codes_in = check[check].index
sign = sign[codes_in]

factor_name = 'gp_02_alpha_section_ts_rank'
#定义因子回测对象

factor_test = FactorBackTest(sign)
# del sign
#并行回测
factor_test.evaluation(6)
factor_test.result_output(factor_name, '/data/user/006693/')
factor_test.result_output(factor_name, '/data/group/800319/factorScripts/')
res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record
print('total time:',time.time()-e1)