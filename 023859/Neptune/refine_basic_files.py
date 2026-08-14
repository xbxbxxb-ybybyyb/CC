import pandas as pd
import IO

def generate_neptune_basic_stocks_pool(start_date, end_date, md):
    zz1000 = IO.read_data([start_date, end_date], columns=['index_1000'],
                          alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
    trading_days = s.tradingday(start_date, end_date)
    res = {}
    for date in tqdm(trading_days):
        if date < '20170101':
            zz1000_list = list(zz1000[zz1000['index_1000']].loc[pd.to_datetime(date)].index)
            # stockPool = list(set(zz1000_list) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
            #     s.hset('INDEX', date, 'HS300')['stock']))
            stockPool = list(set(zz1000_list))
        else:
            # stockPool = list(
            #     set(s.hset('INDEX', date, 'ZZ1000')['stock']) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
            #         s.hset('INDEX', date, 'HS300')['stock']))
            stockPool = list(set(s.hset('INDEX', date, 'ZZ1000')['stock']))
        # stockPool_st_out = s.stock_filter(stockPool, date, 'STPT')['stock'].tolist()
        # md_date = md.loc[pd.to_datetime(date)]
        # filter_condition = ((md_date['list_len'] > 120) & (md_date['last_close_is_zt'] == 0) & (md_date['last_close_is_dt'] == 0))
        # market_available_stock_list = list(md_date[filter_condition].index)
        # res[date] = list(set(stockPool_st_out) & set(market_available_stock_list))
        res[date] = stockPool
    return res

start_date, end_date = 20160101, 20201231
basic_ori = pd.read_pickle('')

basic_ori['tag'] =