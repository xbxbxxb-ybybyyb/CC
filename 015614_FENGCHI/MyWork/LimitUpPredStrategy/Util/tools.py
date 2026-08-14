# coding: utf-8
# Author：fengchi863
# Date ：2021/4/2 16:29

import pandas as pd
from xquant.factordata import FactorData
import datetime
from LimitUpPredStrategy.dataApi.stockList import trans_int2windcode

def get_stock_name_dict():
    # stock_code_and_name = pd.read_excel('/data/user/fengchi/MyWork/BullClient/other_data/stock_code_and_name.xlsx',
    #                                     encoding='gb18030')
    # stock_code_and_name_dict = {}
    #
    # for idx, curr in stock_code_and_name.iterrows():
    #     stock_code = curr['证券代码']
    #     stock_name = curr['证券简称']
    #     stock_code_and_name_dict[stock_code] = stock_name
    today_date = get_today_date()
    fd = FactorData()
    df = fd.get_factor_value('Basic_factor', mddate=['%s' % today_date], factor_names=['short_name'])
    stock_code_and_name_dict = df['short_name'].to_dict()
    return stock_code_and_name_dict

def get_stock_name(stk_id, stock_name_dict):
    if type(stk_id) == int:
        stk_id = trans_int2windcode(stk_id)
    if stk_id in list(stock_name_dict.keys()):
        return stock_name_dict[stk_id]
    else:
        return stk_id

def get_today_date():
    now_datetime = datetime.datetime.now()
    now_date = int(now_datetime.strftime('%Y%m%d'))
    return now_date