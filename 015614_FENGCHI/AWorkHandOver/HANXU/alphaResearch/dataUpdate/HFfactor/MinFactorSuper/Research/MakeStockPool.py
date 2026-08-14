import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from HFfactor.MinFactorSuper.Utility.LoadBigData import get_all_stock
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import store_augmented_matrix
from dataApi.tradeDate import get_date_range, get_trade_date_interval
from dataApi.stockList import clean_stock_list
import pandas as pd
import numpy as np
import time


def make_stock_pool(end_date=None, start_date=20140101, address='/arch1/group/800442/800319/MinFactorSuper/'):
    date_list = get_date_range(start_date, end_date, dividing_point=19)
    start_date = date_list[0]
    end_date = date_list[-1]
    date_offset = get_trade_date_interval(start_date, 20140101)
    code_list = get_all_stock(end_date)
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, trade_mode=True,
                                  start_date=date_list[0], end_date=date_list[-1])
    stock_pool = (stock_pool.reindex(columns=code_list) > 0).values[:, None, :]
    stock_pool = np.ascontiguousarray(stock_pool)
    store_augmented_matrix(stock_pool, f'{address}/Label/stock_pool.npy', offset_days=date_offset)
    store_augmented_matrix(stock_pool, f'{address}/ReduceLabel/stock_pool.npy', offset_days=date_offset)

    new_stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=5,
                                      no_pause=True, least_recover_days=1,
                                      no_pause_limit=0.5, no_pause_stats_days=5,
                                      no_limit_up=False, no_limit_down=False,
                                      other_limit=None, trade_mode=True,
                                      start_date=date_list[0], end_date=date_list[-1])
    new_stock_pool = (new_stock_pool.reindex(columns=code_list) > 0).values[:, None, :]
    new_stock_pool = np.ascontiguousarray(new_stock_pool)
    store_augmented_matrix(new_stock_pool, f'{address}/Label/new_stock_pool.npy', offset_days=date_offset)
    store_augmented_matrix(new_stock_pool, f'{address}/ReduceLabel/new_stock_pool.npy', offset_days=date_offset)


if __name__ == '__main__':
    make_stock_pool()
