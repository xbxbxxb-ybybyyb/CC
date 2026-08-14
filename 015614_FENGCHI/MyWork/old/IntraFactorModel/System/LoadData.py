# @Time : 2020/6/16 13:11
# @Author : Zhichen Lu
# @File : LoadData.py

import datetime
import os
from multiprocessing import Pool

import pandas as pd
from xquant.marketdata import MarketData

from conf.path_config import root_path
from dataApi.stockList import clean_stock_list


# dfs是hdfs连接，若不传，会创建一个新的连接，在sparkmr中使用需要传入该参数，详见sparkmr的demo


# if not os.path.exists(out_path):
#     os.mkdir(out_path)

def load_tick_data(stk, month, out_path=root_path + 'IntradayData/TickData/'):
    mdp = MarketData()
    temp_out_path = out_path + '%d/' % int(stk[:-3])
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    if not os.path.exists(temp_out_path):
        os.mkdir(temp_out_path)
    col_list = ['MDDate', 'MDTime', 'Buy1Price', 'Buy1OrderQty', 'Sell1Price', 'Sell1OrderQty', 'Buy2Price', 'Buy2OrderQty', 'Sell2Price', 'Sell2OrderQty', 'Buy3Price',
                'Buy3OrderQty', 'Sell3Price', 'Sell3OrderQty', 'Buy4Price', 'Buy4OrderQty', 'Sell4Price', 'Sell4OrderQty', 'Buy5Price', 'Buy5OrderQty', 'Sell5Price',
                'Sell5OrderQty', 'Buy6Price', 'Buy6OrderQty', 'Sell6Price', 'Sell6OrderQty', 'Buy7Price', 'Buy7OrderQty', 'Sell7Price', 'Sell7OrderQty', 'Buy8Price',
                'Buy8OrderQty', 'Sell8Price', 'Sell8OrderQty', 'Buy9Price', 'Buy9OrderQty', 'Sell9Price', 'Sell9OrderQty', 'Buy10Price', 'Buy10OrderQty', 'Sell10Price',
                'Sell10OrderQty']
    rename_dict = {}
    for i in range(1, 11):
        rename_dict['Buy%dPrice' % i] = 'BidPrice%d' % i
        rename_dict['Sell%dPrice' % i] = 'AskPrice%d' % i
        rename_dict['Buy%dOrderQty' % i] = 'BidVolume%d' % i
        rename_dict['Sell%dOrderQty' % i] = 'AskVolume%d' % i
    df = mdp.get_data_by_year_month("Stock", stk, month, ["3"], sort_by_receive_time=True)
    df.columns.tolist()
    df = df[col_list]
    df = df.rename(columns=rename_dict)
    df['TimeStamp'] = df['MDDate'] + df['MDTime']
    df['TimeStamp'] = df['TimeStamp'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S%f'))
    date_list = list(set(df['MDDate']))
    for day in date_list:
        temp_df = df[df['MDDate'] == day].drop(['MDDate', 'MDTime'], axis=1)
        if len(temp_df) == 0:
            continue
        temp_df.index = list(range(len(temp_df)))
        pd.to_pickle(temp_df, temp_out_path + '%s.pkl' % day)


# stk = '000001.SZ'
# month = '201801'

def load_trans_data(stk, month, out_path=root_path + 'IntradayData/TransData/'):
    mdp = MarketData()
    temp_out_path = out_path + '%d/' % int(stk[:-3])
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    if not os.path.exists(temp_out_path):
        os.mkdir(temp_out_path)
    df = mdp.get_data_by_year_month("Transaction", stk, month, sort_by_receive_time=True)
    # mdp.get_data_by_date("Transaction", stk, '20180228')
    # mdp.get_data_by_year_month("Transaction", stk, '201801', sort_by_receive_time=True)
    df = df[['MDDate', 'MDTime', 'TradePrice', 'TradeQty', 'TradeType', 'TradeBSFlag']].rename(
        columns={'TradePrice': 'Price', 'TradeQty': 'Volume'})
    df['TimeStamp'] = df['MDDate'] + df['MDTime']
    df['TimeStamp'] = df['TimeStamp'].apply(lambda x: datetime.datetime.strptime(x, '%Y%m%d%H%M%S%f'))
    date_list = list(set(df['MDDate']))
    for day in date_list:
        temp_df = df[df['MDDate'] == day].drop(['MDDate', 'MDTime'], axis=1)
        if len(temp_df) == 0:
            continue
        temp_df.index = list(range(len(temp_df)))
        pd.to_pickle(temp_df, temp_out_path + '%s.pkl' % day)


# load_tick_data(stk = '000001.SZ',month = '201801')
# load_trans_data(stk = '000001.SZ',month = '201801')
wrong_log_path = root_path + 'IntradayData/'


def tick_wraper(para):
    try:
        load_tick_data(para[0], para[1])
        print(para, 'Tick Done')
    except:
        print(para, 'Tick Wrong!')
        pd.to_pickle([], wrong_log_path + 'Tick_%s_%s_Wong.pkl' % para)


def trans_wraper(para):
    try:
        load_trans_data(para[0], para[1])
        print(para, 'Trans Done')
    except:
        print(para, 'Trans Wrong!')
        pd.to_pickle([], wrong_log_path + 'Trans_%s_%s_Wong.pkl' % para)


def main():
    stock_pool = clean_stock_list('ALL').loc[20180102:20181231]
    isin = stock_pool.sum()
    stock_pool = stock_pool[isin[isin > 0].index]
    stock_pool.columns = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x).zfill(6) + '.SH' for x in stock_pool.columns]
    para_list = []
    for i in range(1, 13):
        month = '2018' + str(i).zfill(2)
        para_list = para_list + [(x, month) for x in stock_pool.columns]
    # tick_wraper(para_list[0])
    # trans_wraper(para_list[0])
    pool = Pool(12)
    for para in para_list:
        pool.apply_async(trans_wraper, (para,))
        # pool.apply_async(tick_wraper, (para,))
    pool.close()
    pool.join()


def del_file(base_path):
    stk_list = os.listdir(base_path)
    del_list = []
    for stk in stk_list:
        file_list = os.listdir(base_path + '%s/' % stk)
        if len(file_list) == 0:
            continue
        del_list += [base_path + '%s/%s' % (stk, file_name) for file_name in file_list]
    pool = Pool(12)
    pool.map(os.remove, del_list)
    pool.close()
    pool.join()
    print(base_path, 'done')


if __name__ == "__main__":
    # del_file(root_path + 'IntradayData/TransData_old/')
    # del_file(root_path + 'IntradayData/TransData_old2/')
    # main()
    # load_tick_data('601360.SH', '201801')
    load_trans_data('601360.SH', '201802')
    # main()
    # del_file('/data/group/800319/junkData/IntraFactorModel/IntradayData/TickData_old/')
    # del_file('/data/group/800319/junkData/IntraFactorModel/IntradayData/TransData_old/')
    # main()
