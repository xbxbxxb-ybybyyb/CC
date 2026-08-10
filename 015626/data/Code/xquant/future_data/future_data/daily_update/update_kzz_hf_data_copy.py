from xquant.bonddata import BondData

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
    
def get_hfdata(para):
    bd = BondData()
    
    date = para[0]
    symbol = para[1]
    
    rootpath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/tick_transaction_to_minute/'
    csvpath = os.path.join(rootpath, str(date))
    filepath = os.path.join(csvpath, symbol+'.csv')
    if os.path.exists(filepath):
        return
        
    print(para)
    
    try:
        tick =  bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'TICK')
        tickdf = pd.DataFrame()
        if len(tick) > 100:
            if symbol.endswith('SH'):
                qty_columns = ['TotalVolumeTrade', 'TotalBidQty', 'TotalOfferQty', 'Buy1OrderQty', 'Sell1OrderQty', 'Buy2OrderQty', 'Sell2OrderQty', 'Buy3OrderQty', 'Sell3OrderQty', 'Buy4OrderQty', 'Sell4OrderQty', 'Buy5OrderQty', 'Sell5OrderQty', 'Buy6OrderQty', 'Sell6OrderQty', 'Buy7OrderQty', 'Sell7OrderQty', 'Buy8OrderQty', 'Sell8OrderQty', 'Buy9OrderQty', 'Sell9OrderQty', 'Buy10OrderQty', 'Sell10OrderQty']
                tick[qty_columns] *= 10
            tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            tick['minute'] = tick.dt.map(lambda x: x.replace(second=0))
            tick = tick.set_index('dt')
            tick['OBImbalance'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
            tick['OBImbalanceMean'] = tick['OBImbalance']
            tick['OBImbalanceStd'] = tick['OBImbalance']
            tick['OBImbalanceLast'] = tick['OBImbalance']

            tick.loc[tick['Buy1Price'] > tick['Buy1Price'].shift(), 'DeltaBuyQty'] = tick['Buy1OrderQty']
            tick.loc[tick['Buy1Price'] == tick['Buy1Price'].shift(), 'DeltaBuyQty'] = tick['Buy1OrderQty'] - tick['Buy1OrderQty'].shift()
            tick.loc[tick['Buy1Price'] < tick['Buy1Price'].shift(), 'DeltaBuyQty'] = -1 * tick['Buy1OrderQty'].shift()
            tick.loc[tick['Sell1Price'] > tick['Sell1Price'].shift(), 'DeltaSellQty'] = -1 * tick['Sell1OrderQty'].shift()
            tick.loc[tick['Sell1Price'] == tick['Sell1Price'].shift(), 'DeltaSellQty'] = tick['Sell1OrderQty'] - tick['Sell1OrderQty'].shift()
            tick.loc[tick['Sell1Price'] < tick['Sell1Price'].shift(), 'DeltaSellQty'] = tick['Sell1OrderQty']
            tick['OFImbalance'] = tick['DeltaBuyQty'] - tick['DeltaSellQty']
            obdict = {'OBImbalanceMean':'mean','OBImbalanceStd':'std','OBImbalanceLast':'last','OFImbalance':'sum'}
            
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

            df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1, **obdict})
            df1amt = df1amt.rename(columns = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'})

            # check price
            if df1amt.close.sum() > 0:    
                tickdf = df1amt.join(pvcorrdf)
                
            tickdf[['open','high','low','close']] = tickdf[['open','high','low','close']].replace(0, np.nan)
            tickdf[['volume','amount']] = tickdf[['volume','amount']].fillna(value = 0)
            tickdf = tickdf.replace([np.inf, -np.inf], np.nan)
        
        transaction = bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'TRANSACTION')
        transactiondf = pd.DataFrame()
        if len(transaction) > 100:
            if symbol.endswith('SH'):
                transaction['TradeQty'] *= 10
            transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            transaction['minute'] = transaction.dt.map(lambda x: x.replace(second=0,microsecond=0))
            
            cancel = transaction.copy()
            cselldf = cancel[cancel.TradeBSFlag == 2]
            cancelselldf = cselldf[cselldf.TradeType == 1]
            cancelselldf = cancelselldf.groupby('minute').agg({'TradeType':'count'}).rename(columns = {'TradeType':'sell_cancelorder_count'})
            cbuydf = cancel[cancel.TradeBSFlag == 1]
            cancelbuydf = cbuydf[cbuydf.TradeType == 1]
            cancelbuydf = cancelbuydf.groupby('minute').agg({'TradeType':'count'}).rename(columns = {'TradeType':'buy_cancelorder_count'})
            
            
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

            transactiondf = pd.concat([cancelselldf,cancelbuydf,selldf, buydf, sell_small_order, sell_mid_order, sell_big_order, sell_super_order, buy_small_order, buy_mid_order, buy_big_order, buy_super_order], axis = 1)
            
            transactiondf = transactiondf.fillna(value = 0)
            if symbol.endswith('SH'):
                transactiondf[['sell_cancelorder_count','buy_cancelorder_count']] = np.nan
                
        del(bd)        
        result = pd.concat([tickdf, transactiondf], axis = 1)
        if len(result) == 0:
            return
        result['Ticker'] = symbol
        result.index.name = 'dt'
        result.loc[:str(date) + ' 112900'].append(result.loc[str(date) + ' 130000':]).to_csv(filepath)
    except:
        del(bd)
        return
        
    
