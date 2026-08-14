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

def factor_tx_WeightBuyOrder(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    LastPx = dp.get_data_by_date_list(item='LastPx', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()
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

    Buy1Price = dp.get_data_by_date_list(item='Buy1Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy2Price = dp.get_data_by_date_list(item='Buy2Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy3Price = dp.get_data_by_date_list(item='Buy3Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy4Price = dp.get_data_by_date_list(item='Buy4Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy5Price = dp.get_data_by_date_list(item='Buy5Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy6Price = dp.get_data_by_date_list(item='Buy6Price', start_date=start_date, end_date=end_date, return_idx=True)
    Buy7Price = dp.get_data_by_date_list(item='Buy7Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy8Price = dp.get_data_by_date_list(item='Buy8Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy9Price = dp.get_data_by_date_list(item='Buy9Price', start_date=start_date, end_date=end_date,return_idx=True)
    Buy10Price = dp.get_data_by_date_list(item='Buy10Price', start_date=start_date, end_date=end_date,return_idx=True)

    buy_volume = Buy1OrderQty + Buy2OrderQty + Buy3OrderQty + Buy4OrderQty + Buy5OrderQty + Buy6OrderQty + Buy7OrderQty + Buy8OrderQty + Buy9OrderQty + Buy10OrderQty

    WeightBuy = Buy1OrderQty * Buy1Price + Buy2OrderQty * Buy2Price + Buy3OrderQty * Buy3Price + Buy4OrderQty * Buy4Price + Buy5OrderQty * Buy5Price + \
                Buy6OrderQty * Buy6Price + Buy7OrderQty * Buy7Price + Buy8OrderQty * Buy8Price + Buy9OrderQty * Buy9Price + Buy10OrderQty * Buy10Price

    factor = (WeightBuy / buy_volume) / LastPx

    factor = factor[LimitPool].stack()
    factor = factor.loc[stock_pool_stack.index]

    return factor

