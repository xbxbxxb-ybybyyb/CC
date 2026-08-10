import re, datetime, time
import numpy as np
import pandas as pd
from overnight.naming_config import *
from xquant.thirdpartydata.marketdata import MarketData
from overnight.utility import concurrent_apply_func, get_future_codes, replace_zero

ma = MarketData()

def get_delta_time(original_time, mdelta):
    combined_datetime = datetime.datetime.combine(datetime.datetime.today(), original_time)
    new_datetime = combined_datetime + datetime.timedelta(minutes=mdelta)
    new_time = new_datetime.time()
    return new_time

def retrieve_single_stock_p1_hfdata(stock, date, start_time, stop_time):
    date_str = date.strftime('%Y%m%d')
    transaction = ma.getMDTransactionDataFrame(stock,date_str + start_time.strftime("%H%M%S"), date_str + stop_time.strftime("%H%M%S"))
    tick = ma.getMDSecurityTickDataFrame(stock,date_str + start_time.strftime("%H%M%S"), date_str + stop_time.strftime("%H%M%S"),1)
    # out_trans_path = os.path.join(hotdata_path, date_str, 'transaction')
    # out_tick_path = os.path.join(hotdata_path, date_str, 'tick')
    # if not os.path.exists(out_trans_path) or not os.path.exists(out_tick_path):
    #     os.makedirs(out_trans_path, exist_ok=True)
    #     os.makedirs(out_tick_path, exist_ok=True)
    # transaction.to_parquet(os.path.join(out_trans_path, f'{stock}.parquet'))
    # tick.to_parquet(os.path.join(out_tick_path, f'{stock}.parquet'))

    result = get_cfg_hfdata(tick, transaction, stock, date, str(futures_data_morning_begin), str(futures_data_morning_end), str(futures_data_afternoon_begin), str(get_delta_time(stop_time, -1)))
    return result

