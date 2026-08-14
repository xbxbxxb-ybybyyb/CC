# coding: utf-8
# Author：fengchi863
# Date ：2020/6/16 11:05
import pandas as pd

from conf.path_config import *


def get_tick_data(stk_id, date):
    return pd.read_pickle(tick_data_path + '%d/%d.pkl' % (stk_id, date))


def get_transaction_data(stk_id, date):
    return pd.read_pickle(trans_data_path + '%d/%d.pkl' % (stk_id, date))
