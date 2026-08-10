from xquant.marketdata import MarketData
from xquant.factordata import FactorData
from xquant.compute.aimr import AIMR
import pandas as pd
pd.set_option('max_columns', 150)
import datetime 
from multifactor.IO import IO
import numpy as np
import os
from multiprocessing import Pool
import time
import sys
import bottleneck as bk
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from xquant.xqutils.helper import link
lm = link.LinkMessage()

ROOT_PATH = '/data/group/800466/warehouse/prod/MarketData'


def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')

WIND_AShareEODPrices = IO.read_data([20141201, 21000101],columns = ['adjfactor'], alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
WIND_AShareEODPrices = WIND_AShareEODPrices.reset_index()

def get_adjfactor(stock, date):
    df = WIND_AShareEODPrices[WIND_AShareEODPrices['dt'] == pd.to_datetime(str(date))]
    return df[df.Ticker == stock]['adjfactor'].tolist()[0]

# »ñÈ¡¹ÉÆ±µ±ÈÕµÄ×ÔÓÉÁ÷Í¨¹ÉÊýÒÔ¼°»»ÊÖÂÊ
s = FactorData()
ashare_total = s.get_factor_value('WIND_AShareCapitalization', factors = ['S_INFO_WINDCODE','CHANGE_DT', 'FLOAT_A_SHR']).rename(columns = {'S_INFO_WINDCODE':'Ticker'}).set_index('Ticker')
ashare_total['CHANGE_DT'] = ashare_total['CHANGE_DT'].astype('int')
del(s)
def add_turnover_rate(df, stock):
    df = df.reset_index()
    df['CHANGE_DT'] = df.dt.apply(lambda x:int(str(x.date()).replace('-','')))
    ashare = ashare_total.loc[stock].reset_index(drop = True).sort_values(by = 'CHANGE_DT')
    temp = df[['CHANGE_DT']]
    temp2 = pd.merge(temp, ashare, on=['CHANGE_DT'], how = 'outer')
    temp2 = temp2.sort_values(['CHANGE_DT'])
    temp2['FLOAT_A_SHR'] = temp2['FLOAT_A_SHR'].fillna(method = 'ffill')
    temp2 = temp2[temp2.CHANGE_DT >= 20100101]
    temp2 = temp2.drop_duplicates(keep = 'last')

    totaldf = pd.merge(df, temp2, on=['CHANGE_DT'], how = 'left')
    

    totaldf = totaldf.drop(['CHANGE_DT'], axis = 1)
    totaldf.rename(columns = {'FLOAT_A_SHR':'float_shares'}, inplace = True)

    if ('volume' not in totaldf.columns) or ('float_shares' not in totaldf.columns):
        totaldf['turnover_rate'] = np.nan
    else:
        totaldf['turnover_rate'] = totaldf.volume / totaldf.float_shares / 100
    totaldf = totaldf.set_index(['dt'])
    totaldf = totaldf.sort_index()

    return totaldf

# ½«Ã¿ÈÕµÄÊ±¼ä´Á¹Ì¶¨Îª9:30-14:56
def standard_index(data):
    t_days_list = udt.get_trading_date_range(str(data.index[0].date()).replace('-',''),str(data.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:56:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    data = index_df.join(data, how = 'left')
    return data


def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

def update_cfgdata(para):
    try:
        mdp = MarketData()

    #     print(para)
        date = para[0]
        stock = para[1]
        weight = round(para[2],5)

        rootpath = '{}/LOCAL_DATA/CSV/MINUTE/CHINA_STOCK/tick_transaction_tominute_v2/'.format(ROOT_PATH)
        csvpath = os.path.join(rootpath, str(date))
        filepath = os.path.join(csvpath, stock+'.csv')
    #     if os.path.exists(filepath):
    #         return
        h5_rootpath = '{}/MD/CHINA_STOCK/MINUTE/'.format(ROOT_PATH)
        h5_path = os.path.join(h5_rootpath, stock + '.h5')

        tick = mdp.get_data_by_date("Stock", stock, str(date), ['3','5'])

        tickdf = pd.DataFrame()
        if len(tick) > 100:
            fill_na_columns = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price', 'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price']
            df_fill_na = tick[fill_na_columns]
            df_fill_na[df_fill_na == 0] = np.nan
            tick[fill_na_columns] = df_fill_na
            
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

            tick['BidVolMean'] = (tick[['Buy{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
                [0.8 ** i for i in range(10)])).sum(axis=1)
            tick['AskVolMean'] = (tick[['Sell{}OrderQty'.format(i) for i in range(1, 11)]] * np.array(
                [0.8 ** i for i in range(10)])).sum(axis=1)

            aggdict1 = {'AskVolMean':'mean','BidVolMean':'mean','BuyNumOrdersSumMean':'mean','SellNumOrdersSumMean':'mean','BuyOrderQtySumMean':'mean','SellOrderQtySumMean':'mean','WeightBuyOrderQtySumMean':'mean','WeightSellOrderQtySumMean':'mean'}

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
        result.index.names = ['dt']

        result['adjfactor'] = get_adjfactor(stock, date)
        result = add_turnover_rate(result, stock)
        result = standard_index(result)

        result['Ticker'] = stock
        result = result.reset_index().set_index(['dt','Ticker'])


    #     pre20date = datetime.datetime.strptime(str(date), '%Y%m%d') - datetime.timedelta(20)
    #     tomorrowdate = datetime.datetime.strptime(str(date), '%Y%m%d') + datetime.timedelta(1)
    #     if os.path.exists(h5_path):
    #         historydf = IO.read_data([pre20date, date],alt = h5_path)
    #         result = historydf.append(result)
    #     stk_ret = result['close'].pct_change(1, fill_method=None)
    #     result['stk_volatility'] = ts_std(stk_ret, 15)

    #     if len(result) < 1200:
    #         result['stk_index_corr_hs300'] = np.nan
    #         result['stk_index_corr_zz500'] = np.nan
    #     else:
    #         index_data_300 = IO.read_data([pre20date, tomorrowdate], alt = '{}/MD/CHINA_INDEX/MINUTE/000300.SH.h5'.format(ROOT_PATH))
    #         index_close_300 = index_data_300['close'].xs('000300.SH', level = 1)
    #         index_ret_300 = index_close_300.pct_change(1, fill_method=None)
    #         result['stk_index_corr_hs300'] = stk_ret.rolling(1200, min_periods=600).corr(index_ret_300)
    #         result['stk_index_corr_hs300'] = result['stk_index_corr_hs300'].replace([-np.inf, np.inf], np.nan)

    #         index_data_500 = IO.read_data([pre20date, tomorrowdate], alt = '{}/MD/CHINA_INDEX/MINUTE/000905.SH.h5'.format(ROOT_PATH))
    #         index_close_500 = index_data_500['close'].xs('000905.SH', level = 1)
    #         index_ret_500 = index_close_500.pct_change(1, fill_method=None)
    #         result['stk_index_corr_zz500'] = stk_ret.rolling(1200, min_periods=600).corr(index_ret_500)
    #         result['stk_index_corr_zz500'] = result['stk_index_corr_zz500'].replace([-np.inf, np.inf], np.nan)

        result = result.loc[str(date)]

        save_stock_df_to_csv(result,stock,date)

        #if os.path.exists(h5_path):
        #    IO.pd_hdf5_writer(result, h5_path, dataset = stock, append = True)
        #else:
        #    IO.pd_hdf5_writer(result, h5_path, dataset = stock)

        return
    except Exception as e:
        print(para, e)
        return

# »ñÈ¡Ê±¼ä¶ÎÄÚÐèÒª½øÐÐ¸üÐÂµÄ¹ÉÆ±²ÎÊý¡¾stock£¬date£¬weight¡¿
def get_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '{}/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'.format(ROOT_PATH))
    indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()

# »ñÈ¡ÏÂÒ»½»Ò×ÈÕµÄ³É·Ö¹É¼°È¨ÖØ£¬ºÃÓÃÀ´²¹³äÀúÊ±Ò»¸öÔÂµÄÊý¾Ý
def get_nexttday_target_list(ticker, startdate, enddate):
    tickerdict = {'IC.CFE':'index_weight_zz500','IF.CFE':'index_weight_hs300','IH.CFE':'index_weight_sh50'}
    tickercolumn = tickerdict[ticker]
    indexweight = IO.read_data([startdate, enddate],columns = [tickercolumn], alt = '{}/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5'.format(ROOT_PATH))
#     indexweight = indexweight.unstack().shift(1).stack()
    universe = indexweight[indexweight[tickercolumn]>0]
    universe = universe.reset_index()
    universe['dt'] = universe.dt.apply(lambda x:int(str(x)[:10].replace('-','')))
    return np.array(universe).tolist()


def save_stock_df_to_csv(df_result, symbol, date):
    dir_path = '{}/MD/TEMP_STOCK/{}'.format(ROOT_PATH, symbol)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    stock_path = '{}/{}.csv'.format(dir_path, date)

    df_result.to_csv(stock_path)
#     print('{}_{} is saved.'.format(symbol, date))

# ²¹³äÀúÊ·Ò»¸öÔÂµÄÊý¾Ý
def update_30daysdata(plist, ncore):
    print(plist)
    
    for para in plist:
        with Pool(ncore) as pool:
            pool.map(update_cfgdata, para)
        #for item in para:
            
            #update_cfgdata(item)
            
            
def update_by_date(date, ncore = 24):
    last_tday = udt.get_trading_day_offset(date,-1)[0] #ÉÏÒ»¸ö½»Ò×ÈÕ

    today_uplist = get_target_list('IC.CFE',last_tday,date) + get_target_list('IF.CFE',last_tday,date)
    nexttday_uplist = get_nexttday_target_list('IC.CFE',date,date) + get_nexttday_target_list('IF.CFE',date,date)

    today_stklist = [x[1] for x in today_uplist]
    nexttday_stklist = [x[1] for x in nexttday_uplist]

    new_addstk_list = list(set(nexttday_stklist) - set(today_stklist))
    
    with Pool(ncore) as pool:
        pool.map(update_cfgdata, today_uplist)
    #for item in today_uplist:

        #print(item)
        #a = IO.read_data([20210701, 20210930], alt = '/arch1/group/800466/MarketData/MD/CHINA_STOCK/MINUTE/'+item[1]+'.h5').index[-1]
        #if a[0].date() == pd.to_datetime('20210910').date():
            #continue
        #update_cfgdata(item)
        

    print('all stock finished!')
    print(new_addstk_list)
    # Èç¹ûÓÐÐÂµ÷ÈëµÄ¹ÉÆ±£¬½øÐÐ´¦Àí
    if len(new_addstk_list) > 0:
        print('!')
        tdays30days = [int(str(x.date()).replace('-','')) for x in udt.get_trading_date_range(udt.get_trading_day_offset(date,-30)[0],date)]
        new_addstk_uplist = []
        
        for d in tdays30days:
            slist = []
            for stk in new_addstk_list:
                slist.append([d,stk,np.nan])
            new_addstk_uplist.append(slist)            

        # for stk in new_addstk_list:
        #     slist = []
        #     for d in tdays30days:
        #         slist.append([d, stk, np.nan])
        #     new_addstk_uplist.append(slist)

        print('start add history 30days date for new stock!')
        # print(tdays30days)
        update_30daysdata(new_addstk_uplist, ncore = ncore)
    print('done')

    return


if __name__ == '__main__':
    #args = AIMR.getParam().split(',')

    start_date, end_date = '20210712', '20210820'
    # start_date = int(sys.argv[1])
    # end_date = int(sys.argv[2])
    sdate,edate,cdate_list = check_update_date(int(start_date),int(end_date))
    for date in cdate_list:
        print(date)
        update_by_date(date)
    lm.sendMessage('%s done' % start_date)

