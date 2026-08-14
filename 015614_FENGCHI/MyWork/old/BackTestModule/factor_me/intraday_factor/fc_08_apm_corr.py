# coding: utf-8
# Author：fengchi863
# Date ：2020/3/10 15:20
from config import *
import pandas as pd, numpy as np
import time
import os
from multiprocessing import Pool
from dataApi.stockList import clean_stock_list
from QuickFactorEvaluationBackTest import FactorBackTest

root_path = '/data/group/800319/junkData/temp_factor_by_fc/'

# 日期
start_date = 20170101
end_date = 20191231

# 日间股票池筛选参数
least_live_days = 120
least_recover_days = 5
daily_report_period = 240
daily_amt_period = 20
daily_ret_period = 60
daily_ret_low_band = 0.1
daily_ret_high_band = 0.9
pe_low_band = 0
pe_high_band = 300
price_low_band = 3
amt_low_band = 1e4
week_report_low_band = 0
apm_low_band = 0.1

# 日内参数
len_intraday_rolling_window = 30
open_vol_corr_high = 0.9
open_vol_corr_low = 0.01

# 回测参数
max_holding_day = 3
order_holding = 5

# 因子名称
factor_name = 'fc_08_apm_corr_%.2f_%.2f' % (open_vol_corr_high, open_vol_corr_low)

date_list = get_date_range(get_pre_trade_date(start_date, 1), end_date)

stock_pool_all = clean_stock_list(
    no_ST=True,
    stock_list='COMMON',
    least_live_days=120,
    no_pause=True,
    least_recover_days=5,
    no_limit_up=False,
    no_limit_down=False,
    address='/data/group/800319/junkData/daily',
).reindex(index=date_list)

stk_code_list = stock_pool_all.columns.to_list()

e1 = time.time()

# 收益分位数
daily_adj_close = get_daily_1factor(
    factor='close_badj',
    date_list=get_date_range(get_pre_trade_date(start_date, 1+daily_ret_period), end_date),
)
daily_ret = daily_adj_close.pct_change(daily_ret_period).iloc[daily_ret_period:].fillna(0)
daily_ret_rank = daily_ret.rank(pct=True, axis=1).reindex(columns=stk_code_list)

# 市盈率范围
daily_pe = get_daily_1factor(
    factor='pe_ttm',
    date_list=date_list,
    code_list=stk_code_list,
)

# 过去20个交易日成交额中位数
daily_amt = get_daily_1factor(
    factor='amt',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_amt_period), end_date),
    code_list=stk_code_list,
)
daily_amt = daily_amt.rolling(daily_amt_period).median().iloc[daily_amt_period-1:]

#股价不能低于
daily_price = get_daily_1factor(
    factor='close',
    date_list=date_list,
    code_list=stk_code_list,
)

# 研报数量
daily_report_num = get_daily_1factor(
    factor='report_number7',
    date_list=get_date_range(get_pre_trade_date(start_date, daily_report_period), end_date),
    code_list=stock_pool_all.columns.to_list(),
)
daily_report_num = daily_report_num.rolling(daily_report_period).mean().iloc[daily_report_period-1:]

# 基于日内的动量模式，日间选股
def get_daily_momentum(date):
    print(date)
    start_time = date * 10000 + 930
    end_time = date * 10000 + 1500
    minute = get_minute_1factor('close', start_datetime=start_time, end_datetime=end_time, code_list=stk_code_list)
    minute_pctchg = minute.pct_change(periods=60)
    r1 = minute_pctchg.iloc[60]
    r2 = minute_pctchg.iloc[120]
    r2.name = (date, 1130)
    r3 = minute_pctchg.iloc[180]
    r4 = minute_pctchg.iloc[240]
    close = get_daily_1factor('open_badj', date_list=[date], code_list=stk_code_list)
    pre_close = get_daily_1factor('pre_close_badj', date_list=[date], code_list=stk_code_list)
    r0 = (close / pre_close - 1).iloc[0]
    r0.name = (date, 930)
    res = pd.concat([r0, r1, r2, r3, r4], axis=1).T
    return res

