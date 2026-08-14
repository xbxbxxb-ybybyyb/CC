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

def factor_tx_Weight_BuyPressure(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    Buy1OrderQty = dp.get_data_by_date_list(item='Buy1OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy2OrderQty = dp.get_data_by_date_list(item='Buy2OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy3OrderQty = dp.get_data_by_date_list(item='Buy3OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy4OrderQty = dp.get_data_by_date_list(item='Buy4OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy5OrderQty = dp.get_data_by_date_list(item='Buy5OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy6OrderQty = dp.get_data_by_date_list(item='Buy6OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy7OrderQty = dp.get_data_by_date_list(item='Buy7OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy8OrderQty = dp.get_data_by_date_list(item='Buy8OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy9OrderQty = dp.get_data_by_date_list(item='Buy9OrderQty', start_date=start_date, end_date=end_date,
                                            return_idx=True)
    Buy10OrderQty = dp.get_data_by_date_list(item='Buy10OrderQty', start_date=start_date, end_date=end_date,
                                             return_idx=True)

    stock_pool_stack = LimitPool[LimitPool].stack()

    buy_volume = 0.4 * Buy1OrderQty + 0.2 * Buy2OrderQty + 0.1 * Buy3OrderQty + 0.05 * Buy4OrderQty + 0.05 * Buy5OrderQty + \
                 0.05 * Buy6OrderQty + 0.05 * Buy7OrderQty + 0.05 * Buy8OrderQty + 0.05 * Buy9OrderQty + 0.05 * Buy10OrderQty

    buy_volume = buy_volume[LimitPool].stack()

    free_shares = getData.get_daily_1factor('free_float_shares', date_list=LimitPool.index.levels[0].to_list(),
                                            code_list=LimitPool.index.levels[1].to_list()).shift(1)
    free_shares = free_shares.stack().loc[buy_volume.index]

    factor = buy_volume / free_shares
    factor = factor.loc[stock_pool_stack.index]


    return factor
