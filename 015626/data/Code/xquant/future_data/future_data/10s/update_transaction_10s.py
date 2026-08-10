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
    
    rootpath = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction_to_10s/CSV/ZZ500/'
    csvpath = os.path.join(rootpath, str(date))
    if not os.path.exists(csvpath):
        os.makedirs(csvpath)
    filepath = os.path.join(csvpath, stock+'.csv')
    if os.path.exists(filepath):
        return
    transaction = mdp.get_data_by_date("Transaction", stock, str(date), ['3','5'])
    transactiondf = pd.DataFrame()
    if len(transaction) > 100:
        transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        transaction = transaction.set_index('dt')
        transaction['raw_flag'] = True

        index_list = pd.date_range(str(date)+'090000',str(date)+'150000', freq ='10S').tolist()
        index_df = pd.DataFrame(index_list, columns = ['dt'])
        index_df['seconds_10s'] = index_list
        index_df = index_df.set_index('dt')

        transaction = transaction.join(index_df, how = 'outer').sort_index()
        transaction['seconds_10s'] = transaction['seconds_10s'].fillna(method = 'ffill')
        transaction = transaction[transaction.raw_flag == True].reset_index()
    
        transaction = transaction[transaction.TradePrice != 0]
        transaction = transaction[transaction.TradeType != 1] # 去除撤单，深交所用
        
        transaction['open'] = transaction['TradePrice']
        transaction['high'] = transaction['TradePrice']
        transaction['low'] = transaction['TradePrice']
        transaction['close'] = transaction['TradePrice']
        transaction['volume'] = transaction['TradeQty']
        transaction['amount'] = transaction['TradeMoney']
        aggdict_ohlcva = {'open':'first','high':'max','low':'min','close':'last','volume':'sum','amount':'sum'}
        ohlcva = transaction.groupby('seconds_10s').agg(aggdict_ohlcva)
        
        selldf = transaction[transaction.TradeBSFlag == 2]
        sellorder_money = selldf.groupby(['seconds_10s', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order = sellorder_money[sellorder_money.TradeMoney <= 40000]
        sell_mid_order = sellorder_money[(sellorder_money.TradeMoney > 40000) & (sellorder_money.TradeMoney <= 200000)]
        sell_big_order = sellorder_money[(sellorder_money.TradeMoney > 200000) & (sellorder_money.TradeMoney <= 1000000)]
        sell_super_order = sellorder_money[(sellorder_money.TradeMoney > 1000000)]
        sell_small_order = sell_small_order.groupby('seconds_10s').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count','TradeMoney':'sell_smallorder_money','TradeQty':'sell_smallorder_volume'})
        sell_mid_order = sell_mid_order.groupby('seconds_10s').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count','TradeMoney':'sell_midorder_money','TradeQty':'sell_midorder_volume'})
        sell_big_order = sell_big_order.groupby('seconds_10s').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count','TradeMoney':'sell_bigorder_money','TradeQty':'sell_bigorder_volume'})
        sell_super_order = sell_super_order.groupby('seconds_10s').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count','TradeMoney':'sell_superorder_money','TradeQty':'sell_superorder_volume'})

        selldf = selldf.groupby('seconds_10s').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeSellNo':lambda x:len(x.unique())})
        selldf = selldf.rename(columns = {'TradeMoney':'SellTradeMoney','TradeQty':'SellTradeQuantity','TradePrice':'SellTradeNum','TradeSellNo':'SellUniqueOrderNum'})

        buydf = transaction[transaction.TradeBSFlag == 1]
        buyorder_money = buydf.groupby(['seconds_10s', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        buy_small_order = buyorder_money[buyorder_money.TradeMoney <= 40000]
        buy_mid_order = buyorder_money[(buyorder_money.TradeMoney > 40000) & (buyorder_money.TradeMoney <= 200000)]
        buy_big_order = buyorder_money[(buyorder_money.TradeMoney > 200000) & (buyorder_money.TradeMoney <= 1000000)]
        buy_super_order = buyorder_money[(buyorder_money.TradeMoney > 1000000)]
        buy_small_order = buy_small_order.groupby('seconds_10s').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_smallorder_count','TradeMoney':'buy_smallorder_money','TradeQty':'buy_smallorder_volume'})
        buy_mid_order = buy_mid_order.groupby('seconds_10s').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_midorder_count','TradeMoney':'buy_midorder_money','TradeQty':'buy_midorder_volume'})
        buy_big_order = buy_big_order.groupby('seconds_10s').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_bigorder_count','TradeMoney':'buy_bigorder_money','TradeQty':'buy_bigorder_volume'})
        buy_super_order = buy_super_order.groupby('seconds_10s').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'buy_superorder_count','TradeMoney':'buy_superorder_money','TradeQty':'buy_superorder_volume'})

        buydf = buydf.groupby('seconds_10s').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeBuyNo':lambda x:len(x.unique())})
        buydf = buydf.rename(columns = {'TradeMoney':'BuyTradeMoney','TradeQty':'BuyTradeQuantity','TradePrice':'BuyTradeNum','TradeBuyNo':'BuyUniqueOrderNum'})

        transactiondf = pd.concat([ohlcva, selldf, buydf, sell_small_order, sell_mid_order, sell_big_order, sell_super_order, buy_small_order, buy_mid_order, buy_big_order, buy_super_order], axis = 1)
    
    del(mdp)        
    result = transactiondf
    if len(result) == 0:
        return
    result['weight'] = weight
    result.loc[str(date)+'093000':str(date)+'113000'].append(result.loc[str(date)+'130000':str(date)+'150000']).to_csv(filepath)
    

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
    t_mins_list = pd.date_range('09:30:00', '11:29:50', freq='10S').to_list() + pd.date_range('13:00:00','14:56:50',freq='10S').to_list()
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
    try:
        csvdf = pd.read_csv(csvpath, index_col=0)
    except:
        return

    csvdf = get_index_fromdate(para[0]).join(csvdf, how = 'left') 
    
    csv_columns = csvdf.columns.tolist()

    for k in ['open','high','low','close']:
        if k in csv_columns:
            csvdf[k] = csvdf[k].replace(0,np.nan).fillna(method = 'pad')
    res_columns = list(set(csv_columns) - set(['open','high','low','close']))
    for k in res_columns:
        if k in csv_columns:
            csvdf[k] = csvdf[k].fillna(0)

    csvdf['Ticker'] = para[1]
    csvdf['weight'] = round(para[2], 5)
    return csvdf

                        
for ticker in ['IC.CFE']:
    rootpath = '/arch0/group/800466/warehouse/prod/MD/CHINA_STOCK/Transaction_to_10s/CSV/ZZ500/'

    paralist = get_target_list(ticker,20190331,20210101)


    for x in list(set([y[0] for y in paralist])):
        csvpath = os.path.join(rootpath, str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
            
    # download data       
    with Pool(processes = 24) as pool:
        pool.map(get_cfg_hfdata, paralist)

    dflist = []
    with Pool(24) as pool:
        dflist = pool.map(get_csvdf, paralist)
#    for para in paralist:
#        dflist.append(get_csvdf(para))

    print('csv done!')
    dfnew = pd.concat(dflist, axis = 0)
    print('concat done!')
    dfnew = dfnew.reset_index().set_index(['dt','Ticker']).sort_index()
    print('sort done!')
    dfnew.to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/10s/zz500_cfg_10s_20190401_20210101.pkl')
    
    insample = dfnew.unstack()
    for col in insample.columns.get_level_values(0).unique():
        insample[col].to_pickle('/data/user/015626/data/share/MD/CHINA_FUTURES/10s/INSAMPLE/ZZ500/%s.pkl'%col)



