import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from HFfactor.MinFactorSuper.Utility.LoadBigData import get_minute_data, get_all_stock
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import store_augmented_matrix
from HFfactor.MinFactorSuper.RealTime.Desample import ReduceMaterial
from dataApi.tradeDate import get_date_range, get_pre_trade_date, \
    get_trade_date_interval, get_recent_trade_date
import pandas as pd
import numpy as np
import time


def make_label(end_date=None, start_date=20140101, address='/arch1/group/800442/800319/MinFactorSuper/'):
    date_list = get_date_range(start_date, end_date, dividing_point=19)
    end_date = min(get_pre_trade_date(date_list[-1], -2), get_recent_trade_date(dividing_point=19))
    date_list = get_date_range(start_date, end_date)
    start_date = date_list[0]
    date_offset = get_trade_date_interval(start_date, 20140101)
    code_list = get_all_stock(end_date)
    adj_close = get_minute_data('close_adj', date_list, code_list)
    limit_status = get_minute_data('limit_status', date_list, code_list)
    amt = get_minute_data('amt', date_list, code_list)

    future = adj_close.reshape(-1, adj_close.shape[-1])
    future = (future[243:-241] / future[1:-483] - 1).reshape(
        -1, 242, adj_close.shape[-1])
    limit_status = limit_status.reshape(-1, limit_status.shape[-1])[1:-483].reshape(
        -1, 242, limit_status.shape[-1]) == 0
    trade_amt = amt.reshape(-1, amt.shape[-1])[2:-482].reshape(-1, 242, amt.shape[-1])

    future = np.ascontiguousarray(future, dtype='float32')
    limit_status = np.ascontiguousarray(limit_status)
    trade_amt = np.ascontiguousarray(trade_amt, dtype='float32')

    store_augmented_matrix(future, f'{address}/Label/future.npy', offset_days=date_offset)
    store_augmented_matrix(limit_status, f'{address}/Label/limit_status.npy', offset_days=date_offset)
    store_augmented_matrix(trade_amt, f'{address}/Label/trade_amt.npy', offset_days=date_offset)

    reduce = ReduceMaterial()
    future = reduce.last(future)
    limit_status = reduce.last(limit_status)
    trade_amt = reduce.sum(trade_amt)

    store_augmented_matrix(future, f'{address}/ReduceLabel/future.npy', offset_days=date_offset)
    store_augmented_matrix(limit_status, f'{address}/ReduceLabel/limit_status.npy', offset_days=date_offset)
    store_augmented_matrix(trade_amt, f'{address}/ReduceLabel/trade_amt.npy', offset_days=date_offset)


if __name__ == '__main__':
    make_label()
