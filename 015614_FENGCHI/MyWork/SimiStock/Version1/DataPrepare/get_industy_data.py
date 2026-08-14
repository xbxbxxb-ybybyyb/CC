# coding: utf-8
# Author：fengchi863
# Date ：2022/3/8 16:21

from xquant.factordata import FactorData
from dataApi import indName, getData, tradeDate
from SimiStock.config.path_config import *
from SimiStock.SimiStockGenerator.util import util

if __name__ == '__main__':
    start_date = 20171101
    end_date = 20211231
    date_list = tradeDate.get_date_range(start_date, end_date)
    """SW1"""
    df = getData.get_daily_1factor('SW1', date_list=date_list)
    util.save_df2pkl(df, data_path, 'SW1.pkl')
    print(1)