# coding: utf-8
# Author：fengchi863
# Date ：2020/3/20 10:36

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

# 因子名称
factor_name = 'fc_08_apm_corr.2f'

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