import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.stockList import trans_windcode2int, clean_stock_list
from dataApi.getData import get_daily_1factor
from dataApi.indName import sw_level1, sw_level2
from dataApi.tradeDate import trans_datetime2int, get_recent_trade_date, get_pre_trade_date, get_date_range
import pandas as pd
import numpy as np
import os

risk_factors = [
    'Beta',
    'BookToPrice',
    'DividendYield',
    'EarningsQuality',
    'EarningsVariability',
    'EarningsYield',
    'Growth',
    'InvestmentQuality',
    'Leverage',
    'Liquidity',
    'LongTermReversal',
    'MidCapitalization',
    'Momentum',
    'Profitability',
    'ResidualVolatility',
    'Size',
]

risk_address = '/data/group/800002/basic_data/full/financial_data/' \
          'RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5'

date_list = get_date_range(20110104, None)

stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                              no_pause=True, least_recover_days=1,
                              no_pause_limit=0.5, no_pause_stats_days=120,
                              no_limit_up=False, no_limit_down=False,
                              other_limit=None, trade_mode=False,
                              start_date=date_list[0], end_date=date_list[-1])

code_list = stock_pool.columns.to_list()
pct_chg = get_daily_1factor('pct_chg', date_list, code_list)
close = get_daily_1factor('close', date_list, code_list)

# 1 风格监控
def load_risk_factor(item, date_list, code_list, address):
    factor = pd.read_hdf(address, item)[item].unstack()
    factor.index = factor.index.map(trans_datetime2int)
    factor.columns = factor.columns.map(trans_windcode2int)
    factor = factor.reindex(index=date_list, columns=code_list)
    return factor

Beta = load_risk_factor('Beta', date_list, code_list, risk_address)
BookToPrice = load_risk_factor('BookToPrice', date_list, code_list, risk_address)
DividendYield = load_risk_factor('DividendYield', date_list, code_list, risk_address)
EarningsQuality = load_risk_factor('EarningsQuality', date_list, code_list, risk_address)
EarningsVariability = load_risk_factor('EarningsVariability', date_list, code_list, risk_address)
EarningsYield = load_risk_factor('EarningsYield', date_list, code_list, risk_address)
Growth = load_risk_factor('Growth', date_list, code_list, risk_address)
InvestmentQuality = load_risk_factor('InvestmentQuality', date_list, code_list, risk_address)
Leverage = load_risk_factor('Leverage', date_list, code_list, risk_address)
Liquidity = load_risk_factor('Liquidity', date_list, code_list, risk_address)
LongTermReversal = load_risk_factor('LongTermReversal', date_list, code_list, risk_address)
MidCapitalization = load_risk_factor('MidCapitalization', date_list, code_list, risk_address)
Momentum = load_risk_factor('Momentum', date_list, code_list, risk_address)
Profitability = load_risk_factor('Profitability', date_list, code_list, risk_address)
ResidualVolatility = load_risk_factor('ResidualVolatility', date_list, code_list, risk_address)
Size = load_risk_factor('Size', date_list, code_list, risk_address)

def calc_risk_return(factor, pct_chg, stock_pool):

    pool = stock_pool & pct_chg.notnull() & factor.notnull()
    factor = factor[pool].rank(axis=1, pct=True)
    pct_chg = pct_chg[factor > 0.5].mean(axis=1) - pct_chg[factor <= 0.5].mean(axis=1)
    pct_chg.iloc[0] = 0
    pct_chg = (pct_chg / 100 + 1).cumprod()
    return pct_chg

risk_val = pd.concat([calc_risk_return(x, pct_chg, stock_pool) for x in [
    Beta, BookToPrice, DividendYield, EarningsQuality, EarningsVariability,
    EarningsYield, Growth, InvestmentQuality, Leverage, Liquidity,
    LongTermReversal, MidCapitalization, Momentum, Profitability,
    ResidualVolatility, Size]], keys=risk_factors, axis=1)

