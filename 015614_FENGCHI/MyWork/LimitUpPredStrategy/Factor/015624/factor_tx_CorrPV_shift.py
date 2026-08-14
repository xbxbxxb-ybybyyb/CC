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

def factor_tx_CorrPV_shift(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date, return_idx=True)
    TotalVolumeTrade = dp.get_data_by_date_list(item='TotalVolumeTrade', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()

    TickVolume = TotalVolumeTrade.astype(int).T.diff(1)
    Px = LastPx.T.shift(1)

    Volume_sum = TickVolume.expanding().mean()
    Price_sum = Px.expanding().mean()

    Volume_sum2 = (TickVolume ** 2).expanding().mean()
    Price_sum2 = (Px ** 2).expanding().mean()

    VolumePrice_sum = (Px * TickVolume).expanding().mean()

    factor = ((VolumePrice_sum - Volume_sum * Price_sum) / np.sqrt(
        (Volume_sum2 - Volume_sum ** 2) * (Price_sum2 - Price_sum ** 2))).T

    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]

    return factor


