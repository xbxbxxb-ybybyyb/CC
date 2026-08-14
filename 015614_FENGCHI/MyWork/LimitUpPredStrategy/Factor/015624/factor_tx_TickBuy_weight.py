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

def factor_tx_TickBuy_weight(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date, return_idx=True)
    Buy1Price = dp.get_data_by_date_list(item='Buy1Price', start_date=start_date, end_date=end_date, return_idx=True)
    TotalVolumeTrade = dp.get_data_by_date_list(item='TotalVolumeTrade', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()

    Buy1Price_before = Buy1Price.T.shift(1).T
    Tick_VolumeTrade = TotalVolumeTrade.T.diff(1).T
    BuyTick = Tick_VolumeTrade[LastPx > Buy1Price_before].T.expanding().sum().T
    SellTick = Tick_VolumeTrade[LastPx < Buy1Price_before].T.expanding().sum().T
    OtherTick = Tick_VolumeTrade[LastPx < Buy1Price_before].T.expanding().sum().T

    factor = (BuyTick + OtherTick / 2) / (BuyTick + SellTick + OtherTick)
    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]



    return factor
