# coding: utf-8
# Author：fengchi863
# Date ：2020/4/23 18:02

from dataApi.getData import *
from dataApi.usefulTools import *
from dataApi.stockList import *

start_date = 20170103
end_date = 20191231
date_list = get_date_range(start_date, end_date)

stock_pool = clean_stock_list('COMMON')
stock_list = clean_stock_list(no_limit_down=True, no_limit_up=True).shift(1).reindex(date_list)
stock_list = (stock_list > 0.5) & (
            stock_pool.shift(1).reindex_like(stock_list) > 0.5) if stock_pool is not None else stock_list
stock_list = stock_list.reindex(columns=sorted(stock_list.sum()[stock_list.sum() > 0.5].index.tolist()))

vwap = get_minute_1factor('amt', start_date, end_date)[stock_list.columns.tolist()] / \
       get_minute_1factor('vol', start_date, end_date)[stock_list.columns.tolist()]
index, columns = vwap.index, stock_list.columns.tolist()
vwap = frame2arr(vwap)
factor106 = -1*vwap/delay(vwap,20)-1
factor106 = arr2frame(factor106, index, columns)
# factor106.to_hdf('/data/group/800319/storeFactor/'+'factor106.h5', 'factor106', format='t')
factor106.to_hdf('/data/group/800319/storeFactor/original_intrafactor/'+'factor106.h5', 'factor106', format='t')