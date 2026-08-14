# -*- coding: utf-8 -*-
import IO
import pandas as pd
from xquant.marketdata import MarketData
mdp = MarketData()
import os
assert os.system('pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl')==0
from xdbJG.stockdata import StockData

import numpy as np
a = StockData()

def get_tick_data(stock_code, tradingday):
    df = a.get_tickfull(tradingday,stock_code)
    rename_dic={'md_time':'MDTime','total_num_trades':'NumTrades','total_volume':'TotalVolumeTrade','total_amount':'TotalValueTrade',
                'last_px':'LastPx','high_px':'HighPx','low_px':'LowPx','bid_order_qty':'TotalBidQty','ask_order_qty':'TotalOfferQty',
                'bid_avg_px':'WeightedAvgBidPx','ask_avg_px':'WeightedAvgOfferPx','last_local_index':'LastLocalIndex'}
    for i in range(1,11):
        rename_dic['bid_price%d'%i]='Buy%dPrice' % (i)
        rename_dic['bid_qty%d' % i] = 'Buy%dOrderQty' % (i)
        rename_dic['bid_order_nums%d' % i] = 'Buy%dNumOrders' % (i)
        rename_dic['ask_price%d' % i] = 'Sell%dPrice' % (i)
        rename_dic['ask_qty%d' % i] = 'Sell%dOrderQty' % (i)
        rename_dic['ask_order_nums%d' % i] = 'Sell%dNumOrders' % (i)
    df=df.rename(columns=rename_dic)
    return df


def update_data_tickab(start_date, end_date, basic_file_path, result_path):
    basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    for tradingday_timestamp, df in basic_df.groupby(level=0):
        tradingday = tradingday_timestamp.strftime('%Y%m%d')
        result_df_list = []
        for index, d in df.iterrows():
            stock_code = index[1]
            interception_time = d['ZT_Time']
            trigger_price = d['trigger_price']
            print(tradingday, stock_code)
            try:
                trans_data = mdp.get_data_by_date('Transaction', stock_code, tradingday)
                trans_data['MDTime'] = trans_data['MDTime'].astype(int)
                trans_data = trans_data[trans_data['MDTime'] <= interception_time]  # 时间筛选
                last_trans = trans_data[(trans_data['MDTime'] == interception_time) & (trans_data['TradePrice'] >= trigger_price)].iloc[0]
                last_appl_seq_num=int(last_trans['ApplSeqNum'])

                tick_data = get_tick_data(stock_code, tradingday)
                tick_data['MDTime'] = tick_data['MDTime'].astype(int)
                # 时间筛选
                tick_data = tick_data[tick_data['MDTime']<=interception_time]
                tick_data = tick_data[tick_data['MDTime'] >= 91500000]
                # ApplSeqNum筛选
                tick_data = tick_data[tick_data['appl_seq_num'] <last_appl_seq_num]


                tick_data['dt'] = pd.to_datetime(tradingday)
                tick_data['Ticker'] = stock_code
                tick_data = tick_data.set_index(['dt', 'Ticker'])

                used_cols = ['MDTime', 'NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'HighPx','LowPx',
                             'TotalBidQty', 'TotalOfferQty','WeightedAvgBidPx', 'WeightedAvgOfferPx','LastLocalIndex'] + \
                            ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                            ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)] + \
                            ['Buy%dNumOrders' % (i) for i in range(1, 11)] + ['Sell%dNumOrders' % (i) for i in range(1, 11)] + \
                            ['appl_seq_num']
                tick_data = tick_data[used_cols]
                tick_data['pre_close'] = d['pre_close']
                tick_data['ff_shares'] = d['float_shares']
                result_df_list.append(tick_data)
            except Exception as e:
                print(e)
        result_df = pd.concat(result_df_list)
        result_df.to_pickle('%s%s.pkl'%(result_path, tradingday))

if __name__ == '__main__':
    import os
    start_date,end_date=20170101,20170630
    basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v3/Basic_zt_001_20150901_20191231.h5'
    result_path = '/dfs/group/800463/data/xdb_data_lag3_test/T_europa_jupiter_test/'
    #
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    from xquant.factordata import FactorData
    s = FactorData()
    tradingday_list = s.tradingday(start_date, end_date)
    pool_num = 30
    pool_num=min(pool_num,len(tradingday_list))
    from multiprocessing import Pool
    pool = Pool(pool_num)
    task_list = []
    for tradingday in tradingday_list:
        task_list.append(pool.apply_async(update_data_tickab,args=(tradingday, tradingday, basic_file_path,result_path)))
    pool.close()
    pool.join()
