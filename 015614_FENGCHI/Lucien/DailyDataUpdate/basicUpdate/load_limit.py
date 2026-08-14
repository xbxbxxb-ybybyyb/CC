import sys
sys.path.append('/data/user/015614/Lucien')

from dataApi.stockList import clean_stock_list, trans_windcode2int
from dataApi.getData import get_minute_pickle
from dataApi.tradeDate import get_date_range
import datetime as dt
import pandas as pd
import numpy as np

from xquant.factordata import FactorData
fd = FactorData()

half_years = get_date_range(20091231, 20251231, 'Q')    # TODO: 这里日期每年得改一下
left = ['>=%s' % x for x in half_years[:-1]]
right = ['<%s' % x for x in half_years[1:]]

limit_price = pd.DataFrame()
for j in range(len(left)):
    df = fd.get_factor_value(
        "WIND_AShareEODPrices",
        factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_LIMIT', 'S_DQ_STOPPING'],
        TRADE_DT=[left[j], right[j]],
    )
    limit_price = limit_price.append(df)

limit_max = limit_price.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_LIMIT').sort_index().iloc[1:]
limit_max.index = limit_max.index.map(int)
limit_max.columns = limit_max.columns.map(trans_windcode2int)
limit_max = limit_max.sort_index(axis=1)

limit_min = limit_price.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_STOPPING').sort_index().iloc[1:]
limit_min.index = limit_min.index.map(int)
limit_min.columns = limit_min.columns.map(trans_windcode2int)
limit_min = limit_min.sort_index(axis=1)

limit_min.to_hdf('/data/user/015614/easy_transfer/basic_data/daily/limit_min.h5', 'limit_min', format='t')
limit_max.to_hdf('/data/user/015614/easy_transfer/basic_data/daily/limit_max.h5', 'limit_max', format='t')