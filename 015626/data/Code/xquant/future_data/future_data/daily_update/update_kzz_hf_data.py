from xquant.bonddata import BondData

import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os, re
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
    
def aggregate_transaction(transaction):
    transactiondf = pd.DataFrame()
    if len(transaction) > 100:
        transaction.loc[transaction.TradeBSFlag == 1, 'ot_market_index'] = transaction['TradeBuyNo']
        transaction.loc[transaction.TradeBSFlag == 2, 'ot_market_index'] = transaction['TradeSellNo']

        transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        transaction['minute'] = transaction.dt.map(lambda x: x.replace(second=0,microsecond=0))
        transaction = transaction[transaction.TradePrice != 0]
        transaction = transaction[transaction.TradeType != 1] # 去除撤单，深交所用
        
        tran_count_info = transaction.groupby('minute').agg({'TradePrice':'count','TradeBuyNo':lambda x:len(x.unique()),'TradeSellNo':lambda x:len(x.unique())})
        tran_count_info.columns = ['tran_count','tran_buy_unique_order_count','tran_sell_unique_order_count']
        
        allsell_order_money = transaction.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
        allsell_small_order = allsell_order_money[allsell_order_money.TradeMoney <= 40000]
        allsell_mid_order = allsell_order_money[(allsell_order_money.TradeMoney > 40000) & (allsell_order_money.TradeMoney <= 200000)]
        allsell_big_order = allsell_order_money[(allsell_order_money.TradeMoney > 200000) & (allsell_order_money.TradeMoney <= 1000000)]
        allsell_super_order = allsell_order_money[(allsell_order_money.TradeMoney > 1000000)]
        allsell_small_order = allsell_small_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_smallorder_count','TradeMoney':'allsell_smallorder_money','TradeQty':'allsell_smallorder_volume'})
        allsell_mid_order = allsell_mid_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_midorder_count','TradeMoney':'allsell_midorder_money','TradeQty':'allsell_midorder_volume'})
        allsell_big_order = allsell_big_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_bigorder_count','TradeMoney':'allsell_bigorder_money','TradeQty':'allsell_bigorder_volume'})
        allsell_super_order = allsell_super_order.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'allsell_superorder_count','TradeMoney':'allsell_superorder_money','TradeQty':'allsell_superorder_volume'})

        allbuy_order_money = transaction.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        allbuy_small_order = allbuy_order_money[allbuy_order_money.TradeMoney <= 40000]
        allbuy_mid_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 40000) & (allbuy_order_money.TradeMoney <= 200000)]
        allbuy_big_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 200000) & (allbuy_order_money.TradeMoney <= 1000000)]
        allbuy_super_order = allbuy_order_money[(allbuy_order_money.TradeMoney > 1000000)]
        allbuy_small_order = allbuy_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_smallorder_count','TradeMoney':'allbuy_smallorder_money','TradeQty':'allbuy_smallorder_volume'})
        allbuy_mid_order = allbuy_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_midorder_count','TradeMoney':'allbuy_midorder_money','TradeQty':'allbuy_midorder_volume'})
        allbuy_big_order = allbuy_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_bigorder_count','TradeMoney':'allbuy_bigorder_money','TradeQty':'allbuy_bigorder_volume'})
        allbuy_super_order = allbuy_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'allbuy_superorder_count','TradeMoney':'allbuy_superorder_money','TradeQty':'allbuy_superorder_volume'})

        selldf = transaction[transaction.TradeBSFlag == 2]
        sellorder_money_v2 = selldf.groupby(['minute', 'TradeSellNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order_v2 = sellorder_money_v2[sellorder_money_v2.TradeMoney <= 40000]
        sell_mid_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 40000) & (sellorder_money_v2.TradeMoney <= 200000)]
        sell_big_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 200000) & (sellorder_money_v2.TradeMoney <= 1000000)]
        sell_super_order_v2 = sellorder_money_v2[(sellorder_money_v2.TradeMoney > 1000000)]
        sell_small_order_v2 = sell_small_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_smallorder_count_v2','TradeMoney':'sell_smallorder_money_v2','TradeQty':'sell_smallorder_volume_v2'})
        sell_mid_order_v2 = sell_mid_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_midorder_count_v2','TradeMoney':'sell_midorder_money_v2','TradeQty':'sell_midorder_volume_v2'})
        sell_big_order_v2 = sell_big_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_bigorder_count_v2','TradeMoney':'sell_bigorder_money_v2','TradeQty':'sell_bigorder_volume_v2'})
        sell_super_order_v2 = sell_super_order_v2.groupby('minute').agg({'TradeSellNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeSellNo':'sell_superorder_count_v2','TradeMoney':'sell_superorder_money_v2','TradeQty':'sell_superorder_volume_v2'})

        sellorder_money = selldf.groupby(['minute', 'TradeBuyNo'])['TradeMoney','TradeQty'].sum().reset_index()
        sell_small_order = sellorder_money[sellorder_money.TradeMoney <= 40000]
        sell_mid_order = sellorder_money[(sellorder_money.TradeMoney > 40000) & (sellorder_money.TradeMoney <= 200000)]
        sell_big_order = sellorder_money[(sellorder_money.TradeMoney > 200000) & (sellorder_money.TradeMoney <= 1000000)]
        sell_super_order = sellorder_money[(sellorder_money.TradeMoney > 1000000)]
        sell_small_order = sell_small_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_smallorder_count','TradeMoney':'sell_smallorder_money','TradeQty':'sell_smallorder_volume'})
        sell_mid_order = sell_mid_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_midorder_count','TradeMoney':'sell_midorder_money','TradeQty':'sell_midorder_volume'})
        sell_big_order = sell_big_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_bigorder_count','TradeMoney':'sell_bigorder_money','TradeQty':'sell_bigorder_volume'})
        sell_super_order = sell_super_order.groupby('minute').agg({'TradeBuyNo':'count', 'TradeMoney':'sum', 'TradeQty':'sum'}).rename(columns = {'TradeBuyNo':'sell_superorder_count','TradeMoney':'sell_superorder_money','TradeQty':'sell_superorder_volume'})

        selldfgroup = selldf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeSellNo':lambda x:len(x.unique())})
        selldfgroup = selldfgroup.rename(columns = {'TradeMoney':'SellTradeMoney','TradeQty':'SellTradeQuantity','TradePrice':'SellTradeNum','TradeSellNo':'SellUniqueOrderNum'})

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


        buydfgroup = buydf.groupby('minute').agg({'TradeMoney':'sum','TradeQty':'sum','TradePrice':'count','TradeBuyNo':lambda x:len(x.unique())})
        buydfgroup = buydfgroup.rename(columns = {'TradeMoney':'BuyTradeMoney','TradeQty':'BuyTradeQuantity','TradePrice':'BuyTradeNum','TradeBuyNo':'BuyUniqueOrderNum'})

        rlist = []
        for x in [transaction, selldf, buydf]:
            temp = x.groupby(['minute','ot_market_index'])['TradePrice'].count() # 主动成交单吃掉了多少单挂单
            temp = temp.groupby('minute').mean()
            rlist.append(temp)
        market_map_limit_num = pd.concat(rlist, axis = 1)
        market_map_limit_num.columns = ['market_map_limit_num','sell_market_map_limit_num','buy_market_map_limit_num']

        transaction['price_diff'] = transaction.TradePrice.diff()
        transaction['price_ret'] = transaction.TradePrice.pct_change()
        transaction['abs_price_diff'] = abs(transaction['price_diff'])
        transaction['TradeMoney_direction'] = np.sign(transaction['price_diff']) * transaction['TradeMoney']
        transaction['TradeMoney_ret_weighted'] = transaction['price_ret'] * transaction['TradeMoney']
        tran1 = transaction.groupby('minute')['abs_price_diff','TradeMoney_direction','TradeMoney_ret_weighted'].sum()
        tran1.columns = ['abs_px_path_tran','trademoney_ret_sign_sum','trademoney_ret_weighted']

        max_volume_price = transaction.groupby(['minute','TradePrice','TradeBSFlag'])['TradeQty'].sum()
        rlist = []
        level2_index_list = max_volume_price.index.get_level_values(2).unique().tolist()
        for i in [1,2]:
            if i in level2_index_list:
                select_level = max_volume_price.xs(i, level = 2)
                select_max_volume_price = select_level.loc[select_level.groupby('minute').idxmax()].reset_index(level = 1)#[['TradePrice']]
            else:
                select_max_volume_price = pd.DataFrame(columns = ['TradePrice', 'TradeQty'])
            rlist.append(select_max_volume_price)
        select_alllevel = max_volume_price.groupby(['minute','TradePrice']).sum()
        select_alllevel_max_volume_price = select_alllevel.loc[select_alllevel.groupby('minute').idxmax()].reset_index(level = 1)#[['TradePrice']]
        rlist.append(select_alllevel_max_volume_price)
        tran2 = pd.concat(rlist, axis = 1)
        tran2.columns = ['buy_maxvol_price','buy_maxvol_price_vol','sell_maxvol_price','sell_maxvol_price_vol','maxvol_price','maxvol_price_vol']

        transactiondf = pd.concat([selldfgroup, buydfgroup, sell_small_order, sell_mid_order, sell_big_order, 
                        sell_super_order,sell_small_order_v2, sell_mid_order_v2, sell_big_order_v2, sell_super_order_v2, 
                        buy_small_order, buy_mid_order, buy_big_order, buy_super_order, market_map_limit_num, tran1, tran2,
                        allsell_small_order,allsell_mid_order,allsell_big_order,allsell_super_order,allbuy_small_order,
                        allbuy_mid_order,allbuy_big_order,allbuy_super_order,tran_count_info], axis = 1)
    return transactiondf

