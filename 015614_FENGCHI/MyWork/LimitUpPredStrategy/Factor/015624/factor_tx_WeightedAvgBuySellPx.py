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

def factor_tx_WeightedAvgBuySellPx(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    WeightedAvgBidPx = dp.get_data_by_date_list(item='WeightedAvgBidPx', start_date=start_date, end_date=end_date, return_idx=True)
    WeightedAvgOfferPx = dp.get_data_by_date_list(item='WeightedAvgOfferPx', start_date=start_date, end_date=end_date,
                                                return_idx=True)

    stock_pool_stack = LimitPool[LimitPool].stack()

    factor = WeightedAvgBidPx / WeightedAvgOfferPx - 1
    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]
    factor.replace(np.inf, 0, inplace=True)

    return factor