pool = Pool(32)
factor_df_list = pool.map_async(get_daily_momentum, date_list)
pool.close()
pool.join()
momentum_factor = pd.concat(factor_df_list.get(), axis=0)
momentum_factor.sort_index(inplace=True)

R0 = momentum_factor.loc[(slice(None), 930),:].values
R1 = momentum_factor.loc[(slice(None), 1030),:].values
R2 = momentum_factor.loc[(slice(None), 1130),:].values
R3 = momentum_factor.loc[(slice(None), 1400),:].values
R4 = momentum_factor.loc[(slice(None), 1500),:].values

# 参考方正证券研报《基于日内模式的动量因子革新》
momentum = -0.47 * R0 - 0.59 * R1 + 0.76 * R2 + 1.5 * R3 + R4
apm = pd.DataFrame(momentum, index=date_list, columns=stk_code_list)
apm = apm.rank(axis=1, pct=True)

daily_filter = (
        True
        & (daily_ret_rank > daily_ret_low_band)
        & (daily_ret_rank < daily_ret_high_band)
        & (daily_pe > pe_low_band)
        & (daily_pe < pe_high_band)
        & (daily_price > price_low_band)
        & (daily_amt > amt_low_band)
        & (daily_report_num > week_report_low_band)
        & (stock_pool_all > 0)
        & (apm < apm_low_band)
)

## 日内因子计算
def get_daily_factor(date):
    print(date)
    start_time = date * 10000 + 930
    end_time = date * 10000 + 1500
    temp_bool_clean = daily_filter.loc[date]

    # 数据准备
    temp_minute_vol = get_minute_1factor('vol', start_datetime=start_time, \
                                         end_datetime=end_time)
    temp_minute_open = get_minute_1factor('open', start_datetime=start_time, \
                                          end_datetime=end_time)

    # 计算因子
    open_vol_corr = -1 * temp_minute_open.rolling(len_intraday_rolling_window).corr(temp_minute_vol)

    high_band = open_vol_corr.quantile(open_vol_corr_high, axis=1)
    low_band = open_vol_corr.quantile(open_vol_corr_low, axis=1)

    # 因子值越小，越呈现出量增价增的状态，这时买入，反之
    factor_df = open_vol_corr.sub(low_band, axis=0)
    factor_df.where(factor_df < 0, np.nan, inplace=True)
    factor_df.where(factor_df.isna(), 1, inplace=True)

    factor_df2 = open_vol_corr.sub(high_band, axis=0)
    factor_df2.where(factor_df2 > 0, 0, inplace=True)
    factor_df2.where(factor_df2 <= 0, -1, inplace=True)

    factor_df.fillna(factor_df2, inplace=True)
    factor_df.fillna(0, inplace=True)

    factor_df.iloc[:30, :] = 0
    factor_df.iloc[-3:, :] = 0

    # 清洗
    stk_clean = temp_bool_clean[~temp_bool_clean].index.intersection(factor_df.columns)
    factor_df[stk_clean] = 0
    return factor_df

pool = Pool(32)
factor_df_list = pool.map_async(get_daily_factor, date_list)
pool.close()
pool.join()
factor = pd.concat(factor_df_list.get(), axis=0)
factor.sort_index(inplace=True)

## 计算买入信号和卖出信号的比例
pct_buy_signal = factor[factor > 0].sum().sum() / (factor.shape[0] * factor.shape[1])
pct_sell_signal = factor[factor < 0].sum().sum() / (factor.shape[0] * factor.shape[1])

## 进行回测
factor = factor.astype(int)
factor.index = [x * 10000 + y for x, y in factor.index]

factor.to_pickle(root_path + 'factor/' + factor_name + '.pkl')

print('因子计算时间：', time.time() - e1)

e1 = time.time()

# 定义因子回测对象
factor_test = FactorBackTest(factor, max_holding_day=max_holding_day, \
                             order_holding=order_holding)
print('因子回测初始化时间：', time.time() - e1)

# 并行回测
e1 = time.time()
factor_test.evaluation(32)
factor_test.result_output(factor_name, root_path + 'result/')
print('因子回测时间：', time.time() - e1)

res = factor_test.evaluation_result.T
resDay = factor_test.evaluation_result_daily
netValue = factor_test.net_value
trading_records = factor_test.trading_record
