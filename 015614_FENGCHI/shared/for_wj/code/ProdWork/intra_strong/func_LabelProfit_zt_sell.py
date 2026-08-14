# -*- coding: utf-8 -*-
# @Time    : 2019/12/26 16:21
# @Author  : wangweidi
# 第一版卖出的h5文件
import pandas as pd
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import datetime as dt
def change_code_for_mdp(code, date):
    # if (code=='601360.SH') and (date<'20180228'):
    #     return '601313.SH'
    if (code=='001872.SZ') and (date<'20181226'):
        return '000022.SZ'
    else:
        return code

def get_next_day(date, date_list):
    if (date in date_list) and (date_list.index(date) < len(date_list)-1):
        return date_list[date_list.index(date) + 1]
    else:
        return np.nan

def cal_trading_time_atfer_lags(trading_time, lag_ms):
    trading_time = int(trading_time)
    trading_time = datetime.strptime(str(trading_time), '%H%M%S%f')
    next_trading_time = (trading_time + timedelta(milliseconds=lag_ms))

    if (next_trading_time >  datetime.strptime('113000000', '%H%M%S%f')) and (trading_time <= datetime.strptime('113000000', '%H%M%S%f')):
        next_trading_time = next_trading_time + timedelta(hours=1.5)
    return int(next_trading_time.strftime('%H%M%S%f')[:-3])

def cal_time_from_open(trade_time):
    trade_time = dt.datetime.strptime(str(trade_time)[:-3], '%H%M%S')
    time_9_30 = dt.datetime.strptime('93000', '%H%M%S')
    time_12_00 = dt.datetime.strptime('120000', '%H%M%S')
    minute = (trade_time - time_9_30).total_seconds() / 60
    if trade_time > time_12_00:
        minute = minute - 1.5 *60
    return minute / 60 / 4

def hf_preprocessing(data_type, md_df, btTime=None):
    if (data_type == 'Stock') or (data_type == 'StockAllDay') or (data_type == 'StockAllDayNoTradingPhaseCode'):    #TICK
        use_col = ['MDDate', 'MDTime', 'HTSCSecurityID', 'TradingPhaseCode', 'PreClosePx', 'NumTrades',
                   'TotalVolumeTrade', 'TotalValueTrade', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'MaxPx',
                   'MinPx', 'TotalBidQty', 'TotalOfferQty', 'WeightedAvgBidPx', 'WeightedAvgOfferPx'] + \
                  ['Buy%dPrice'%(i) for i in range(1,11)] + ['Sell%dPrice'%(i) for i in range(1,11)] + \
                  ['Buy%dOrderQty'%(i) for i in range(1,11)] + ['Sell%dOrderQty'%(i) for i in range(1,11)] + \
                  ['Buy%dNumOrders'%(i) for i in range(1, 11)] + ['Sell%dNumOrders'%(i) for i in range(1, 11)] + \
                  ['Buy1NoOrders', 'Buy1OrderDetail', 'Sell1NoOrders', 'Sell1OrderDetail']
        md_df = md_df[use_col]
        md_df['vol'] = md_df['TotalVolumeTrade'] - md_df['TotalVolumeTrade'].shift(1)
        md_df['amt'] = md_df['TotalValueTrade'] - md_df['TotalValueTrade'].shift(1)

        '''
        1:集合竞价；2:集合竞价最后一条；3:连续竞价；4:上午连续竞价最后一条；5:尾盘集合竞价；6:收盘最后一条
        '''

        if data_type != 'StockAllDayNoTradingPhaseCode':
            md_df = pd.concat([md_df[md_df['TradingPhaseCode'] == '1'],
                               md_df[md_df['TradingPhaseCode'] == '2'].drop_duplicates(['TradingPhaseCode'], keep='first'),
                               md_df[md_df['TradingPhaseCode'] == '3'],
                               md_df[md_df['TradingPhaseCode'] == '4'].drop_duplicates(['TradingPhaseCode'], keep='first'),
                               md_df[md_df['TradingPhaseCode'] == '5'],
                               md_df[md_df['TradingPhaseCode'] == '6'].drop_duplicates(['TradingPhaseCode'], keep='first'),
                               ]).sort_values(by='MDTime').reset_index(drop=True)

        md_df['MDTime'] = md_df['MDTime'].astype(int)
        if data_type == 'Stock':
            md_df = md_df[md_df['MDTime'] <= btTime] #泛强势股的数据筛选
        elif data_type == 'StockAllDay':
            md_df = md_df  # 使用全部的数据
        return md_df
    elif data_type == 'Index':
        use_col = ['MDTime', 'PreClosePx', 'LastPx', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'HTSCSecurityID']
        md_df = md_df[use_col]
        md_df['MDTime'] = md_df['MDTime'].astype(int)
        md_df = md_df[md_df['MDTime'] <= btTime]  # 泛强势股的数据筛选
        return md_df
    elif data_type == 'WMinute':#前N日的分钟数据，不包括当日
        use_col = ['HTSCSecurityID', 'MDDate', 'MDTime', 'OpenPx', 'ClosePx', 'HighPx', 'LowPx', 'NumTrades',
                   'TotalVolumeTrade', 'TotalValueTrade']
        md_df = md_df[use_col]
        md_df['MDTime'], md_df['MDDate'] = md_df['MDTime'].astype(int), md_df['MDDate'].astype(int)
        return md_df
    elif data_type in ['Transaction', 'TransactionAllDay']: #逐笔成交
        use_col = ['MDDate', 'MDTime', 'TradeIndex', 'TradeBuyNo', 'TradeSellNo', 'TradeType', 'TradeBSFlag', 'TradePrice', 'TradeQty', 'TradeMoney', 'HTSCSecurityID', 'ReceiveDateTime']
        md_df = md_df[use_col]
        md_df['MDTime'], md_df['MDDate'] = md_df['MDTime'].astype(int), md_df['MDDate'].astype(int)
        if data_type == 'TransactionAllDay':
            return md_df
        elif data_type == 'Transaction':
            return md_df[md_df['MDTime'] <= btTime]

