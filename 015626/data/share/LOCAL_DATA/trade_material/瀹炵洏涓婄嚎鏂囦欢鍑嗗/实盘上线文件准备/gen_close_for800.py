
# coding: utf-8

import sys
import pandas as pd
import numpy as np
import json
import datetime


def getClose(file_name, date_str, zz500, hs300):
    data = pd.HDFStore(file_name)
    key = [item for item in list(data.root._v_groups.keys())]
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    shareData = data.select(key[0], where="dt=='{}'".format(from_date))
    close_dt = shareData[['S_DQ_CLOSE', 'S_DQ_PRECLOSE']].reset_index()
    close_list = []
    
    write_str = 'symbol, close, preClose\n'
    for item in zz500:
        close = close_dt[close_dt['Ticker']==item]['S_DQ_CLOSE'].values[0]
        preClose = close_dt[close_dt['Ticker']==item]['S_DQ_PRECLOSE'].values[0]
        #close_dict = dict()
        #close_dict['symbol'] = item
        #close_dict['close'] = close
        #close_list.append(close_dict)
        write_str = write_str + item + ',' + str(close) + ',' + str(preClose) + '\n'

    #s = json.dumps(close_list)
    f = open("ZZ500_price.csv", "w")
    f.write(write_str)
    f.close()
    #print("load {} close data".format(len(close_list)))

    close_list = []
    write_str = 'symbol, close, preClose\n'
    for item in hs300:
        close = close_dt[close_dt['Ticker']==item]['S_DQ_CLOSE'].values[0]
        preClose = close_dt[close_dt['Ticker']==item]['S_DQ_PRECLOSE'].values[0]
        write_str = write_str + item + ',' + str(close) + ',' + str(preClose) + '\n'
        #close_dict = dict()
        #close_dict['symbol'] = item
        #close_dict['close'] = close
        #close_list.append(close_dict)

    #s = json.dumps(close_list)
    f = open("hs300_price.csv", "w")
    f.write(write_str)
    f.close()

def get_stock_list(file_name, date_str):
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    to_date = from_date + datetime.timedelta(1)
    to_date_str = datetime.datetime.strftime(to_date, "%Y-%m-%d")

    data = pd.HDFStore(file_name)

    index_weight_hs300 = data.select('index_weight_hs300', where="dt>='{}'&dt<'{}'".format(from_date, to_date))
    index_weight_zz500 = data.select('index_weight_zz500', where="dt>='{}'&dt<'{}'".format(from_date, to_date))

    hs_stock_list = index_weight_hs300[index_weight_hs300['index_weight_hs300'] > 0].index.get_level_values(1).to_list()
    zz500_stock_list = index_weight_zz500[index_weight_zz500['index_weight_zz500'] > 0].index.get_level_values(1).to_list()

    zz500_stock_list.sort()
    hs_stock_list.sort()
    data.close()
    return zz500_stock_list, hs_stock_list


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("need 3 arguments, just like as 2020-12-31 \'/data/group/800002/FutureTrader/test/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5\' \'AShareEODPrices.h5\'")
    else:
        trade_date = sys.argv[1]
        date_str = sys.argv[2]
        daily_file = '/data/group/800445/future_data/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'
        share_price_file = sys.argv[3]
        zz500, hs300 = get_stock_list(daily_file, trade_date)
        getClose(share_price_file, date_str, zz500, hs300)
