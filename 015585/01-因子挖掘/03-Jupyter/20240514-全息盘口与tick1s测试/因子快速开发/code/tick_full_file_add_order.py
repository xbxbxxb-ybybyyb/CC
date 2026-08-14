# 对europa tick_full类数据，增加数列以描述该行对应的订单信息
import pandas as pd
import numpy as np
import os
import decimal

def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def func_add_order_2fulltick(base_path, date, result_path):
    # base_path = '/dfs/group/800463/data/xdb_data_europa/xdb_tickfull/'
    # date = '20170103'
    print(date)
    tick_df = pd.read_pickle(base_path + date + '.pkl')
    # 订单类别
    '''
        挂买/卖，未成交------成交额没有变动，有一边挂单总量增加
        挂买/卖，部分或全部成交------成交额增加，对面挂单总量减少，自己挂单总量（可能）增加
        撤买/卖------成交额没有变动，有一边挂单总量减少
    订单类别：
        'b1'：挂买，未成交
        'b2'：挂买，有成交
        'o1'：挂卖，未成交
        'o2'：挂卖，有成交
        'cb'：撤买
        'co'：撤卖
    '''
    tick_df['OrderType'] = np.nan
    tick_df['ValueTrade'] = (tick_df.groupby(["dt", "Ticker"])['TotalValueTrade'].diff().fillna(tick_df['TotalValueTrade'])).apply(lambda x : round_(x,8))
    tick_df['DeltaBidQty'] = (tick_df.groupby(["dt", "Ticker"])['TotalBidQty'].diff().fillna(tick_df['TotalBidQty'])).apply(lambda x : round_(x,2))
    tick_df['DeltaOfferQty'] = (tick_df.groupby(["dt", "Ticker"])['TotalOfferQty'].diff().fillna(tick_df['TotalOfferQty'])).apply(lambda x : round_(x,2))

    tick_df['TotalBidValue'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['TotalOfferValue'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['DeltaBidValue'] = (tick_df.groupby(["dt", "Ticker"])['TotalBidValue'].diff().fillna(tick_df['TotalBidValue'])).apply(lambda x : round_(x,2))
    tick_df['DeltaOfferValue'] = (tick_df.groupby(["dt", "Ticker"])['TotalOfferValue'].diff().fillna(tick_df['TotalOfferValue'])).apply(lambda x : round_(x,2))

    tick_df.loc[(tick_df['ValueTrade'] == 0) & (tick_df['DeltaBidQty'] > 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'b1'
    tick_df.loc[(tick_df['ValueTrade'] == 0) & (tick_df['DeltaOfferQty'] > 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'o1'
    tick_df.loc[(tick_df['ValueTrade'] == 0) & (tick_df['DeltaBidQty'] < 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'cb'
    tick_df.loc[(tick_df['ValueTrade'] == 0) & (tick_df['DeltaOfferQty'] < 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'co'
    tick_df.loc[(tick_df['ValueTrade'] > 0) & (tick_df['DeltaOfferQty'] < 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'b2'
    tick_df.loc[(tick_df['ValueTrade'] > 0) & (tick_df['DeltaBidQty'] < 0) & (tick_df['MDTime'] >= 93000000), 'OrderType'] = 'o2'
    # 订单数量
    tick_df.loc[tick_df['OrderType'] == 'b1','OrderQty'] = tick_df.loc[tick_df['OrderType'] == 'b1','DeltaBidQty']
    tick_df.loc[tick_df['OrderType'] == 'o1','OrderQty'] = tick_df.loc[tick_df['OrderType'] == 'o1','DeltaOfferQty']
    tick_df.loc[tick_df['OrderType'] == 'cb','OrderQty'] = -tick_df.loc[tick_df['OrderType'] == 'cb','DeltaBidQty']
    tick_df.loc[tick_df['OrderType'] == 'co','OrderQty'] = -tick_df.loc[tick_df['OrderType'] == 'co','DeltaOfferQty']
    tick_df.loc[tick_df['OrderType'] == 'b2','OrderQty'] = tick_df.loc[tick_df['OrderType'] == 'b2','DeltaBidQty'] - \
                                                           tick_df.loc[tick_df['OrderType'] == 'b2','DeltaOfferQty']
    tick_df.loc[tick_df['OrderType'] == 'o2','OrderQty'] = tick_df.loc[tick_df['OrderType'] == 'o2','DeltaOfferQty'] - \
                                                           tick_df.loc[tick_df['OrderType'] == 'o2','DeltaBidQty']
    # 订单价格：挂的价格，如果有成交，再分为全部成交（最新价格即为估计值）和部分成交（用挂单的delta估算）
    tick_df.loc[tick_df['OrderType'] == 'b1','OrderPrice'] = tick_df.loc[tick_df['OrderType'] == 'b1','DeltaBidValue'] \
                                                             / tick_df.loc[tick_df['OrderType'] == 'b1','DeltaBidQty']
    tick_df.loc[tick_df['OrderType'] == 'o1','OrderPrice'] = tick_df.loc[tick_df['OrderType'] == 'o1','DeltaOfferValue'] \
                                                             / tick_df.loc[tick_df['OrderType'] == 'o1','DeltaOfferQty']
    tick_df.loc[tick_df['OrderType'] == 'cb','OrderPrice'] = tick_df.loc[tick_df['OrderType'] == 'cb','DeltaBidValue'] \
                                                             / tick_df.loc[tick_df['OrderType'] == 'cb','DeltaBidQty']
    tick_df.loc[tick_df['OrderType'] == 'co','OrderPrice'] = tick_df.loc[tick_df['OrderType'] == 'co','DeltaOfferValue'] \
                                                             / tick_df.loc[tick_df['OrderType'] == 'co','DeltaOfferQty']
    tick_df.loc[(tick_df['OrderType'] == 'b2') & (tick_df['DeltaBidQty'] > 0),'OrderPrice'] = \
        tick_df.loc[(tick_df['OrderType'] == 'b2') & (tick_df['DeltaBidQty'] > 0),'DeltaBidValue'] \
        / tick_df.loc[(tick_df['OrderType'] == 'b2') & (tick_df['DeltaBidQty'] > 0),'DeltaBidQty']
    tick_df.loc[(tick_df['OrderType'] == 'o2') & (tick_df['DeltaOfferQty'] > 0),'OrderPrice'] = \
        tick_df.loc[(tick_df['OrderType'] == 'o2') & (tick_df['DeltaOfferQty'] > 0),'DeltaOfferValue'] \
        / tick_df.loc[(tick_df['OrderType'] == 'o2') & (tick_df['DeltaOfferQty'] > 0),'DeltaOfferQty']
    tick_df.loc[(tick_df['OrderType'] == 'b2') & (tick_df['DeltaBidQty'] == 0),'OrderPrice'] = \
        tick_df.loc[(tick_df['OrderType'] == 'b2') & (tick_df['DeltaBidQty'] == 0),'LastPx']
    tick_df.loc[(tick_df['OrderType'] == 'o2') & (tick_df['DeltaOfferQty'] == 0),'OrderPrice'] = \
        tick_df.loc[(tick_df['OrderType'] == 'o2') & (tick_df['DeltaOfferQty'] == 0),'LastPx']
    #
    tick_df.to_pickle(result_path + date + '.pkl')
    return
base_path = '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfull_cs/'
result_path = '/dfs/group/800463/data/project2_prod/everyday_Data_931/next_tickfull_add_order_cs/'
date_list = list(os.listdir(base_path))
date_list = [i.replace('.pkl','') for i in date_list]

'''
# date_list_del = list(os.listdir(result_path))
# date_list_del = [i.replace('.pkl','') for i in date_list_del]
# date_list_del_new = []
# for i in date_list_del:
#     if (i >= '20160101') & (i <= '20201231'):
#         date_list_del_new.append(i)
# res_list = list(set(date_list_new) - set(date_list_del_new))
# print(res_list)
'''

from joblib import Parallel, delayed
Parallel(n_jobs=10)(delayed(func_add_order_2fulltick)(base_path, i, result_path) for i in date_list)