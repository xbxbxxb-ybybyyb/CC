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

def factor_tx_price_percent(start_date,end_date):
    dp = TickDataPrepare()  # 实例化类
    LimitPool = dp.get_data_by_date_list(item='LimitPool', start_date=start_date, end_date=end_date, return_idx=True)
    stock_pool_stack = LimitPool[LimitPool].stack()

    close = getData.get_daily_1factor('close_badj', date_list=get_date_range(20120101, end_date),
                                      code_list=LimitPool.index.levels[1].to_list()).shift(1)
    factor = bk.move_rank(close, 300, axis=0)
    factor = pd.DataFrame(factor, index=close.index, columns=close.columns)

    factor = factor.stack().loc[LimitPool.index]
    factor = factor.loc[stock_pool_stack.index]

    return factor