def retrieve_p1_hfdata_helper(start_time, stop_time, date=None, stock_list=None):
    if date is None:
        date = pd.Timestamp.now()
    date_str = date.strftime('%Y%m%d')
    
    out_trans_path = os.path.join(hotdata_path, date_str, 'transaction')
    out_tick_path = os.path.join(hotdata_path, date_str, 'tick')
    if not os.path.exists(out_trans_path) or not os.path.exists(out_tick_path):
        os.makedirs(out_trans_path, exist_ok=True)
        os.makedirs(out_tick_path, exist_ok=True)
        
    if stock_list is None:
        stock_list = pd.read_pickle(os.path.join(hisdata_path, date_str, 'history_09301449.pkl'))[2]['zz500_stock_list']
    result = concurrent_apply_func(retrieve_single_stock_p1_hfdata, stock_list, getdata_parallel_count, date=date, start_time=start_time, stop_time=stop_time, void_log_flag=True)
    combined_df = pd.concat(result.values()).sort_index()
    out_path = os.path.join(hotdata_path, date_str, f"cfg500_hf_data_p1.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    combined_df.to_hdf(out_path, 'cfg500_hf_data_p1', mode='w')

def getdt(a, b):
    strdate = a + ' ' + b
    return datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f')
    
def get_cfg_hfdata(tick, transaction, stock, date, m1, m2, n1, n2):
    try:
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

            # pvcorrdf = tick[['minute','LastPx','volume']].groupby('minute').corr().xs('LastPx', level = 1)[['volume']]
            # pvcorrdf.columns = ['PxVolCorr']
            aggdict = {'Buy1NumOrders':'mean','Sell1NumOrders':'mean','BidAskSpreadMean':'mean','Bid1Amt':'mean','Ask1Amt':'mean','volume':'sum','amount':'sum','pricediff':'sum','LastPx':'std','VolStd':'std'}

            df1amt = tick.resample('1min').agg({**aggdict_ohlc, **aggdict, **aggdict1})
            df1amt = df1amt.rename(columns = {'Buy1NumOrders':'Buy1NumOrdersMean','Sell1NumOrders':'Sell1NumOrdersMean','Bid1Amt':'Bid1AmtMean','Ask1Amt':'Ask1AmtMean','pricediff':'AbsPxPath','LastPx':'PxStd'})

            # check price
            if df1amt.close.sum() > 0:    
                tickdf = df1amt#.join(pvcorrdf)

        transactiondf = pd.DataFrame()
        if len(transaction) > 100:
            transaction['dt'] = transaction.apply(lambda x: getdt(x.MDDate, x.MDTime), axis=1)
            transaction['minute'] = transaction.dt.map(lambda x: x.replace(second=0,microsecond=0))
            transaction = transaction[transaction.TradePrice != 0]

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

            transactiondf = pd.concat([selldf, buydf, sell_small_order, sell_mid_order, sell_big_order, sell_super_order,sell_small_order_v2, sell_mid_order_v2, sell_big_order_v2, sell_super_order_v2,  buy_small_order, buy_mid_order, buy_big_order, buy_super_order], axis = 1)

        result = pd.concat([tickdf, transactiondf], axis = 1)
        if len(result) == 0:
            return pd.DataFrame()
        result.index.name = 'dt'
        result = result.reindex(standard_index(date, m1, m2, n1, n2).index)
        result['Ticker'] = stock
        result = result.set_index('Ticker', append = True)

        csv_columns = result.columns.tolist()
        for k in ['open','high','low','close']:
            if k in csv_columns:
                result[k] = result[k].replace(0, np.nan).fillna(method = 'pad')
        res_columns = list(set(csv_columns) - set(['open','high','low','close']))
        for k in res_columns:
            if k in csv_columns:
                result[k] = result[k].fillna(0)
        return result
    except Exception as e:
        print(stock, date, e)
        return pd.DataFrame()

def standard_index(date, m1, m2, n1, n2):
    t_mins_list = pd.date_range(m1, m2, freq='min').to_list() + pd.date_range(n1, n2, freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for m in t_mins_list:
        index_list.append(str(date) + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    return index_min.set_index('dt').sort_index()   

def retrieve_single_stock_all_hfdata(stock, date, start_time, stop_time):
    date_str = date.strftime('%Y%m%d')
    # stime = time.time()
    trans_p2 = ma.getMDTransactionDataFrame(stock,date_str + start_time.strftime("%H%M%S"), date_str + stop_time.strftime("%H%M%S"))
    tick_p2 = ma.getMDSecurityTickDataFrame(stock,date_str + start_time.strftime("%H%M%S"), date_str + stop_time.strftime("%H%M%S"),1)
    # time1 = time.time()
    # out_trans_path = os.path.join(hotdata_path, date_str, 'transaction')
    # out_tick_path = os.path.join(hotdata_path, date_str, 'tick')
    # trans_p1 = pd.read_parquet(os.path.join(out_trans_path, f'{stock}.parquet'))
    # tick_p1 = pd.read_parquet(os.path.join(out_tick_path, f'{stock}.parquet'))

    # transaction = pd.concat([trans_p1, trans_p2])
    # tick = pd.concat([tick_p1, tick_p2])
    # time2 = time.time()
    _time = get_delta_time(trade_mid_time, 1)
    result = get_cfg_hfdata(tick_p2, trans_p2, stock, date, str(_time), str(_time), str(get_delta_time(_time, 1)), str(trade_stop_time))
    # time3 = time.time()
    # print(time1 - stime, time2 - time1, time3 - time2)
    return result

def retrieve_all_hfdata_helper(start_time, stop_time, date=None, stock_list=None):
    if date is None:
        date = pd.Timestamp.now()
    date_str = date.strftime('%Y%m%d')
    
    # out_trans_path = os.path.join(hotdata_path, date_str, 'transaction')
    # out_tick_path = os.path.join(hotdata_path, date_str, 'tick')

    if stock_list is None:
        stock_list = pd.read_hdf(os.path.join(hotdata_path, date_str, 'cfg500_hf_data_p1.h5')).index.get_level_values(1).unique().tolist()
    result = concurrent_apply_func(retrieve_single_stock_all_hfdata, stock_list, getdata_parallel_count, date=date, start_time=start_time, stop_time=stop_time, void_log_flag=True)
    combined_df = pd.concat(result.values()).sort_index()
    out_path = os.path.join(hotdata_path, date_str, f"cfg500_hf_data_p2.h5")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    combined_df.to_hdf(out_path, 'cfg500_hf_data_p2', mode='w')

# retrieve_p1_hfdata_helper(trade_start_time, get_delta_time(trade_mid_time, 1), pd.to_datetime('20250109'))
# retrieve_all_hfdata_helper(get_delta_time(trade_mid_time, 1), get_delta_time(trade_stop_time, 1), pd.to_datetime('20250109'))