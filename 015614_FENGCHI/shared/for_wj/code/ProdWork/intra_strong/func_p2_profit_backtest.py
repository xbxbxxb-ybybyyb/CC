# -*- coding: utf-8 -*-
# @Time    : 2020/11/13 13:51
# @Author  : wangweidi
# saturn的模拟收益h5
import pandas as pd
import numpy as np
import datetime as dt

def change_code_for_mdp(code, date):
    if (code=='601360.SH') and (date<'20180228'):
        return '601313.SH'
    elif (code=='001872.SZ') and (date<'20181226'):
        return '000022.SZ'
    else:
        return code

def get_next_day(date, date_list):
    if (date in date_list) and (date_list.index(date) < len(date_list)-1):
        return date_list[date_list.index(date) + 1]
    else:
        return np.nan

def cal_time_from_open(trade_time):
    trade_time = dt.datetime.strptime(str(trade_time)[:-3], '%H%M%S')
    time_9_30 = dt.datetime.strptime('93000', '%H%M%S')
    time_12_00 = dt.datetime.strptime('120000', '%H%M%S')
    minute = (trade_time - time_9_30).total_seconds() / 60
    if trade_time > time_12_00:
        minute = minute - 1.5 *60
    return minute / 60 / 4

def buy_backtest(mdp, buy_date, code, buy_vol_pct, max_amt, pre_close, close_price):
    trans_df = mdp.get_data_by_date('Transaction', code, buy_date)
    trans_df = trans_df.sort_values(by='TradeIndex', ascending=True)
    tick_df = mdp.get_data_by_date('stock', code, buy_date)
    trans_df['MDTime'], tick_df['MDTime'] = trans_df['MDTime'].astype(int), tick_df['MDTime'].astype(int)
    rise_pct_chg = 1.2 if (buy_date>='20200824') and (code[:2]=='30') else 1.1
    ul_price = np.floor(pre_close * 100 * rise_pct_chg + 0.5) / 100
    price_930 = trans_df[(trans_df['MDTime']>=93000000) & (trans_df['TradePrice']>0)]['TradePrice'].iloc[0]
    buy_end_time = 94000000 if (trans_df['TradePrice'].max() < ul_price) else min(94000000, trans_df[trans_df['TradePrice']==ul_price].iloc[0]['MDTime'])
    tick_df = tick_df[(tick_df['MDTime']>93005000) & (tick_df['MDTime']<=buy_end_time)]
    if (len(tick_df)==0) or (len(tick_df)==1): #==1的情况是后加的
        # 没机会买入 或者没有数据
        return {'buy_vol':0, 'buy_amt':0, 'buy_vwap':price_930, 'pct_T':close_price / price_930 - 1, 'buy_tick_num':0, 'last_buy_time':buy_end_time}, close_price

    tick_df['cum_amt'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].iloc[0]) * buy_vol_pct
    tick_df['cum_vol'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].iloc[0]) * buy_vol_pct
    if tick_df['cum_amt'].max() <= max_amt:
        # 前十分钟未完成全部交易
        index = -1
        last_buy_time = buy_end_time
    else:
        # 前十分钟完成全部交易
        index = sum(tick_df['cum_amt']<=max_amt)
        last_buy_time = tick_df.iloc[index]['MDTime']

    buy_vwap = tick_df['cum_amt'].iloc[index] / tick_df['cum_vol'].iloc[index]
    buy_vol = min(tick_df['cum_vol'].iloc[index], max_amt//buy_vwap) // 100 * 100
    buy_amt = buy_vol * buy_vwap
    pct_T = close_price / buy_vwap - 1
    return {'buy_vol': buy_vol, 'buy_amt': buy_amt, 'buy_vwap': buy_vwap, 'pct_T': pct_T, 'buy_tick_num':index, 'last_buy_time':last_buy_time}, close_price

def buy_backtest_931(mdp, buy_date, code, buy_vol_pct, max_amt, pre_close, close_price):
    trans_df = mdp.get_data_by_date('Transaction', code, buy_date)
    trans_df = trans_df.sort_values(by='TradeIndex', ascending=True)
    tick_df = mdp.get_data_by_date('stock', code, buy_date)
    trans_df['MDTime'], tick_df['MDTime'] = trans_df['MDTime'].astype(int), tick_df['MDTime'].astype(int)
    rise_pct_chg = 1.2 if (buy_date>='20200824') and (code[:2]=='30') else 1.1
    ul_price = np.floor(pre_close * 100 * rise_pct_chg + 0.5) / 100
    price_931 = trans_df[(trans_df['MDTime'] >= 93100000) & (trans_df['TradePrice'] > 0)]['TradePrice'].iloc[0]
    buy_end_time = 94100000 if (trans_df['TradePrice'].max() < ul_price) else min(94100000, trans_df[trans_df['TradePrice']==ul_price].iloc[0]['MDTime'])
    tick_df = tick_df[(tick_df['MDTime']>93105000) & (tick_df['MDTime']<=buy_end_time)]
    if len(tick_df)==0 or (len(tick_df)==1): #==1的情况是后加的
        # 没机会买入 或者没有数据
        return {'buy_vol':0, 'buy_amt':0, 'buy_vwap':price_931, 'pct_T':close_price / price_931 - 1, 'buy_tick_num':0, 'last_buy_time':buy_end_time}, close_price
    tick_df['cum_amt'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].iloc[0]) * buy_vol_pct
    tick_df['cum_vol'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].iloc[0]) * buy_vol_pct
    if tick_df['cum_amt'].max() <= max_amt:
        # 前十分钟未完成全部交易
        index = -1
        last_buy_time = buy_end_time
    else:
        # 前十分钟完成全部交易
        index = sum(tick_df['cum_amt']<=max_amt)
        last_buy_time = tick_df.iloc[index]['MDTime']

    buy_vwap = tick_df['cum_amt'].iloc[index] / tick_df['cum_vol'].iloc[index]
    buy_vol = min(tick_df['cum_vol'].iloc[index], max_amt//buy_vwap) // 100 * 100
    buy_amt = buy_vol * buy_vwap
    pct_T = close_price / buy_vwap - 1
    return {'buy_vol': buy_vol, 'buy_amt': buy_amt, 'buy_vwap': buy_vwap, 'pct_T': pct_T, 'buy_tick_num':index, 'last_buy_time':last_buy_time}, close_price


def buy_backtest_940(mdp, buy_date, code, buy_vol_pct, max_amt, pre_close, close_price):
    trans_df = mdp.get_data_by_date('Transaction', code, buy_date)
    trans_df = trans_df.sort_values(by='TradeIndex', ascending=True)
    tick_df = mdp.get_data_by_date('stock', code, buy_date)
    trans_df['MDTime'], tick_df['MDTime'] = trans_df['MDTime'].astype(int), tick_df['MDTime'].astype(int)
    rise_pct_chg = 1.2 if (buy_date >= '20200824') and (code[:2] == '30') else 1.1
    ul_price = np.floor(pre_close * 100 * rise_pct_chg + 0.5) / 100
    price_940 = trans_df[(trans_df['MDTime'] >= 94000000) & (trans_df['TradePrice'] > 0)]['TradePrice'].iloc[0]
    buy_end_time = 95000000 if (trans_df['TradePrice'].max() < ul_price) else min(95000000, trans_df[trans_df['TradePrice'] == ul_price].iloc[0]['MDTime'])
    tick_df = tick_df[(tick_df['MDTime'] > 94005000) & (tick_df['MDTime'] <= buy_end_time)]
    if len(tick_df) == 0 or (len(tick_df) == 1):  # ==1的情况是后加的
        # 没机会买入 或者没有数据
        return {'buy_vol': 0, 'buy_amt': 0, 'buy_vwap': price_940, 'pct_T': close_price / price_940 - 1,
                'buy_tick_num': 0, 'last_buy_time': buy_end_time}, close_price
    tick_df['cum_amt'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].iloc[0]) * buy_vol_pct
    tick_df['cum_vol'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].iloc[0]) * buy_vol_pct
    if tick_df['cum_amt'].max() <= max_amt:
        # 前十分钟未完成全部交易
        index = -1
        last_buy_time = buy_end_time
    else:
        # 前十分钟完成全部交易
        index = sum(tick_df['cum_amt'] <= max_amt)
        last_buy_time = tick_df.iloc[index]['MDTime']

    buy_vwap = tick_df['cum_amt'].iloc[index] / tick_df['cum_vol'].iloc[index]
    buy_vol = min(tick_df['cum_vol'].iloc[index], max_amt // buy_vwap) // 100 * 100
    buy_amt = buy_vol * buy_vwap
    pct_T = close_price / buy_vwap - 1
    return {'buy_vol': buy_vol, 'buy_amt': buy_amt, 'buy_vwap': buy_vwap, 'pct_T': pct_T, 'buy_tick_num': index,
            'last_buy_time': last_buy_time}, close_price


def get_minute_list(sell_minute_interval):
    minute_list = np.array(range(930, 1457, sell_minute_interval))
    minute_list = minute_list[minute_list%100<=59.9]
    minute_list = minute_list[(minute_list<1130) | (minute_list>=1300)]
    return minute_list
def get_normal_vol_list(sell_vol, minute_list):
    normal_vol_list = [sell_vol // (len(minute_list) - 1) // 100 * 100] * (len(minute_list) - 1)
    res_vol = sell_vol - sum(normal_vol_list)
    for i in range(int(res_vol // 100)):
        normal_vol_list[i] = normal_vol_list[i] + 100
    normal_vol_list[0] += (sell_vol-sum(normal_vol_list))
    return normal_vol_list

def interval_trade(sell_vol, vol_pct, tick_df, dl_price, ul_price, cover_amt):
    trade_vol_list, trade_price_list = [], []
    touch_ul = 0
    for index, tick_data in tick_df.iterrows():
        if tick_data['LastPx'] == dl_price:
            touch_ul = 1
            continue  # 跌停状态不卖
        elif tick_data['LastPx'] == ul_price:  # 涨停状态
            if tick_data['Buy1OrderQty'] * ul_price > (cover_amt * 10000):
                touch_ul = 1
                continue  # 涨停封单量超过1500W时不卖
            else:  # 快开板了卖掉
                now_trade_vol = min(sell_vol - sum(trade_vol_list), tick_data['Buy1OrderQty'])
                trade_vol_list.append(now_trade_vol)
                trade_price_list.append(ul_price)
        else:  # 非涨停或跌停状态
            now_trade_vol = tick_data['vol'] * vol_pct
            trade_price = (tick_data['amt'] / tick_data['vol']) if tick_data['vol'] > 0 else tick_data['LastPx']
            trade_vol_list.append(now_trade_vol)
            trade_price_list.append(trade_price)
        if sum(trade_vol_list) >= sell_vol:
            trade_vol_list[-1] = sell_vol - sum(trade_vol_list[:-1])
            break  # 卖到足够的量
    tot_acculated_vol = sell_vol - sum(trade_vol_list)
    return trade_vol_list, trade_price_list, tot_acculated_vol, touch_ul

def sell_backtest(mdp, nextday, mdp_code, sell_vol, last_close, date_list, pre_close_list, close_list, vol_pct, cover_amt, sell_minute_interval=5):
    if nextday!=nextday: #目前没有下一交易日
        return {'pct_T1':0, 'sell_len':0, 'date_list':[], 'touch_list':[-2], 'vol_list':[],'finish_indicator':0}
    else:
        tick_md_df = mdp.get_data_by_date('Stock', mdp_code, nextday)
        tick_md_df['MDTime'] = tick_md_df['MDTime'].astype(float)
        tick_md_df['vol'] = tick_md_df['TotalVolumeTrade'] - tick_md_df['TotalVolumeTrade'].shift(1)
        tick_md_df['amt'] = tick_md_df['TotalValueTrade'] - tick_md_df['TotalValueTrade'].shift(1)
        if (len(tick_md_df) == 0): #或者下个交易日没有数据
            return {'pct_T1':0, 'sell_len':0, 'date_list':[], 'touch_list':[-2], 'vol_list':[],'finish_indicator':0}
    pre_close = pre_close_list[date_list.index(nextday)]
    open_price = tick_md_df[tick_md_df['LastPx']>0]['LastPx'].iloc[0]
    close_price = close_list[date_list.index(nextday)]

    rise_pct_chg = 1.2 if (nextday >= '20200824') and (mdp_code[:2] == '30') else 1.1
    down_pct_chg = 0.8 if (nextday >= '20200824') and (mdp_code[:2] == '30') else 0.9
    ul_price = np.floor(pre_close * 100 * rise_pct_chg + 0.5) / 100
    dl_price = np.floor(pre_close * 100 * down_pct_chg + 0.5) / 100

    if (sell_vol <= 0.0001):#已经卖完了
        return {'pct_T1':open_price / pre_close - 1, 'sell_len':0, 'date_list':[], 'touch_list':[-1], 'vol_list':[],'finish_indicator':1}
    if (pre_close != last_close) and (pre_close>=1e-3) and (last_close>=1e-3): #昨收盘价不等于昨日收盘价，说明当日进行了除权除息
        sell_vol = sell_vol * last_close / pre_close

    tick_md_df = tick_md_df[(tick_md_df['LastPx']>0) & (tick_md_df['TradingPhaseCode']=='3')]

    trade_vol_list = []
    trade_price_list = []
    touch_ul = 0
    minute_list = get_minute_list(sell_minute_interval)
    normal_vol_list = get_normal_vol_list(sell_vol, minute_list)
    tot_acculated_vol = 0

    for i in range(len(minute_list)-1):
        minute_interval = [minute_list[i], minute_list[i+1]]
        interval_tick_data = tick_md_df[(tick_md_df['MDTime']>=minute_interval[0]*100000) & (tick_md_df['MDTime']<minute_interval[1]*100000)]
        sell_pct = min(0.2, vol_pct * (tot_acculated_vol+normal_vol_list[i])/normal_vol_list[i]) if normal_vol_list[i]!=0 else vol_pct
        vol_list, price_list, tot_acculated_vol, touch_ul_tmp = interval_trade(tot_acculated_vol+normal_vol_list[i], sell_pct, interval_tick_data, dl_price, ul_price, cover_amt)
        touch_ul = max(touch_ul_tmp, touch_ul)
        trade_vol_list = trade_vol_list + vol_list
        trade_price_list = trade_price_list + price_list

    if sum(trade_vol_list)>0:
        trade_vwap = sum(np.array(trade_vol_list) * np.array(trade_price_list)) / sum(trade_vol_list)
        pct_chg_t1 = trade_vwap / pre_close -1
    else:
        pct_chg_t1 = 0 #今日一字板，未交易
        touch_ul = 2

    if (sum(trade_vol_list) - sell_vol)> -1: #卖到足够量
        touch_ul = -1
        return {'pct_T1':pct_chg_t1, 'sell_len':1, 'date_list':[nextday], 'touch_list':[touch_ul], 'vol_list':[sell_vol],'finish_indicator':1}
    else:
        next_nextday = get_next_day(nextday, date_list)
        next_mdp_code = change_code_for_mdp(code=mdp_code, date=next_nextday)
        next_last_close = close_price
        next_sell_vol = sell_vol - sum(trade_vol_list)
        sell_dic = sell_backtest(mdp, next_nextday, next_mdp_code, next_sell_vol, next_last_close, date_list, pre_close_list, close_list, vol_pct, cover_amt)
        next_pct_chg_t1, next_sell_len, next_sell_date_list, touch_ul_next_list, sell_vol_list, finish_indicator = sell_dic['pct_T1'], sell_dic['sell_len'], sell_dic['date_list'], sell_dic['touch_list'], sell_dic['vol_list'], sell_dic['finish_indicator']
        today_pct_chg = close_price / pre_close - 1
        return {'pct_T1':(pct_chg_t1 * (sum(trade_vol_list) / sell_vol)) + ((1 + today_pct_chg) * (1 + next_pct_chg_t1) - 1) * (1 - sum(trade_vol_list) / sell_vol),
                'sell_len':1 + next_sell_len,
                'date_list':[nextday] + next_sell_date_list,
                'touch_list':[touch_ul] + touch_ul_next_list,
                'vol_list':[sum(trade_vol_list)] + sell_vol_list,
                'finish_indicator':finish_indicator}


def cal_p2_profit_backtest(mdp, tradingday, code, param):
    buy_vol_pct, sell_vol_pct = param['buy_vol_pct'], param['sell_vol_pct']  # 0.05
    max_amt, cover_amt, date_list, pre_close_list = param['max_amt'], param['cover_amt'], param['date_list'], param['pre_close_list']
    p2_type = param['p2_type']
    close_list = param['close_list']
    close = param['close']
    pre_close = param['pre_close']
    res_dic = {'dt':pd.Timestamp(tradingday), 'Ticker':code}
    if p2_type == '930':
        buy_dic, buy_day_close = buy_backtest(mdp, tradingday, code, buy_vol_pct, max_amt, pre_close, close)
    elif p2_type == '931':
        buy_dic, buy_day_close = buy_backtest_931(mdp, tradingday, code, buy_vol_pct, max_amt, pre_close, close)
    elif p2_type == '940':
        buy_dic, buy_day_close = buy_backtest_940(mdp, tradingday, code, buy_vol_pct, max_amt, pre_close, close)
    if len(date_list) == 0:
        sell_dic = {'pct_T1':0, 'sell_len':0, 'date_list':[], 'touch_list':[-2], 'vol_list':[],'finish_indicator':0}
    else:
        sell_dic = sell_backtest(mdp, date_list[0], code, buy_dic['buy_vol'], buy_day_close, date_list, pre_close_list, close_list, sell_vol_pct, cover_amt)
    res_dic = {**res_dic, **buy_dic, **sell_dic}
    res_dic['pct'] = (res_dic['pct_T']+1) * (res_dic['pct_T1']+1) - 1
    return pd.DataFrame(pd.Series(res_dic)).T.set_index(['dt', 'Ticker'])