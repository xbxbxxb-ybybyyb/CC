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

def factor_tx_tick_WeightedBuyNum(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    NumTrades = dp.get_data_by_date_list(item='NumTrades', start_date=start_date, end_date=end_date, return_idx=True)

    Buy1OrderQty = dp.get_data_by_date_list(item='Buy1OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy2OrderQty = dp.get_data_by_date_list(item='Buy2OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy3OrderQty = dp.get_data_by_date_list(item='Buy3OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy4OrderQty = dp.get_data_by_date_list(item='Buy4OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy5OrderQty = dp.get_data_by_date_list(item='Buy5OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy6OrderQty = dp.get_data_by_date_list(item='Buy6OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy7OrderQty = dp.get_data_by_date_list(item='Buy7OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy8OrderQty = dp.get_data_by_date_list(item='Buy8OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy9OrderQty = dp.get_data_by_date_list(item='Buy9OrderQty', start_date=start_date, end_date=end_date, return_idx=True)
    Buy10OrderQty = dp.get_data_by_date_list(item='Buy10OrderQty', start_date=start_date, end_date=end_date, return_idx=True)

    Buy1NumOrders = dp.get_data_by_date_list(item='Buy1NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy2NumOrders = dp.get_data_by_date_list(item='Buy2NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy3NumOrders = dp.get_data_by_date_list(item='Buy3NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy4NumOrders = dp.get_data_by_date_list(item='Buy4NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy5NumOrders = dp.get_data_by_date_list(item='Buy5NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy6NumOrders = dp.get_data_by_date_list(item='Buy6NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy7NumOrders = dp.get_data_by_date_list(item='Buy7NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy8NumOrders = dp.get_data_by_date_list(item='Buy8NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy9NumOrders = dp.get_data_by_date_list(item='Buy9NumOrders', start_date=start_date, end_date=end_date,return_idx=True)
    Buy10NumOrders = dp.get_data_by_date_list(item='Buy10NumOrders', start_date=start_date, end_date=end_date,return_idx=True)

    stock_pool_stack = LimitPool[LimitPool].stack()

    Weight_BuyNum=0.4*(Buy1OrderQty/Buy1NumOrders).replace([np.nan,np.inf],0)+\
                  0.2*(Buy2OrderQty/Buy2NumOrders).replace([np.nan,np.inf],0)+ \
                  0.1*(Buy3OrderQty / Buy3NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy4OrderQty / Buy4NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy5OrderQty / Buy5NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy6OrderQty / Buy6NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy7OrderQty / Buy7NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy8OrderQty / Buy8NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy9OrderQty / Buy9NumOrders).replace([np.nan,np.inf],0)+\
                  0.05*(Buy10OrderQty / Buy10NumOrders).replace([np.nan,np.inf],0)

    factor = Weight_BuyNum / NumTrades

    factor = factor[LimitPool].stack()
    factor.replace(np.inf, np.nan, inplace=True)
    factor = factor.loc[stock_pool_stack.index]

    return factor

