# coding: utf-8
# Author：fengchi863
# Date ：2022/4/15 14:04

from SimiStock.config.path_config import *
import pandas as pd
import numpy as np
from SimiStock.SimiStockGenerator.util import util


def get_quater(date):
    year = date // 10000
    month = date // 100 % 100
    if month in [1, 2, 3]:
        return f'{year}Q1'
    elif month in [4, 5, 6]:
        return f'{year}Q2'
    elif month in [7, 8, 9]:
        return f'{year}Q3'
    else:
        return f'{year}Q4'


def get_half(date):
    year = date // 10000
    month = date // 100 % 100
    if month in [1, 2, 3, 4, 5, 6]:
        return f'{year}H1'
    else:
        return f'{year}H2'


if __name__ == '__main__':
    start_date = 20180101
    end_date = 20200630
    block_data = pd.read_pickle(data_path + 'block_data_95.pkl')
    block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
    df = block_data.copy()
    df['折扣比例'] = 1 - df['折价比例']
    df['month'] = df['交易日期'] // 100
    df['quater'] = df['交易日期'].apply(lambda x: get_quater(x))
    df['half'] = df['交易日期'].apply(lambda x: get_half(x))

    ret_df = pd.DataFrame()
    ret_df.loc[f'1个月算1次', '项目数量'] = len(df.groupby(['month', '股票代码']).agg('count'))