def cal_shot_trade_result(zt_trans_df1, trans_reach_zt_time, lag_ms, max_amt, close_price, ul_price):
    zt_trans_df = zt_trans_df1.sort_values(by='TradeIndex', ascending=True)
    place_time = cal_trading_time_atfer_lags(trans_reach_zt_time, lag_ms)
    if place_time > 145700000:
        #尾盘集合竞价
        shot_vol, shot_amt = 0, 0
    else: # 未开过板，计算排位；开板了，也计算排位
        last_trans_before_place = zt_trans_df[zt_trans_df['MDTime'] >= place_time].iloc[0]
        last_trans_index_before_place = max(last_trans_before_place['TradeSellNo'], last_trans_before_place['TradeBuyNo'])
        trans_df_after_place = (zt_trans_df[zt_trans_df['TradeBuyNo'] > last_trans_index_before_place])
        market_vol = trans_df_after_place[trans_df_after_place['TradePrice'] > 0]['TradeQty'].sum()
        target_vol = np.floor(max_amt / ul_price / 100) * 100
        shot_vol = min(target_vol, market_vol)
        shot_amt = shot_vol * ul_price
    result = {'buy_vol':shot_vol, 'buy_amt':shot_amt, 'pct_t':close_price / ul_price -1}
    return result

def cal_sell_trade_result(mdp, nextday, mdp_code, sell_vol, last_close, date_list, vol_pct):
    if nextday!=nextday: #目前没有下一交易日
        return 0, 0, [], 0, 0
    else:
        tick_md_df = mdp.get_data_by_date('Stock', mdp_code, nextday)
        tick_md_df = hf_preprocessing('StockAllDay', tick_md_df)
        if (len(tick_md_df) == 0): #或者下个交易日没有数据
            return 0, 0, [], 0, 0
    pre_close, open_price, ul_price = tick_md_df['PreClosePx'].iloc[0], tick_md_df['OpenPx'].iloc[-1], tick_md_df['MaxPx'].iloc[-1]
    dl_price, close_price = tick_md_df['MinPx'].iloc[-1], tick_md_df['LastPx'].iloc[-1]
    if (sell_vol == 0):#已经卖完了
        return open_price / pre_close - 1, 0, [], 0, 1
    if pre_close != last_close: #昨收盘价不等于昨日收盘价，说明当日进行了除权除息
        sell_vol = sell_vol * last_close / pre_close

    tick_md_df = tick_md_df[(tick_md_df['LastPx']>0) & (tick_md_df['TradingPhaseCode']=='3')]

    trade_vol_list = []
    trade_price_list = []
    touch_ul = 0
    for index, tick_data in tick_md_df.iterrows():
        if tick_data['LastPx'] == dl_price: continue # 跌停状态不卖
        elif tick_data['LastPx'] == ul_price: # 涨停状态
            if tick_data['Buy1OrderQty']* ul_price > 15000000:
                touch_ul = 1
                continue #涨停封单量超过1500W时不卖
            else: #快开板了卖掉
                now_trade_vol = min(sell_vol - sum(trade_vol_list), tick_data['Buy1OrderQty'])
                trade_vol_list.append(now_trade_vol)
                trade_price_list.append(ul_price)
        else: #非涨停或跌停状态
            now_trade_vol = tick_data['vol'] * vol_pct
            trade_price = (tick_data['amt'] / tick_data['vol']) if tick_data['vol']>0 else tick_data['LastPx']
            trade_vol_list.append(now_trade_vol)
            trade_price_list.append(trade_price)
        if sum(trade_vol_list) >= sell_vol:
            break #卖到足够的量

    if sum(trade_vol_list)>0:
        trade_vwap = sum(np.array(trade_vol_list) * np.array(trade_price_list)) / sum(trade_vol_list)
        pct_chg_t1 = trade_vwap / pre_close -1
    else:
        pct_chg_t1 = 0 #今日一字板，未交易
        touch_ul = 2

    if sum(trade_vol_list) >= sell_vol: #买到足够量
        return pct_chg_t1, cal_time_from_open(tick_data['MDTime'])+0.00001, [nextday], touch_ul, 1
    else:
        next_nextday = get_next_day(nextday, date_list)
        next_mdp_code = change_code_for_mdp(code=mdp_code, date=next_nextday)
        next_last_close = close_price
        next_sell_vol = sell_vol - sum(trade_vol_list)
        next_pct_chg_t1, next_sell_len, next_sell_date_list, touch_ul_next, finish_indicator = cal_sell_trade_result(mdp, next_nextday, next_mdp_code, next_sell_vol, next_last_close,
                                                date_list, vol_pct)
        today_pct_chg = close_price / pre_close - 1
        return (pct_chg_t1 * (sum(trade_vol_list) / sell_vol)) + (
                    (1 + today_pct_chg) * (1 + next_pct_chg_t1) - 1) * (1 - sum(trade_vol_list) / sell_vol), 1 + next_sell_len, [nextday] + next_sell_date_list, touch_ul, finish_indicator