def aggregate_tick(tick):
    fill_na_columns = ['LastPx','Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price']
    tickdf = pd.DataFrame()
    if len(tick) > 100:
        tick[fill_na_columns] =  tick[fill_na_columns].replace(0,np.nan)
    
        tick['dt'] = tick.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
        tick['minute'] = tick.dt.map(lambda x: x.replace(second=0))
        tick = tick.set_index('dt')
        tick['LastPx'] = tick['LastPx'].replace(0, np.nan)
        tick['OBI'] = (tick['Buy1OrderQty'] - tick['Sell1OrderQty']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty'])
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
            
        tick['BidVolMean'] = (tick[['Buy{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
            [0.8 ** i for i in range(10)])).sum(axis=1)
        tick['AskVolMean'] = (tick[['Sell{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
            [0.8 ** i for i in range(10)])).sum(axis=1)
        
        aggdict1 = {'AskVolMean':'mean','BidVolMean':'mean','BuyNumOrdersSumMean':'mean','SellNumOrdersSumMean':'mean','BuyOrderQtySumMean':'mean','SellOrderQtySumMean':'mean','WeightBuyOrderQtySumMean':'mean','WeightSellOrderQtySumMean':'mean','OBI':'mean'}

        tick['open'] = tick['LastPx']
        tick['high'] = tick['LastPx']
        tick['low'] = tick['LastPx']
        tick['close'] = tick['LastPx']
        tick['twap'] = tick['LastPx']
        aggdict_ohlc = {'open':'first','high':'max','low':'min','close':'last','twap':'mean'}

        pvcorrdf = tick[['minute','LastPx','volume']].groupby('minute').corr().xs('LastPx', level = 1)[['volume']]
        pvcorrdf.columns = ['PxVolCorr']
        aggdict = {'Buy1NumOrders':'mean','Sell1NumOrders':'mean','BidAskSpreadMean':'mean','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std'}
        
        aggdict2 = {'TotalValueTrade':'last','TotalVolumeTrade':'last','TotalOfferQty':'last','TotalBidQty':'last','Buy1Price':'last','Buy1OrderQty':'last', 'Sell1Price':'last','Sell1OrderQty':'last','Buy2Price':'last','Buy2OrderQty':'last', 'Sell2Price':'last','Sell2OrderQty':'last',
                   'Buy3Price':'last','Buy3OrderQty':'last', 'Sell3Price':'last','Sell3OrderQty':'last','Buy4Price':'last','Buy4OrderQty':'last', 'Sell4Price':'last','Sell4OrderQty':'last',
                   'Buy5Price':'last','Buy5OrderQty':'last', 'Sell5Price':'last','Sell5OrderQty':'last'}
        
        df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1, **aggdict2})
        
        renamedict1 = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'}
        
        renamedict2 = {'TotalOfferQty':'TotalAskVol','TotalBidQty':'TotalBidVol','Buy1Price':'BidP0','Buy1OrderQty':'BidV0', 'Sell1Price':'AskP0','Sell1OrderQty':'AskV0','Buy2Price':'BidP1','Buy2OrderQty':'BidV1', 'Sell2Price':'AskP1','Sell2OrderQty':'AskV1',
                   'Buy3Price':'BidP2','Buy3OrderQty':'BidV2', 'Sell3Price':'AskP2','Sell3OrderQty':'AskV2','Buy4Price':'BidP3','Buy4OrderQty':'BidV3', 'Sell4Price':'AskP3','Sell4OrderQty':'AskV3',
                   'Buy5Price':'BidP4','Buy5OrderQty':'BidV4', 'Sell5Price':'AskP4','Sell5OrderQty':'AskV4'}
        df1amt = df1amt.rename(columns = {**renamedict1, **renamedict2})
        
        tick['WeightBuyNumOrdersSumMean'] = 0
        tick['WeightSellNumOrdersSumMean'] = 0
        tick['WeightBuyMoneySumMean'] = 0
        tick['WeightSellMoneySumMean'] = 0
        for i in range(1,11):
            tick['WeightBuyNumOrdersSumMean'] += tick['Buy'+str(i)+'NumOrders'] * 0.8 ** (i-1)
            tick['WeightSellNumOrdersSumMean'] += tick['Sell'+str(i)+'NumOrders'] * 0.8 ** (i-1)
            tick['WeightBuyMoneySumMean'] += tick['Buy'+str(i)+'Price'] * tick['Buy'+str(i)+'OrderQty'] * 0.8 ** (i-1)
            tick['WeightSellMoneySumMean'] += tick['Sell'+str(i)+'Price'] * tick['Sell'+str(i)+'OrderQty'] * 0.8 ** (i-1)

        agg_dict_v3 = {'TotalBidQty':'last', 'TotalOfferQty':'last', 'WeightedAvgBidPx':'last', 'WeightedAvgOfferPx':'last',
                    'WeightBuyNumOrdersSumMean':'mean', 'WeightSellNumOrdersSumMean':'mean','WeightBuyMoneySumMean':'mean','WeightSellMoneySumMean':'mean',
                   'Buy1Price':'mean','Buy1OrderQty':'mean','Buy1NumOrders':'mean','Sell1Price':'mean','Sell1OrderQty':'mean','Sell1NumOrders':'mean'}

        tickv3 = tick.resample('1min').agg(agg_dict_v3).rename(columns = {x:f'{x}_mean' for x in ['Buy1Price','Buy1OrderQty','Buy1NumOrders','Sell1Price','Sell1OrderQty','Sell1NumOrders']})
        
        # amtOBI
        for x in ['BuyOrderAmt_5','BuyOrderAmt_5_linear','BuyOrderAmt_5_exp','BuyOrderQty_5_exp','BuyOrderAmt_10','BuyOrderAmt_10_linear','BuyOrderAmt_10_exp','BuyOrderQty_10_exp',
                 'SellOrderAmt_5','SellOrderAmt_5_linear','SellOrderAmt_5_exp','SellOrderQty_5_exp','SellOrderAmt_10','SellOrderAmt_10_linear','SellOrderAmt_10_exp','SellOrderQty_10_exp',
                 'BuyOrderQty_5','BuyOrderQty_10','SellOrderQty_5','SellOrderQty_10']:
            tick[x] = 0

        for i in range(1,11):
            for kind in ['Buy', 'Sell']:
                tick[f'{kind}{i}OrderAmt'] = (tick[f'{kind}{i}Price'] * tick[f'{kind}{i}OrderQty']).fillna(0)
                tick[f'{kind}OrderAmt_10'] += tick[f'{kind}{i}OrderAmt']
                tick[f'{kind}OrderQty_10'] += tick[f'{kind}{i}OrderQty']
                tick[f'{kind}OrderAmt_10_linear'] += tick[f'{kind}{i}OrderAmt'] * (11-i) / 10
                tick[f'{kind}OrderAmt_10_exp'] += tick[f'{kind}{i}OrderAmt'] * 0.8 ** (i-1)
                tick[f'{kind}OrderQty_10_exp'] += tick[f'{kind}{i}OrderQty'] * 0.8 ** (i-1)
                if i < 6:
                    tick[f'{kind}OrderAmt_5'] += tick[f'{kind}{i}OrderAmt']
                    tick[f'{kind}OrderQty_5'] += tick[f'{kind}{i}OrderQty']
                    tick[f'{kind}OrderAmt_5_linear'] += tick[f'{kind}{i}OrderAmt'] * (11-i) / 10
                    tick[f'{kind}OrderAmt_5_exp'] += tick[f'{kind}{i}OrderAmt'] * 0.8 ** (i-1)
                    tick[f'{kind}OrderQty_5_exp'] += tick[f'{kind}{i}OrderQty'] * 0.8 ** (i-1)

        tick['BuyOrderAmt_total'] = (tick['TotalBidQty'] * tick['WeightedAvgBidPx']).fillna(0)
        tick['SellOrderAmt_total'] = (tick['TotalOfferQty'] * tick['WeightedAvgOfferPx']).fillna(0)
        tick['amtOBI_total'] = (tick['BuyOrderAmt_total'] - tick['SellOrderAmt_total']) / (tick['BuyOrderAmt_total'] + tick['SellOrderAmt_total']).replace(0, np.nan)

        tick['amtOBI_1'] = (tick['Buy1OrderAmt'] - tick['Sell1OrderAmt']) / (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']).replace(0, np.nan)
        for i in [5,10]:
            tick[f'amtOBI_{i}'] = (tick[f'BuyOrderAmt_{i}'] - tick[f'SellOrderAmt_{i}']) / (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']).replace(0, np.nan)
            for kind in ['linear','exp']:
                tick[f'amtOBI_{i}_{kind}'] = (tick[f'BuyOrderAmt_{i}_{kind}'] - tick[f'SellOrderAmt_{i}_{kind}']) / (tick[f'BuyOrderAmt_{i}_{kind}'] + tick[f'SellOrderAmt_{i}_{kind}']).replace(0, np.nan)

        amtOBI_list = ['BuyOrderAmt_total', 'SellOrderAmt_total', 'amtOBI_total', 'BuyOrderAmt_5', 'BuyOrderAmt_5_linear', 'BuyOrderAmt_5_exp', 'BuyOrderAmt_10', 'BuyOrderAmt_10_linear', 'BuyOrderAmt_10_exp','SellOrderAmt_5', 'SellOrderAmt_5_linear', 'SellOrderAmt_5_exp',  'SellOrderAmt_10', 'SellOrderAmt_10_linear', 'SellOrderAmt_10_exp',  'amtOBI_1', 'amtOBI_5', 'amtOBI_5_linear', 'amtOBI_5_exp', 'amtOBI_10', 'amtOBI_10_linear', 'amtOBI_10_exp']
        amtOBI_dict = {x:'mean' for x in amtOBI_list}

        # amount 相关
        tick.loc[tick['LastPx'].pct_change() > 0, 'tickup_amount'] = tick['amount']
        tick['orderamt1_amount_ratio'] = (tick['Buy1OrderAmt'] - tick['Sell1OrderAmt']) / tick['amount'].replace(0, np.nan)
        for i in [5, 10]:
            tick[f'orderamt{i}_amount_ratio'] = (tick[f'BuyOrderAmt_{i}'] - tick[f'SellOrderAmt_{i}']) / tick['amount'].replace(0, np.nan)
            tick[f'BSOrderAmt_{i}_to_amount'] = (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']) / tick['amount'].replace(0, np.nan)
        tick['BSOrderAmt_1_to_amount'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / tick['amount'].replace(0, np.nan)

        amount_dict = {'BSOrderAmt_1_to_amount':'mean','BSOrderAmt_5_to_amount':'mean','BSOrderAmt_10_to_amount':'mean','tickup_amount':'sum', 'orderamt1_amount_ratio':'mean', 'orderamt5_amount_ratio':'mean', 'orderamt10_amount_ratio':'mean'}

        # bid ask spread
        tick['mid_price'] = tick[['Buy1Price', 'Sell1Price']].mean(axis = 1)
        # tick['mid_price'] = tick['mid_price'].fillna(value = tick[['Buy1Price','Sell1Price']].fillna(0).max(axis = 1))

        tick['bas'] = tick['Sell1Price'] - tick['Buy1Price']
        tick['bas_ratio'] = tick['bas'] / tick['mid_price']

        for i in range(1, 11):
            tick[f's1bndiff_{i}'] = tick['Sell1Price'] - tick[f'Buy{i}Price'] 
            tick[f'snb1diff_{i}'] = tick[f'Sell{i}Price'] - tick['Buy1Price']
            tick[f'snmiddiff_{i}'] = tick[f'Sell{i}Price'] - tick['mid_price']
            tick[f'bnmiddiff_{i}'] = tick['mid_price'] - tick[f'Buy{i}Price']
            tick[f'Amtmul_snmiddiff_{i}'] = tick[f'snmiddiff_{i}'] * tick[f'Sell{i}OrderAmt']
            tick[f'Amtmul_bnmiddiff_{i}'] = tick[f'bnmiddiff_{i}'] * tick[f'Buy{i}OrderAmt']

        for i in [5, 10]:
            for kind in ['Buy', 'Sell']:
                tick[f'{kind}OrderWeightedPx_{i}'] = tick[f'{kind}OrderAmt_{i}'] / tick[f'{kind}OrderQty_{i}'].replace(0, np.nan)
            tick[f'bas_bas{i}'] = tick['bas'] / (tick[f'Sell{i}Price'] - tick[f'Buy{i}Price']).replace(0, np.nan)
            tick[f'bas_WeightedPxbas{i}'] = tick['bas'] / (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']).replace(0, np.nan)
            tick[f'cumbas_{i}'] = tick[[f's1bndiff_{j + 1}' for j in range(i)]].sum(axis = 1) / tick[[f'snb1diff_{j + 1}' for j in range(i)]].sum(axis = 1).replace(0, np.nan)
            tick[f'bas_midpx_WeightedPxbas{i}'] = (tick[f'SellOrderWeightedPx_{i}'] - tick['mid_price']) / (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']).replace(0, np.nan)
            tick[f'SBWeightedPx_{i}_to_midprice'] = (tick[f'SellOrderWeightedPx_{i}'] - tick[f'BuyOrderWeightedPx_{i}']) / tick['mid_price']
            tick[f'SWeightedPx_{i}_minusS1_to_midprice'] = (tick[f'SellOrderWeightedPx_{i}'] - tick['Sell1Price']) / tick['mid_price']
            tick[f'B1minus_BWeightedPx_{i}_to_midprice'] = (tick['Buy1Price'] - tick[f'BuyOrderWeightedPx_{i}']) / tick['mid_price']


        bas_list = ['B1minus_BWeightedPx_5_to_midprice','B1minus_BWeightedPx_10_to_midprice','SWeightedPx_5_minusS1_to_midprice','SWeightedPx_10_minusS1_to_midprice','SBWeightedPx_5_to_midprice','SBWeightedPx_10_to_midprice','mid_price', 'bas_ratio', 'BuyOrderWeightedPx_5', 'SellOrderWeightedPx_5', 'bas_bas5', 'bas_WeightedPxbas5', 'cumbas_5', 'bas_midpx_WeightedPxbas5', 'BuyOrderWeightedPx_10', 'SellOrderWeightedPx_10', 'bas_bas10', 'bas_WeightedPxbas10', 'cumbas_10', 'bas_midpx_WeightedPxbas10']
        bas_dict = {x:'mean' for x in bas_list}

        # vwap
        tick['tick_vwap'] = tick['amount'] / tick['volume'].replace(0, np.nan)
        tick['vwap_midprice'] = tick['tick_vwap'] / tick['mid_price']
        tick['vwapmid_lastpx'] = (tick['tick_vwap'] - tick['mid_price']) / tick['LastPx']
        tick['vwap_std'] = tick['tick_vwap']
        tick['vwap_ret_std'] = tick['tick_vwap'].pct_change()
        vwap_dict = {'tick_vwap':'mean', 'vwap_midprice':'mean', 'vwapmid_lastpx':'mean', 'vwap_std':'std', 'vwap_ret_std':'std'}

        # 15s的一些东西
        tickdata15s = tick.resample('15S').agg({'amount':'sum','volume':'sum','LastPx':'first'})
        tickdata15s = tickdata15s.loc[tickdata15s.index.second == 45].reset_index()
        tickdata15s['dt'] = tickdata15s.dt.map(lambda x:x.replace(second = 0))

        tickdata15s = tickdata15s.set_index('dt').add_suffix('_last15s')
        tickdata15s['vwap_last15s'] = tickdata15s['amount_last15s'] / tickdata15s['volume_last15s'].replace(0, np.nan)

        # cc系列
        tick['bas_std'] = tick['bas']
        tick['bid_ask_dis_ratio'] = (tick[[f'Sell{j}Price' for j in range(1,11)]].max(axis = 1) - tick['Sell1Price']) / (tick['Buy1Price'] - tick[[f'Buy{j}Price' for j in range(1,11)]].min(axis = 1)).replace(0, np.nan)
        tick['buy_amt_middiff_weighted'] = tick[[f'Amtmul_bnmiddiff_{i}' for j in range(1,11)]].sum(axis = 1) / tick[[f'bnmiddiff_{i}' for j in range(1,11)]].sum(axis = 1).replace(0, np.nan)
        tick['sell_amt_middiff_weighted'] = tick[[f'Amtmul_snmiddiff_{i}' for j in range(1,11)]].sum(axis = 1) / tick[[f'snmiddiff_{i}' for j in range(1,11)]].sum(axis = 1).replace(0, np.nan)
        tick['bs1_amt_mean'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / 2
        tick['bs1_amt_min'] = tick[['Buy1OrderAmt', 'Sell1OrderAmt']].min(axis = 1)
        tick['amt_b1_ball'] = tick['Buy1OrderAmt'] / tick['BuyOrderAmt_10'].replace(0, np.nan)
        tick['amt_s1_sall'] = tick['Sell1OrderAmt'] / tick['SellOrderAmt_10'].replace(0, np.nan)
        tick['amt_b1_bexpall'] = tick['Buy1OrderAmt'] / tick['BuyOrderAmt_10_exp'].replace(0, np.nan)
        tick['amt_s1_sexpall'] = tick['Sell1OrderAmt'] / tick['SellOrderAmt_10_exp'].replace(0, np.nan)

        tick['amt_b1_s1'] = tick['Buy1OrderAmt'] / tick['Sell1OrderAmt'].replace(0, np.nan)
        tick['amt_bexpall_sexpall'] = tick['BuyOrderAmt_10_exp'] / tick['SellOrderAmt_10_exp'].replace(0, np.nan)
        tick['weighted_mid1'] = (tick['Buy1OrderAmt'] + tick['Sell1OrderAmt']) / (tick['Buy1OrderQty'] + tick['Sell1OrderQty']).replace(0, np.nan)
        for i in [5, 10]:
            tick[f'weighted_mid{i}'] = (tick[f'BuyOrderAmt_{i}'] + tick[f'SellOrderAmt_{i}']) / (tick[f'BuyOrderQty_{i}'] + tick[f'SellOrderQty_{i}']).replace(0, np.nan)
            tick[f'mid_weighted_mid{i}'] = tick['mid_price'] / tick[f'weighted_mid{i}']
            tick[f'expweighted_mid{i}'] = (tick[f'BuyOrderAmt_{i}_exp'] + tick[f'SellOrderAmt_{i}_exp']) / (tick[f'BuyOrderQty_{i}_exp'] + tick[f'SellOrderQty_{i}_exp']).replace(0, np.nan)
            tick[f'mid_expweighted_mid{i}'] = tick['mid_price'] / tick[f'expweighted_mid{i}']

        for kind in ['Buy', 'Sell']:
            # 先找出盘口买量或者卖量最高的价格
            amt_sell = tick[[f'{kind}{j}OrderAmt' for j in range(1,11)]]
            price_sell = tick[[f'{kind}{j}Price' for j in range(1,11)]]
            scols_name = [f'{kind}{j}Order' for j in range(1,11)]
            amtcols_name = [f'{kind}{j}OrderAmt' for j in range(1,11)]

            mask_sell = amt_sell.idxmax(axis = 1)
            # 哪档盘口挂单金额最大
            tick[f'idxmax_{str.lower(kind)}amt'] = mask_sell.apply(lambda x: re.sub("\D", "", x)).astype('int')
            mask_sell = mask_sell.reset_index()
            mask_sell.columns = ['dt','maxcol_name']
            mask_sell['mask'] = True
            mask_sell = mask_sell.set_index(['dt','maxcol_name']).unstack()['mask']
            res_cols = list(set(amtcols_name) - set(mask_sell.columns))
            if len(res_cols) > 0:
                for res_col in res_cols:
                    mask_sell[res_col] = np.nan
            mask_sell = mask_sell[amtcols_name].fillna(False)
            mask_sell.columns = scols_name
            price_sell.columns = scols_name
            amt_sell.columns = scols_name

            tick[f'max_{str.lower(kind)}amt_price'] = price_sell[mask_sell].mean(axis = 1)
            tick[f'max_{str.lower(kind)}amt_price_mid'] = tick[f'max_{str.lower(kind)}amt_price'] / tick['mid_price']
            # 第一档盘口卖量最高价格之间的所有挂单量之和
            mask_sell = mask_sell.replace(False, np.nan).fillna(axis = 1, method = 'bfill').fillna(0).astype('bool')
            tick[f'{str.lower(kind)}_amtsum_1tomax'] = amt_sell[mask_sell].sum(axis = 1)

        cc_list = ['bid_ask_dis_ratio', 'buy_amt_middiff_weighted', 'sell_amt_middiff_weighted', 'bs1_amt_mean', 'bs1_amt_min', 'amt_b1_ball', 'amt_s1_sall', 'amt_b1_bexpall', 'amt_s1_sexpall', 'amt_b1_s1', 'amt_bexpall_sexpall', 'weighted_mid1', 'weighted_mid5', 'mid_weighted_mid5', 'expweighted_mid5', 'mid_expweighted_mid5', 'weighted_mid10', 'mid_weighted_mid10', 'expweighted_mid10', 'mid_expweighted_mid10', 'idxmax_buyamt', 'max_buyamt_price', 'max_buyamt_price_mid', 'buy_amtsum_1tomax', 'idxmax_sellamt', 'max_sellamt_price', 'max_sellamt_price_mid', 'sell_amtsum_1tomax']
        cc_dict = {'bas_std':'std'}
        cc_dict.update({x:'mean' for x in cc_list})

        agg_dict_v4 = {**amtOBI_dict,**amount_dict,**bas_dict,**vwap_dict,**cc_dict}
        tickv4 = tick.resample('1min').agg(agg_dict_v4).join(tickdata15s)
        
        # check price
        if df1amt.close.sum() > 0:    
            tickdf = df1amt.join(pvcorrdf).join(tickv3).join(tickv4)
    return tickdf

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
        if symbol.endswith('SH'):
            qty_columns = ['TotalVolumeTrade', 'TotalBidQty', 'TotalOfferQty', 'Buy1OrderQty', 'Sell1OrderQty', 'Buy2OrderQty', 'Sell2OrderQty', 'Buy3OrderQty', 'Sell3OrderQty', 'Buy4OrderQty', 'Sell4OrderQty', 'Buy5OrderQty', 'Sell5OrderQty', 'Buy6OrderQty', 'Sell6OrderQty', 'Buy7OrderQty', 'Sell7OrderQty', 'Buy8OrderQty', 'Sell8OrderQty', 'Buy9OrderQty', 'Sell9OrderQty', 'Buy10OrderQty', 'Sell10OrderQty']
            tick[qty_columns] *= 10
        tickdf = aggregate_tick(tick)
        
        transaction = bd.get_bond_data(symbol, "%s 090000000" % str(date), "%s 150000000" % str(date), 'TRANSACTION')
        if symbol.endswith('SH'):
            transaction['TradeQty'] *= 10
        transactiondf = aggregate_transaction(transaction)
        
        del(bd)        
        result = pd.concat([tickdf, transactiondf], axis = 1)
        if len(result) == 0:
            return
        result['Ticker'] = symbol
        result.index.name = 'dt'
        result.loc[:str(date) + ' 112900'].append(result.loc[str(date) + ' 130000':]).to_csv(filepath)
    except Exception as e:
        print(para, e)
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
    _,_,cdatelist = check_update_date(20200101, 20240918)

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
    
#    print('get all csv to pkl')
#    dflist = []
#    with Pool(24) as pool:
#        dflist = pool.map(get_csvdf, paralist)

#    print('merge to pkl')
#    df = pd.concat(dflist, axis = 0).sort_index()
#    IO.pd_hdf5_writer(df, '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_HF_TO_MINUTE.h5', dataset='CHINA_CONVERTIBLE_BOND_HF_TO_MINUTE', append=True)                

'''
pathlist_all = glob.glob('/arch1/group/800466/warehouse/prod/MD/CHINA_CONVERTIBLE_BOND/tick_transaction_to_minute/*/*.csv')
ticker_list = list(set([x.split('/')[-1].split('.csv')[0] for x in pathlist_all]))

standard_columns = ['open','high','low','close','volume','amount','AbsPxPath', 'Ask1AmtMean', 'AskP0', 'AskP1', 'AskP2', 'AskP3', 'AskP4', 'AskV0', 'AskV1', 'AskV2', 'AskV3', 'AskV4', 'AskVolMean', 'B1minus_BWeightedPx_10_to_midprice', 'B1minus_BWeightedPx_5_to_midprice', 'BSOrderAmt_10_to_amount', 'BSOrderAmt_1_to_amount', 'BSOrderAmt_5_to_amount', 'Bid1AmtMean', 'BidAskSpreadMean', 'BidP0', 'BidP1', 'BidP2', 'BidP3', 'BidP4', 'BidV0', 'BidV1', 'BidV2', 'BidV3', 'BidV4', 'BidVolMean', 'Buy1NumOrdersMean', 'Buy1NumOrders_mean', 'Buy1OrderQty_mean', 'Buy1Price_mean', 'BuyNumOrdersSumMean', 'BuyOrderAmt_10', 'BuyOrderAmt_10_exp', 'BuyOrderAmt_10_linear', 'BuyOrderAmt_5', 'BuyOrderAmt_5_exp', 'BuyOrderAmt_5_linear', 'BuyOrderAmt_total', 'BuyOrderQtySumMean', 'BuyOrderWeightedPx_10', 'BuyOrderWeightedPx_5', 'BuyTradeMoney', 'BuyTradeNum', 'BuyTradeQuantity', 'BuyUniqueOrderNum', 'LastPx_last15s', 'OBI', 'PxStd', 'PxVolCorr', 'SBWeightedPx_10_to_midprice', 'SBWeightedPx_5_to_midprice', 'SWeightedPx_10_minusS1_to_midprice', 'SWeightedPx_5_minusS1_to_midprice', 'Sell1NumOrdersMean', 'Sell1NumOrders_mean', 'Sell1OrderQty_mean', 'Sell1Price_mean', 'SellNumOrdersSumMean', 'SellOrderAmt_10', 'SellOrderAmt_10_exp', 'SellOrderAmt_10_linear', 'SellOrderAmt_5', 'SellOrderAmt_5_exp', 'SellOrderAmt_5_linear', 'SellOrderAmt_total', 'SellOrderQtySumMean', 'SellOrderWeightedPx_10', 'SellOrderWeightedPx_5', 'SellTradeMoney', 'SellTradeNum', 'SellTradeQuantity', 'SellUniqueOrderNum', 'TotalAskVol', 'TotalBidQty', 'TotalBidVol', 'TotalOfferQty', 'TotalValueTrade', 'TotalVolumeTrade', 'VolStd', 'WeightBuyMoneySumMean', 'WeightBuyNumOrdersSumMean', 'WeightBuyOrderQtySumMean', 'WeightSellMoneySumMean', 'WeightSellNumOrdersSumMean', 'WeightSellOrderQtySumMean', 'WeightedAvgBidPx', 'WeightedAvgOfferPx', 'abs_px_path_tran', 'allbuy_bigorder_count', 'allbuy_bigorder_money', 'allbuy_bigorder_volume', 'allbuy_midorder_count', 'allbuy_midorder_money', 'allbuy_midorder_volume', 'allbuy_smallorder_count', 'allbuy_smallorder_money', 'allbuy_smallorder_volume', 'allbuy_superorder_count', 'allbuy_superorder_money', 'allbuy_superorder_volume', 'allsell_bigorder_count', 'allsell_bigorder_money', 'allsell_bigorder_volume', 'allsell_midorder_count', 'allsell_midorder_money', 'allsell_midorder_volume', 'allsell_smallorder_count', 'allsell_smallorder_money', 'allsell_smallorder_volume', 'allsell_superorder_count', 'allsell_superorder_money', 'allsell_superorder_volume', 'amount_last15s', 'amtOBI_1', 'amtOBI_10', 'amtOBI_10_exp', 'amtOBI_10_linear', 'amtOBI_5', 'amtOBI_5_exp', 'amtOBI_5_linear', 'amtOBI_total', 'amt_b1_ball', 'amt_b1_bexpall', 'amt_b1_s1', 'amt_bexpall_sexpall', 'amt_s1_sall', 'amt_s1_sexpall', 'bas_WeightedPxbas10', 'bas_WeightedPxbas5', 'bas_bas10', 'bas_bas5', 'bas_midpx_WeightedPxbas10', 'bas_midpx_WeightedPxbas5', 'bas_ratio', 'bas_std', 'bid_ask_dis_ratio', 'bs1_amt_mean', 'bs1_amt_min', 'buy_amt_middiff_weighted', 'buy_amtsum_1tomax', 'buy_bigorder_count', 'buy_bigorder_money', 'buy_bigorder_volume', 'buy_market_map_limit_num', 'buy_maxvol_price', 'buy_maxvol_price_vol', 'buy_midorder_count', 'buy_midorder_money', 'buy_midorder_volume', 'buy_smallorder_count', 'buy_smallorder_money', 'buy_smallorder_volume', 'buy_superorder_count', 'buy_superorder_money', 'buy_superorder_volume', 'cumbas_10', 'cumbas_5', 'expweighted_mid10', 'expweighted_mid5', 'idxmax_buyamt', 'idxmax_sellamt', 'market_map_limit_num', 'max_buyamt_price', 'max_buyamt_price_mid', 'max_sellamt_price', 'max_sellamt_price_mid', 'maxvol_price', 'maxvol_price_vol', 'mid_expweighted_mid10', 'mid_expweighted_mid5', 'mid_price', 'mid_weighted_mid10', 'mid_weighted_mid5', 'orderamt10_amount_ratio', 'orderamt1_amount_ratio', 'orderamt5_amount_ratio', 'sell_amt_middiff_weighted', 'sell_amtsum_1tomax', 'sell_bigorder_count', 'sell_bigorder_count_v2', 'sell_bigorder_money', 'sell_bigorder_money_v2', 'sell_bigorder_volume', 'sell_bigorder_volume_v2', 'sell_market_map_limit_num', 'sell_maxvol_price', 'sell_maxvol_price_vol', 'sell_midorder_count', 'sell_midorder_count_v2', 'sell_midorder_money', 'sell_midorder_money_v2', 'sell_midorder_volume', 'sell_midorder_volume_v2', 'sell_smallorder_count', 'sell_smallorder_count_v2', 'sell_smallorder_money', 'sell_smallorder_money_v2', 'sell_smallorder_volume', 'sell_smallorder_volume_v2', 'sell_superorder_count', 'sell_superorder_count_v2', 'sell_superorder_money', 'sell_superorder_money_v2', 'sell_superorder_volume', 'sell_superorder_volume_v2', 'tick_vwap', 'tickup_amount', 'trademoney_ret_sign_sum', 'trademoney_ret_weighted', 'tran_buy_unique_order_count', 'tran_count', 'tran_sell_unique_order_count', 'twap', 'volume_last15s', 'vwap_last15s', 'vwap_midprice', 'vwap_ret_std', 'vwap_std', 'vwapmid_lastpx', 'weighted_mid1', 'weighted_mid10', 'weighted_mid5']
ffill_list = ['LastPx_last15s', 'twap', 'low', 'bas_std', 'weighted_mid1', 'SellOrderWeightedPx_5', 'SellOrderWeightedPx_10', 'high', 'weighted_mid10', 'BuyOrderWeightedPx_5', 'expweighted_mid10', 'max_sellamt_price', 'tick_vwap', 'close', 'open', 'WeightedAvgOfferPx', 'WeightedAvgBidPx', 'BuyOrderWeightedPx_10', 'Sell1Price_mean', 'max_buyamt_price', 'mid_price', 'vwap_last15s', 'vwap_std', 'expweighted_mid5', 'Buy1Price_mean', 'weighted_mid5']
nofill_list = ['amt_b1_bexpall', 'BidP2', 'BidP0', 'buy_maxvol_price', 'SBWeightedPx_10_to_midprice', 'bid_ask_dis_ratio', 'bas_WeightedPxbas5', 'amt_s1_sall', 'amtOBI_10_linear', 'amt_bexpall_sexpall', 'bas_bas10', 'B1minus_BWeightedPx_10_to_midprice', 'bas_midpx_WeightedPxbas10', 'mid_expweighted_mid5', 'AskP0', 'max_sellamt_price_mid', 'idxmax_sellamt', 'bas_bas5', 'AskP4', 'max_buyamt_price_mid', 'bas_midpx_WeightedPxbas5', 'AskP3', 'sell_maxvol_price', 'BidP3', 'amt_b1_ball', 'amt_s1_sexpall', 'maxvol_price', 'SBWeightedPx_5_to_midprice', 'amtOBI_10_exp', 'amtOBI_total', 'BSOrderAmt_5_to_amount', 'idxmax_buyamt', 'mid_expweighted_mid10', 'amtOBI_10', 'BidP1', 'B1minus_BWeightedPx_5_to_midprice', 'BSOrderAmt_10_to_amount', 'vwap_midprice', 'SWeightedPx_5_minusS1_to_midprice', 'cumbas_10', 'cumbas_5', 'vwapmid_lastpx', 'bas_ratio', 'SWeightedPx_10_minusS1_to_midprice', 'AskP2', 'AskP1', 'amtOBI_5', 'mid_weighted_mid5', 'bas_WeightedPxbas10', 'BSOrderAmt_1_to_amount', 'amtOBI_5_exp', 'mid_weighted_mid10', 'amtOBI_5_linear', 'amtOBI_1', 'BidP4', 'amt_b1_s1']
fill0_list = ['sell_smallorder_count_v2', 'amount', 'TotalAskVol', 'BuyOrderAmt_10', 'buy_amt_middiff_weighted', 'buy_bigorder_count', 'BidVolMean', 'Bid1AmtMean', 'SellOrderAmt_10', 'tran_count', 'BuyUniqueOrderNum', 'sell_midorder_count', 'BuyOrderAmt_5', 'AskV4', 'sell_midorder_money', 'WeightSellOrderQtySumMean', 'buy_superorder_money', 'allsell_superorder_money', 'buy_maxvol_price_vol', 'Sell1NumOrders_mean', 'WeightBuyMoneySumMean', 'BidV3', 'sell_superorder_count', 'buy_market_map_limit_num', 'sell_superorder_count_v2', 'tran_sell_unique_order_count', 'bs1_amt_mean', 'allbuy_midorder_count', 'sell_superorder_volume', 'TotalOfferQty', 'BuyOrderAmt_5_linear', 'AskVolMean', 'allsell_midorder_money', 'SellOrderAmt_5_linear', 'BuyOrderAmt_5_exp', 'allsell_smallorder_money', 'SellOrderAmt_total', 'allbuy_bigorder_volume', 'orderamt1_amount_ratio', 'sell_smallorder_volume_v2', 'BidAskSpreadMean', 'sell_bigorder_volume_v2', 'buy_smallorder_money', 'SellNumOrdersSumMean', 'VolStd', 'sell_bigorder_count_v2', 'TotalVolumeTrade', 'allbuy_smallorder_volume', 'market_map_limit_num', 'allbuy_smallorder_money', 'Sell1OrderQty_mean', 'AskV0', 'orderamt5_amount_ratio', 'volume_last15s', 'sell_smallorder_count', 'sell_midorder_volume_v2', 'trademoney_ret_weighted', 'allsell_superorder_count', 'sell_bigorder_volume', 'TotalBidVol', 'BuyNumOrdersSumMean', 'SellUniqueOrderNum', 'abs_px_path_tran', 'allsell_bigorder_volume', 'AskV2', 'WeightBuyOrderQtySumMean', 'Buy1NumOrders_mean', 'trademoney_ret_sign_sum', 'allbuy_midorder_volume', 'WeightBuyNumOrdersSumMean', 'allsell_smallorder_count', 'volume', 'sell_amtsum_1tomax', 'SellOrderQtySumMean', 'allsell_bigorder_money', 'allsell_smallorder_volume', 'SellOrderAmt_10_linear', 'BuyOrderQtySumMean', 'sell_bigorder_money', 'buy_midorder_money', 'allsell_midorder_volume', 'SellOrderAmt_10_exp', 'buy_bigorder_volume', 'BuyTradeNum', 'orderamt10_amount_ratio', 'Ask1AmtMean', 'SellOrderAmt_5_exp', 'WeightSellNumOrdersSumMean', 'allbuy_superorder_count', 'allsell_bigorder_count', 'buy_smallorder_count', 'BidV4', 'Buy1OrderQty_mean', 'sell_bigorder_money_v2', 'allsell_midorder_count', 'BuyTradeMoney', 'bs1_amt_min', 'tickup_amount', 'buy_bigorder_money', 'TotalValueTrade', 'WeightSellMoneySumMean', 'sell_bigorder_count', 'allbuy_superorder_money', 'buy_midorder_count', 'sell_smallorder_money', 'sell_smallorder_money_v2', 'allsell_superorder_volume', 'buy_midorder_volume', 'sell_smallorder_volume', 'sell_midorder_count_v2', 'sell_amt_middiff_weighted', 'sell_superorder_money', 'tran_buy_unique_order_count', 'BuyOrderAmt_10_linear', 'SellTradeMoney', 'vwap_ret_std', 'BuyOrderAmt_total', 'buy_superorder_volume', 'buy_smallorder_volume', 'Buy1NumOrdersMean', 'allbuy_bigorder_money', 'AbsPxPath', 'SellTradeNum', 'amount_last15s', 'allbuy_bigorder_count', 'Sell1NumOrdersMean', 'sell_midorder_volume', 'AskV1', 'TotalBidQty', 'allbuy_superorder_volume', 'maxvol_price_vol', 'buy_superorder_count', 'AskV3', 'OBI', 'BuyOrderAmt_10_exp', 'BidV0', 'PxStd', 'sell_superorder_money_v2', 'BidV1', 'SellTradeQuantity', 'allbuy_smallorder_count', 'PxVolCorr', 'sell_maxvol_price_vol', 'buy_amtsum_1tomax', 'SellOrderAmt_5', 'BuyTradeQuantity', 'BidV2', 'sell_midorder_money_v2', 'sell_superorder_volume_v2', 'sell_market_map_limit_num', 'allbuy_midorder_money']

def get_csvdf_v3(csvpath):
    if not os.path.exists(csvpath):
         return
    try:
        csvdf = pd.read_csv(csvpath, index_col=0, parse_dates=True)#.drop(time_list, axis = 1)
    except Exception as e:
        print(e, csvpath)
        return
    target_index = get_index_fromdate(int(csvpath.split('/')[-2]))
    csvdf = target_index.join(csvdf, how = 'outer').sort_index()
    res_columns = list(set(standard_columns) - set(csvdf.columns))
    for res in res_columns:
        csvdf[res] = np.nan
    csvdf[ffill_list] = csvdf[ffill_list].replace(0,np.nan).fillna(method = 'ffill')
    csvdf[fill0_list] = csvdf[fill0_list].fillna(0)

    csvdf = csvdf.reindex(target_index.index)[standard_columns] 
    return csvdf

def get_index_fromdate(date):
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:56:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()

# 聚合成新框架h5时所用
def get_h5_by_stock(stock):
    pathlist = glob.glob(rootpath + '*/%s.csv' % stock)

    csvdf_list = []
    for path in pathlist:
        csvdf_list.append(get_csvdf_v3(path))
    if len(csvdf_list) == 0:
        print(stock, 'no csv!!!')
        return
    finaldf = pd.concat(csvdf_list, axis = 0).sort_index()

    stk_ret = finaldf['close'].pct_change(1, fill_method=None)
    finaldf['stk_volatility'] = ts_std(stk_ret, 15)

    finaldf['Ticker'] = stock
    finaldf = finaldf.set_index(['Ticker'], append = True)
    
    IO.pd_hdf5_writer(finaldf[standard_columns], os.path.join(h5_path, '%s.h5' % stock), dataset=stock, data_columns=['dt', 'Ticker'])
    '''