def get_target_list(cdate):
    bd = BondData()
    alist =  [[cdate, x] for x in bd.get_bond_set(str(cdate), 'kzz')]
    del(bd)
    return alist

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '15:00:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()
    
def get_csvdf(para):
    csvpath = os.path.join(rootpath, str(para[0]), para[1] + '.csv')
    if not os.path.exists(csvpath):
        return
    try:
        csvdf = pd.read_csv(csvpath, index_col=0)
    
        csvdf.index = pd.DatetimeIndex(csvdf.index)

        csvdf = get_index_fromdate(para[0]).join(csvdf, how = 'left') 
        
        csv_columns = csvdf.columns.tolist()

        for k in ['open','high','low','close']:
            csvdf[k] = csvdf[k].fillna(method = 'pad')
        res_columns = list(set(csv_columns) - set(['open','high','low','close','sell_cancelorder_count','buy_cancelorder_count']))
        for k in res_columns:
            if k in csv_columns:
                csvdf[k] = csvdf[k].fillna(0)
        csvdf['Ticker'] = para[1]
        return csvdf.reset_index().set_index(['dt','Ticker'])
    except Exception as e:
        print(para, e)
        return

if __name__ == '__main__':
    rootpath = '/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/tick_transaction_to_minute/'
    print('start')
    _,_,cdatelist = check_update_date()

    paralist_temp = []
    with Pool(processes = 24) as pool:
        paralist_temp = pool.map(get_target_list, cdatelist)
    paralist = paralist_temp[0]
    if len(paralist_temp) > 1:
        for i in range(1, len(paralist_temp)):
            paralist = paralist + paralist_temp[i]
    print(len(paralist), paralist[0], paralist[-1])

    for x in list(set([y[0] for y in paralist])):
        csvpath = os.path.join(rootpath, str(x))
        if not os.path.exists(csvpath):
            os.makedirs(csvpath)
            
    print('download data')     
    with Pool(processes = 24) as pool:
        pool.map(get_hfdata, paralist)
    
    print('get all csv to pkl')
    dflist = []
    with Pool(24) as pool:
        dflist = pool.map(get_csvdf, paralist)

    print('merge to pkl')
    df = pd.concat(dflist, axis = 0).sort_index()
    IO.pd_hdf5_writer(df, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_HF_TO_MINUTE.h5', dataset='CHINA_CONVERTIBLE_BOND_HF_TO_MINUTE', append=True)                