risk_ret_rank = pd.concat([risk_val.pct_change(x).rank(axis=1, pct=True) for x in [1, 3, 5, 10]],
                     keys=['1d', '3d', '5d', '10d'], axis=1).loc[20140401:]

# risk_ret = pd.concat([risk_val.pct_change(x) for x in [1, 3, 5, 10, 20]],
#                      keys=['1d', '3d', '5d', '10d', '20d'], axis=1).loc[20140401:]

# # 2 行业监控
# SW1 = get_daily_1factor('SW1', date_list, code_list)
# retSW1 = pd.DataFrame({sw_level1[x]: pct_chg[stock_pool & (SW1 == x)].mean(axis=1) for x in sw_level1})
# retSW1 -= pct_chg.mean(axis=1).values[:, None]
# retSW1.iloc[0] = 0
# retSW1 = (1 + retSW1 / 100).cumprod()
#
#
# retSW1_rank = pd.concat([retSW1.pct_change(x).rank(axis=1, pct=True) for x in [1, 3, 5, 10, 20, 60]],
#                         keys=['1d', '3d', '5d', '10d', '20d', '60d'], axis=1).loc[20140401:]
#
# retSW1 = pd.concat([retSW1.pct_change(x) for x in [1, 3, 5, 10, 20, 60]],
#                    keys=['1d', '3d', '5d', '10d', '20d', '60d'], axis=1).loc[20140401:]
#
# # 3 指数监控
# bench = pd.read_pickle(f'/data/group/800080/Apollo/AlphaDataBase/index/close.pkl')
# bench = bench[['000001.SH', '000016.SH', '000300.SH', '000852.SH', '000905.SH',
#                '000906.SH', '000985.CSI', '399001.SZ', '399005.SZ', '399006.SZ']]
# bench.index = bench.index.map(int)
#
# bench_ret_rank = pd.concat([bench.pct_change(x).rank(axis=1, pct=True) for x in [1, 3, 5, 10, 20, 60]],
#                      keys=['1d', '3d', '5d', '10d', '20d', '60d'], axis=1).loc[20140401:]
#
# bench_ret = pd.concat([bench.pct_change(x) for x in [1, 3, 5, 10, 20, 60]],
#                      keys=['1d', '3d', '5d', '10d', '20d', '60d'], axis=1).loc[20140401:]

def calc_dist(arr, dtype='float32'):
    index = arr.index
    arr = arr.values.astype(dtype)
    arr = arr[:, None] - arr[None, :]
    arr = np.sqrt(np.mean(arr.astype(np.float32) ** 2, axis=2))
    return pd.DataFrame(arr, index=index, columns=index)

risk_rank_dist = calc_dist(risk_ret_rank)
# ind_rank_dist = calc_dist(retSW1_rank)
# bench_rank_dist = calc_dist(bench_ret_rank)
# risk_dist = calc_dist(risk_ret)
# ind_dist = calc_dist(retSW1)
# bench_dist = calc_dist(bench_ret)

risk_rank_dist.to_pickle('/data/group/800442/800319/risk_rank_ex20_dist.pkl')
# ind_rank_dist.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/ind_rank_dist.pkl')
# bench_rank_dist.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/bench_rank_dist.pkl')
# risk_dist.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/risk_dist.pkl')
# ind_dist.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/ind_dist.pkl')
# bench_dist.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/bench_dist.pkl')
#
# szzz_ret = bench['000001.SH'].pct_change()
# szzz_ret = pd.concat([szzz_ret.shift(x) for x in range(20)], axis=1, keys=range(20)).loc[20140401:]
# szzz_ret = calc_dist(szzz_ret)
# szzz_ret.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/szzz_ret.pkl')
#
# size_ret = risk_val['Size'].pct_change()
# size_ret = pd.concat([size_ret.shift(x) for x in range(20)], axis=1, keys=range(20)).loc[20140401:]
# size_ret = calc_dist(size_ret)
# size_ret.to_pickle('/arch1/user/015836/HFmodel/BackPool/ConditionSample/size_ret.pkl')