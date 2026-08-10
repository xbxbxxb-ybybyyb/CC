from xquant.marketdata import MarketData

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
from multifactor.data.utils import *

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(int(year),int(month),int(day),int(hour),int(minute),0)
    
def get_cfg_hfdata(para):
    mdp = MarketData()
    
    print(para)
    date = para[0]
    stock = para[1]
    weight = round(para[2],5)
    
    rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_transaction_tominute_v2/'
    pickle_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'
    csvpath = os.path.join(rootpath, str(date))
    filepath = os.path.join(csvpath, stock+'.csv')
    if os.path.exists(filepath):
        return
    
    tick = mdp.get_data_by_date("Stock", stock, str(date), ['3','5'])
    tickdf = pd.DataFrame()
    if len(tick) > 100:
        tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0))
        tick = tick.set_index('dt')
        tick['pricediff'] = abs(tick.LastPx.diff())
        tick['Bid1Amt'] = tick.Buy1Price * tick.Buy1OrderQty
        tick['Ask1Amt'] = tick.Sell1Price * tick.Sell1OrderQty
        tick['volume'] = tick.TotalVolumeTrade.diff()
        tick['VolStd'] = tick['volume']
        tick['amount'] = tick.TotalValueTrade.diff()
        tick['BidAskSpreadMean'] = tick['Sell1Price'] - tick['Buy1Price']

        tick['BuyNumOrdersSumMean'] = tick[['Buy'+str(i)+'NumOrders' for i in range(1,11)]].sum(axis = 1)
        tick['SellNumOrdersSumMean'] = tick[['Sell'+str(i)+'NumOrders' for i in range(1,11)]].sum(axis = 1)
        tick['BuyOrderQtySumMean'] = tick[['Buy'+str(i)+'OrderQty' for i in range(1,11)]].sum(axis = 1)
        tick['SellOrderQtySumMean'] = tick[['Sell'+str(i)+'OrderQty' for i in range(1,11)]].sum(axis = 1)
        tick['WeightBuyOrderQtySumMean'] = 0
        tick['WeightSellOrderQtySumMean'] = 0
        for i in range(1,11):
            tick['WeightBuyOrderQtySumMean'] += tick['Buy'+str(i)+'OrderQty'] * 0.8 ** (i-1)
            tick['WeightSellOrderQtySumMean'] += tick['Sell'+str(i)+'OrderQty'] * 0.8 ** (i-1)
        aggdict1 = {'BuyNumOrdersSumMean':'mean','SellNumOrdersSumMean':'mean','BuyOrderQtySumMean':'mean','SellOrderQtySumMean':'mean','WeightBuyOrderQtySumMean':'mean','WeightSellOrderQtySumMean':'mean'}

        tick['open'] = tick['LastPx']
        tick['high'] = tick['LastPx']
        tick['low'] = tick['LastPx']
        tick['close'] = tick['LastPx']
        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last'}

        pvcorrdf = tick[['minute','LastPx','volume']].groupby('minute').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf.columns = ['PxVolCorr']
        aggdict = {'Buy1NumOrders':'mean','Sell1NumOrders':'mean','BidAskSpreadMean':'mean','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std'}

        df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1})
        df1amt = df1amt.rename(columns = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'})
        
        # check price
        if df1amt.close.sum() > 0:    
            tickdf = df1amt.join(pvcorrdf)
    
    transaction = mdp.get_data_by_date("Transaction", stock, str(date), ['3','5'])
    transactiondf = pd.DataFrame()
    if len(transaction) > 100:
        transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        transaction['minute'] = transaction.dt.map(lambda x: x.replace(second=0,microsecond=0))
        transaction = transaction[transaction.TradePrice != 0]

        selldf = transaction[transaction.TradeBSFlag == 2]
        sellorder_money = selldf.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order = sellorder_money[sellorder_money.TradeMoney <= 40000]
        sell_mid_order = sellorder_money[(sellorder_money.TradeMoney > 40000) & (sellorder_money.TradeMoney <= 200000)]
        sell_big_order = sellorder_money[(sellorder_money.TradeMoney > 200000) & (sellorder_money.TradeMoney <= 1000000)]
        sell_super_order = sellorder_money[(sellorder_money.TradeMoney > 1000000)]
        sell_small_order = sell_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_smallorder_count','TradeMoney':'sell_smallorder_money','TradeQty':'sell_smallorder_volume'})
        sell_mid_order = sell_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_midorder_count','TradeMoney':'sell_midorder_money','TradeQty':'sell_midorder_volume'})
        sell_big_order = sell_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_bigorder_count','TradeMoney':'sell_bigorder_money','TradeQty':'sell_bigorder_volume'})
        sell_super_order = sell_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_superorder_count','TradeMoney':'sell_superorder_money','TradeQty':'sell_superorder_volume'})

        selldf = selldf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeSellNo':lambda x:len(x.unique())})
        selldf = selldf.rename(columns = {'TradeMoney':'SellTradeMoney','TradeQty':'SellTradeQuantity','TradePrice':'SellTradeNum','TradeSellNo':'SellUniqueOrderNum'})

        buydf = transaction[transaction.TradeBSFlag == 1]
        buyorder_money = buydf.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        buy_small_order = buyorder_money[buyorder_money.TradeMoney <= 40000]
        buy_mid_order = buyorder_money[(buyorder_money.TradeMoney > 40000) & (buyorder_money.TradeMoney <= 200000)]
        buy_big_order = buyorder_money[(buyorder_money.TradeMoney > 200000) & (buyorder_money.TradeMoney <= 1000000)]
        buy_super_order = buyorder_money[(buyorder_money.TradeMoney > 1000000)]
        buy_small_order = buy_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count','TradeMoney':'buy_smallorder_money','TradeQty':'buy_smallorder_volume'})
        buy_mid_order = buy_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count','TradeMoney':'buy_midorder_money','TradeQty':'buy_midorder_volume'})
        buy_big_order = buy_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count','TradeMoney':'buy_bigorder_money','TradeQty':'buy_bigorder_volume'})
        buy_super_order = buy_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count','TradeMoney':'buy_superorder_money','TradeQty':'buy_superorder_volume'})


        buydf = buydf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeBuyNo':lambda x:len(x.unique())})
        buydf = buydf.rename(columns = {'TradeMoney':'BuyTradeMoney','TradeQty':'BuyTradeQuantity','TradePrice':'BuyTradeNum','TradeBuyNo':'BuyUniqueOrderNum'})

        transactiondf = pd.concat([selldf, buydf, sell_small_order, sell_mid_order, sell_big_order, sell_super_order, buy_small_order, buy_mid_order, buy_big_order, buy_super_order], axis = 1)
    
    del(mdp)        
    result = pd.concat([tickdf, transactiondf], axis = 1)
    if len(result) == 0:
        return
    result['weight'] = weight
    result.loc[:str(date) + ' 112900'].append(result.loc[str(date) + ' 130000':]).to_csv(filepath)
    

def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '/data/group/800080/warehouse/prod/INDEXWEIGHT/CHINA_STOCK/DAILY/CSI/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:57:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()
    
def get_csvdf(para):
    print(para)
    csvpath = os.path.join(rootpath, str(para[0]), para[1] + '.csv')
    if not os.path.exists(csvpath):
        return
    csvdf = pd.read_csv(csvpath, index_col=0)
    if 'close' in csvdf.columns.tolist():
        if csvdf['close'].sum() == 0:
            csvdf = csvdf.drop(['open','high','low','close'], axis = 1)
        if csvdf['volume'].sum() == 0:
            csvdf = csvdf.drop(['volume', 'amount'], axis = 1)

    csvdf.index = pd.DatetimeIndex(csvdf.index)
    if 'close' not in csvdf.columns.tolist():
        pickle_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'
        pdf = pd.read_pickle(os.path.join(pickle_path, 'UnAdjstedStockMinute_%s.pkl' % (para[1][:-3])), compression='gzip').reset_index(level = 1, drop = True).loc[para[0]].reset_index()
        pdf['dt'] = pdf.apply(lambda x:get_dt(x['dt'], x.minute), axis = 1)
        pdf = pdf.drop(['minute'], axis = 1).rename(columns = {'amt':'amount'}).set_index('dt')
        csvdf = csvdf.join(pdf, how = 'outer')

    csvdf = get_index_fromdate(para[0]).join(csvdf, how = 'left') 
    
    csv_columns = csvdf.columns.tolist()

    for k in ['open','high','low','close']:
        if k in csv_columns:
            csvdf[k] = csvdf[k].fillna(method = 'pad')
    for k in ['volume', 'amount','SellTradeMoney','SellTradeQuantity','SellTradeNum','SellUniqueOrderNum',
        'BuyTradeMoney','BuyTradeQuantity','BuyTradeNum','TradeBuyNo','Bid1AmtMean','Ask1AmtMean']:
        if k in csv_columns:
            csvdf[k] = csvdf[k].fillna(0)

    csvdf['Ticker'] = para[1]

    return csvdf   

def minute_flag_check(date):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_MINUTE.success'
    path2 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_INDEX_WEIGHT.success'
  
    return os.path.exists(path1) and os.path.exists(path2)
        
        
ticker = 'IM.CFE'
startdate, enddate = 20151228, 20201128

paralist = get_target_list(ticker,startdate,enddate)

rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_transaction_tominute_zz1000/'

#needlist = []
#for para in paralist:
#    date = para[0]
#    stock = para[1]
#    weight = round(para[2],5)
#    csvpath = os.path.join(rootpath, str(date))
#    filepath = os.path.join(csvpath, stock+'.csv')
#    if not os.path.exists(filepath):
#        needlist.append(para)

#print(len(paralist))    
#print(len(needlist))
for x in list(set([y[0] for y in paralist])):
    csvpath = os.path.join(rootpath, str(x))
    if not os.path.exists(csvpath):
        os.makedirs(csvpath)
        
# download data       
with Pool(processes = 24) as pool:
    pool.map(get_cfg_hfdata, paralist)
