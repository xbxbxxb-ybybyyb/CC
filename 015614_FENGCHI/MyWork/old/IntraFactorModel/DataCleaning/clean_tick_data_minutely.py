# @Time : 2020/5/27 11:08
# @Author : Zhichen Lu
# @File : clean_tick_data_minutely.py
import itertools
import os
from multiprocessing import Pool

import gc
import pandas as pd
import xquant.marketdata as mkt_data

from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import trade_minutes, get_date_range

start, end = 20140101, 20200528

stock_pool = clean_stock_list('ALL').loc[20140101:20200528]  # .loc[20140101:20200528]
isin = stock_pool.sum(axis=0)
stock_list = isin[isin > 0].index.tolist()
stock_list = list(map(lambda x: str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH', stock_list))

global_date_list = get_date_range(20140101, 20200528)
datetime_list = list(itertools.product(global_date_list, trade_minutes))


def get_minutely_tick_by_year_month(stk, year_month):
    stk = '000001.SZ'
    year_month = '201801'
    mdp = mkt_data.MarketData()
    data = mdp.get_data_by_year_month("Stock", stk, str(year_month), ["3"], sort_by_receive_time=True)
    if len(data) == 0:
        return pd.DataFrame(columns=['Buy1Price', 'Buy2Price', 'Buy3Price',
                                     'Sell1Price', 'Sell2Price', 'Sell3Price', 'Buy1OrderQty', 'Buy2OrderQty', 'Buy3OrderQty',
                                     'Sell1OrderQty', 'Sell2OrderQty', 'Sell3OrderQty'])
    data_col = data[['MDDate', 'MDTime', 'Buy1Price', 'Buy2Price', 'Buy3Price',
                     'Sell1Price', 'Sell2Price', 'Sell3Price', 'Buy1OrderQty', 'Buy2OrderQty', 'Buy3OrderQty',
                     'Sell1OrderQty', 'Sell2OrderQty', 'Sell3OrderQty']]
    data_col['minutes'] = data_col['MDTime'].apply(lambda x: x[:4])
    data_col['second'] = data_col['MDTime'].apply(lambda x: x[4:])
    data_col = data_col[data_col['minutes'].apply(lambda x: int(x) >= 930)]
    data_col = data_col.groupby(['MDDate', 'minutes']).first()
    data_col = data_col.reset_index()
    data_col['minutes'] = data_col['minutes'].astype(int)
    data_col['MDDate'] = data_col['MDDate'].astype(int)
    data_col = data_col.set_index(['MDDate', 'minutes']).drop('MDTime', axis=1)
    return data_col


def get_minutely_tick_by_stk(stk, start=20140101, end=20200528):
    date_list = get_date_range(start, end)
    year_month_list = list(set([x // 100 for x in date_list]))
    year_month_list.sort()
    result = pd.DataFrame()
    for year_month in year_month_list:
        temp_df = get_minutely_tick_by_year_month(stk, year_month)
        result = result.append(temp_df)
    result = result.reindex(datetime_list)

    return result


out_by_factor = '/data/group/800319/junkData/IntraFactorModel/MinutelyTickByFactor/'
out_path = '/data/group/800319/junkData/IntraFactorModel/MinutelyTickByStock/'
if not os.path.exists(out_path):
    os.mkdir(out_path)

if not os.path.exists(out_by_factor):
    os.mkdir(out_by_factor)

def load_wraper(stk):
    stk_id = int(stk[:-3])
    if os.path.exists(out_path + '%d.h5' % stk_id):
        print(stk, 'exist')
        return 0
    try:
        result = get_minutely_tick_by_stk(stk)
        pd.to_pickle(result, out_path + '%d.pkl' % stk_id)
        if len(result) > 0:
            print(result.index[0], result.index[-1])
        print(stk, 'done')
        # result.to_hdf(out_path+'%d.h5'%stk_id,str(stk_id),format='t')
    except:
        print(stk, 'Wrong')
        pd.to_pickle(result, out_path + 'Wrong_%d.pkl' % stk_id)
        # pd.DataFrame().to_hdf(out_path+'Wrong_%d.h5'%stk_id,str(stk_id))


def load_data_to_local():
    pool = Pool(10)
    pool.map(load_wraper, stock_list)
    pool.close()
    pool.join()


def load_from_local_stkly(stk):
    stk_id = int(stk[:-3])
    temp_df = pd.read_pickle(out_path + '%d.pkl' % stk_id)
    print(stk, 'done')
    return temp_df


def load_from_loacal_by_factor():
    result_dict = {}
    pool = Pool(20)
    for stk_code in stock_list:
        result_dict[int(stk_code[:-3])] = pool.apply_async(load_from_local_stkly, (stk_code,))
    pool.close()
    pool.join()
    col_list = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Sell1Price', 'Sell2Price', 'Sell3Price',
                'Buy1OrderQty', 'Buy2OrderQty', 'Buy3OrderQty', 'Sell1OrderQty', 'Sell2OrderQty', 'Sell3OrderQty']

    for col in col_list:
        factor_by_stk = {}
        for stk in result_dict:
            factor_by_stk[stk] = result_dict[stk].get()[col]
            print(stk)
        result_pn = pd.DataFrame(factor_by_stk)
        result_pn.to_hdf(out_by_factor + col + '.h5', col, format='t')
        del result_pn
        gc.collect()


load_from_loacal_by_factor()
# load_wraper('603357.SH')
# load_data_to_local()
