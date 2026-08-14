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

def factor_tx_TickRet3_diff(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()

    TickRet = LastPx.astype(float).replace(0, np.nan).T.pct_change()
    TickRet2 = (TickRet ** 2).expanding().sum().T
    TickRet3 = (TickRet ** 3).expanding().sum().T
    Num = (TickRet).expanding().sum().T
    factor = np.sqrt(Num) * TickRet3 / (TickRet2) ** (3 / 2)
    factor = factor.T.diff(1).T
    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]
    return factor