def cal_time_delta(start, end):
    if start > 120000000:
        start = start - 17000000
    if end > 120000000:
        end = end - 17000000
    start_str = str(start)
    end_str = str(end)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    return round(time_delta)

def cal_LabelProfit_zt(stock, date, ZT_Time, mdp, param={}):
    trans_df = mdp.get_data_by_date('Transaction', stock, date)
    trans_df = trans_df.sort_values(by='TradeIndex', ascending=True)
    trans_df = hf_preprocessing('TransactionAllDay', trans_df)
    sell_vol_pct = param['sell_vol_pct']#0.05
    max_amt, lag_ms, date_list = param['max_amt'], param['lag_ms'], param['date_list']
    ul_price, close_price = param['ul_price'], param['close_price']
    if max_amt >= 90 * 10000:
        max_amt = min(max_amt, max_amt * ul_price/10)
    if (date >= '20200706') & (date <= '20200708') & (stock[~0] == 'H'):
        max_amt = min(max_amt, 60 * 10000 * ul_price)
    if (date >= '20200706') & (date <= '20200708') & (stock[~0] == 'Z'):
        max_amt = min(max_amt, 70 * 10000 * ul_price)
    if (date >= '20200709') & (date <= '20200716') & (stock[~0] == 'H'):
        max_amt = min(max_amt, 80 * 10000 * ul_price)
    if (date >= '20200709') & (date <= '20200716') & (stock[~0] == 'Z'):
        max_amt = min(max_amt, 80 * 10000 * ul_price)
    if date >= '20200717':
        max_amt = min(max_amt, 60 * 10000 * ul_price)


    zt_trans_df = trans_df[(trans_df['MDTime'] >= ZT_Time) & (trans_df['TradePrice'] != 0)].copy()
    first_ul_trans = (zt_trans_df[zt_trans_df['MDTime'] == ZT_Time].iloc[0])
    result = cal_shot_trade_result(zt_trans_df1=zt_trans_df,
                                   trans_reach_zt_time=ZT_Time,
                                   lag_ms=lag_ms,
                                   max_amt=max_amt,
                                   close_price=close_price,
                                   ul_price=ul_price)
    try:
        result['delta_ms'] = cal_time_delta(int(first_ul_trans['MDTime']), first_ul_trans['ReceiveDateTime']%1000000000)
    except:
        result['delta_ms'] = 0

    #次日卖出部分
    nextday = get_next_day(date, date_list)
    mdp_code = change_code_for_mdp(code=stock, date=date)
    result['pct_t1'], result['sell_length'], result['sell_date'] , result['touch_ul'], result['finish_indicator']= \
        cal_sell_trade_result(mdp=mdp, nextday=nextday, mdp_code=mdp_code, sell_vol=result['buy_vol'],
                              last_close=close_price, date_list=date_list, vol_pct=sell_vol_pct)
    result['sell_date'] = str([int(day) for day in result['sell_date']])
    result['pct'] = ((1 + result['pct_t']) * (1 + result['pct_t1']) - 1)
    result['dt'], result['Ticker'] = pd.Timestamp(str(date)), stock
    result = pd.DataFrame(pd.Series(result)).T
    result = result.set_index(['dt', 'Ticker'])
    return result


