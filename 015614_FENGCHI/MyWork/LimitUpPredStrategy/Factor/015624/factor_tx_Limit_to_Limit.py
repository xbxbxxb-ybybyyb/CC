import numpy as np
import pandas as pd
from tqdm import tqdm
import bottleneck as bk
import time
from backtest.factor_backtest.TickDataPrepare import TickDataPrepare
sys.path.append('/data/group/800442/800319')
from dataApi import getData, tradeDate, stockList
from dataApi.tradeDate import get_date_range
from dataApi.stockList import trans_windcode2int,trans_datetime2int,trans_int2windcode
from LimitUpPredStrategy.Factor.tick_data_load import TickData

def factor_tx_Limit_to_Limit(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()

    LowPx_inday = LastPx.replace(0, np.nan).T.rolling(40).min()
    factor = LastPx.replace(0, np.nan) / LowPx_inday.T

    pct_chg = getData.get_daily_1factor('pct_chg', date_list=LimitPool.index.levels[0].to_list(),code_list=LimitPool.index.levels[1].to_list()).shift(1)
    pct_chg = pct_chg.stack().loc[factor.index]

    factor = (factor.T * pct_chg).T

    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]

    return factor

