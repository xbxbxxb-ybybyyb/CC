# -*- coding: utf-8 -*-
import IO
import sys
import pandas as pd
from datetime import datetime, timedelta
from xquant.marketdata import MarketData
mdp = MarketData()

def view_bar(num,tot,s):
    rate = (num+1)/(tot)
    rate_num = (int(rate*100))
    n = rate_num//3
    r = '\r[%s>%s]%d%%-%s' % ('='*n,'-'*(33-n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')
def find_repeat_tick(tick_data, repeat_filter_cols):
    tick_data['inf_str'] = tick_data[repeat_filter_cols].apply(lambda x: str(x.values), axis=1)
    tick_data['last_inf_str'] = tick_data['inf_str'].shift(1)
    return tick_data['inf_str'] == tick_data['last_inf_str']
def get_before_time(trading_time, bef_time):
    if bef_time==0:
        return trading_time
    trading_time = datetime.strptime(str(trading_time), '%H%M%S%f')
    before_trading_time = (trading_time - timedelta(milliseconds=bef_time))

    if (before_trading_time < datetime.strptime('130000000', '%H%M%S%f')) and (trading_time >= datetime.strptime('130000000', '%H%M%S%f')):
        before_trading_time = before_trading_time - timedelta(hours=1.5)
    return int(before_trading_time.strftime('%H%M%S%f')[:-3])
def update_data_tickab(start_date, end_date, basic_file_path, result_path):
    repeat_filter_cols = ['NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'TotalBidQty', 'TotalOfferQty',
                          'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'TradingPhaseCode'] + \
                         ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                         ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)]

    basic_df = IO.read_data([start_date, end_date], alt=basic_file_path)
    for tradingday_timestamp, df in basic_df.groupby(level=0):
        tradingday = tradingday_timestamp.strftime('%Y%m%d')
        result_df_list = []
        for index, d in df.iterrows():
            stock_code = index[1]
            # interception_time = d['ZT_Time']
            print(tradingday, stock_code)
            try:
                tick_data = mdp.get_data_by_date('stock', stock_code, tradingday)
                tick_data['MDTime'] = tick_data['MDTime'].astype(int)
                # 时间筛选
                # tick_data = tick_data[tick_data['MDTime']<interception_time]
                # lag_dic = {'SH': 1000, 'SZ': 2000}  # ms
                # lag_time= int(get_before_time(int(interception_time),lag_dic[stock_code[-2:]]))
                tick_data = tick_data[tick_data['MDTime'] < 91900000]#策略使用transaction触发, 由于tick相较于transaction延迟，截取时将时间戳提前一定时间
                # tick去重
                bef_len = len(tick_data)
                tick_data['repeat_filter'] = find_repeat_tick(tick_data.copy(), repeat_filter_cols)
                tick_data = tick_data[~tick_data['repeat_filter']]
                aft_len = len(tick_data)
                if (bef_len!=aft_len): print('repeat tick num:%d'%(bef_len-aft_len))
                # 915之后时间筛选
                tick_data = tick_data[tick_data['MDTime']>=91500000]

                tick_data['dt'] = tick_data['MDDate'].apply(pd.Timestamp)
                tick_data['Ticker'] = stock_code
                tick_data = tick_data.set_index(['dt', 'Ticker'])

                used_cols = ['MDTime', 'NumTrades', 'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'HighPx','LowPx',
                             'TotalBidQty', 'TotalOfferQty','WeightedAvgBidPx', 'WeightedAvgOfferPx'] + \
                            ['Buy%dPrice' % (i) for i in range(1, 11)] + ['Sell%dPrice' % (i) for i in range(1, 11)] + \
                            ['Buy%dOrderQty' % (i) for i in range(1, 11)] + ['Sell%dOrderQty' % (i) for i in range(1, 11)] + \
                            ['Buy%dNumOrders' % (i) for i in range(1, 11)] + ['Sell%dNumOrders' % (i) for i in range(1, 11)]
                tick_data = tick_data[used_cols]
                tick_data['pre_close'] = d['pre_close']
                tick_data['ff_shares'] = d['float_shares']
                result_df_list.append(tick_data)
            except Exception as e:
                print(e)
        result_df = pd.concat(result_df_list)
        result_df.to_pickle('%s%s.pkl'%(result_path, tradingday))

basic_file_path = '/data/user/013550/shared_files/for_qyh/basic_dt_new_20160101_20211231.h5'
result_path = '/dfs/group/800463/data/mercury/everyday_Data/tick919/'
update_data_tickab(20160101,20211231,basic_file_path,result_path)