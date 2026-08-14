# @Time : 2021/1/29 9:36
# @Author : Zhichen Lu
# @File : dailyLastBarStat.py

import pandas as pd
import numpy as np
# from online_conf import local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,path_for_930,sub_output_path,ratio_path
from ExtraTools import get_path_conf
from ApplicationNo930 import Application
import os
from dataApi.getData import get_minute_1factor, get_pre_trade_date
import configparser
from xquant.factordata import FactorData
from xquant.xqutils.helper import link

lm = link.LinkMessage()


#
#
def get_holding(date,cash_added=0):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    holding_info = summary['barly_holding_info'][1430]
    last_buy, last_sell = summary['buy_order_record'][1430], summary['sell_order_record'][1430]
    vol = get_minute_1factor('vol', start_datetime=f'{date}1430', end_datetime=f'{date}1459')
    close = get_minute_1factor('close', start_datetime=f'{date}1430', end_datetime=f'{date}1459')
    vwap = (vol.fillna(0) * close.fillna(method='pad')).sum() / vol.sum()
    vol_up = (vol.sum() * 0.1) // 100 * 100
    vwap.index = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in vwap.index]
    vol_up.index = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in vol_up.index]

    last_buy = pd.DataFrame({'target': last_buy, 'up': vol_up.reindex(last_buy.index).fillna(0)}).min(axis=1)
    last_sell = pd.DataFrame({'target': last_sell, 'up': vol_up.reindex(last_sell.index).fillna(0)}).min(axis=1)
    holding_info = holding_info.set_index('Symbol')
    holding_info.loc[last_buy.index, 'NetPosition'] = holding_info.loc[last_buy.index, 'NetPosition'] + last_buy
    holding_info.loc[last_sell.index, 'NetPosition'] = holding_info.loc[last_sell.index, 'NetPosition'] - last_sell
    holding_info.loc[last_sell.index, 'SellAvailable'] = holding_info.loc[last_sell.index, 'SellAvailable'] - last_sell
    holding_info.loc[last_buy.index, 'TotalBuyAmount'] = holding_info.loc[last_buy.index, 'TotalBuyAmount'] + last_buy * vwap.loc[last_buy.index] * (1 + 0.001)
    holding_info.loc[last_sell.index, 'TotalSellAmount'] = holding_info.loc[last_sell.index, 'TotalSellAmount'] + last_sell * vwap.loc[last_sell.index] * (1 - 0.001)
    holding_info = holding_info.reset_index()

    holding = holding_info[holding_info['NetPosition'] > 0].set_index('Symbol')['NetPosition']
    total_buy_amt, total_sell_amt = holding_info[['TotalBuyAmount', 'TotalSellAmount']].sum().tolist()

    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    strategy_config = dict(config['strategy_init'])
    pre_holding_info = pd.read_pickle(holding_info_path + '%d.pkl' % int(strategy_config['pre_date']))
    cash_left = pre_holding_info['cash'] - total_buy_amt + total_sell_amt
    holding['cash'] = cash_left+cash_added
    pd.to_pickle(holding_info, f'{local_config_path}fake_barly_info/{date}/1500.pkl')
    pd.to_pickle(dict(holding), holding_info_path + '%d.pkl' % date)


# buy time info preocess
def get_buy_time_info(date):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    holding_info = pd.read_pickle(f'{local_config_path}fake_barly_info/{date}/1500.pkl')
    buy_time_info = summary['buy_time_info']
    holding_change = holding_info.set_index('Symbol')['NetPosition'] - summary['barly_holding_info'][1430].set_index('Symbol')['NetPosition']
    holding_change = holding_change[~holding_change.eq(0)]
    for each in holding_change.index:
        if holding_change[each] > 0 and each not in buy_time_info:
            buy_time_info[each] = (date, 1430)
        if holding_change[each] < 0 and holding_info.set_index('Symbol').loc[each, 'NetPosition'] == 0 and each in buy_time_info:
            buy_time_info.pop(each)
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    holding.pop('cash')
    holding_stk_list = list(holding.keys())
    if set(holding_stk_list) != set(buy_time_info.keys()):
        raise Exception('Holding and buy time info are not match')
    pd.to_pickle(buy_time_info, f'{buy_time_info_path}{date}.pkl')


# daily_initial_generaton
def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)

    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date)])
    if len(holding) > 0:
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        cap = close * holding
    else:
        cap = pd.Series()

    account_cap = cash + cap.sum()
    config = configparser.ConfigParser()
    per_amt = max(account_cap * per_signal_ratio // 10000 * 10000, 10000)
    config['strategy_init'] = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': int(min(stk_min_amt*per_amt,500000)),
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': '201001',
        'order_ratio': order_ratio
    }

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
        os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
        config.write(configfile)

    config = configparser.ConfigParser()
    if os.path.exists(init_conf_path + '%d.ini' % date):
        config.read(init_conf_path + '%d.ini' % date)
        account_info = dict(config['account_info'])
        pre_account_values = float(account_info['account_value'])
        print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
        lm.sendMessage(f'{date}收盘现金+股票市值 {account_cap}，相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
                       f'收益额{round(account_cap - pre_account_values,2)}'
                       f'持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
        lm.sendMessage(f'{[date,account_cap,cap.sum(),cash]}')

    else:
        lm.sendMessage('Start Day 930')

def initial_a_strategy(start_cash, start_date, pre_date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    pd.to_pickle({'cash': start_cash}, f'{holding_info_path}{pre_date}.pkl')
    pd.to_pickle({}, f'{buy_time_info_path}{pre_date}.pkl')
    daily_initial_generation(start_date, pre_date, barly_max_buy=barly_max_buy, stk_min_amt=stk_min_amt, per_signal_ratio=per_signal_ratio, order_ratio=order_ratio)


def initial_930_startegy(cash_start, start_date, pre_date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    if not os.path.exists(f'{local_config_path}/FolderFor930/{start_date}/'):
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/')
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/StrategyOut/')
        os.mkdir(f'{local_config_path}/FolderFor930/{start_date}/StrategyIn/')
    if not os.path.exists(f'{local_config_path}/FolderFor930/{pre_date}/'):
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/')
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/')
        os.mkdir(f'{local_config_path}/FolderFor930/{pre_date}/StrategyIn/')
    pd.to_pickle({'cash': cash_start}, f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/holding{pre_date}.pkl')
    pd.to_pickle({}, f'{local_config_path}/FolderFor930/{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
    # if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930/{start_date}/StrategyIn/init{start_date}.pkl'):
    conf = {
        'date': start_date,
        'pre_date': pre_date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': stk_min_amt,
        'per_amt': max(cash_start * per_signal_ratio // 10000 * 10000, 10000),
        'cash': cash_start,
        'portfolio_id': '201001',
        'order_ratio': order_ratio
    }
    pd.to_pickle(conf, f'{path_for_930}/{start_date}/StrategyIn/init{start_date}.pkl')
    pd.to_pickle({'account_value': cash_start, 'holding_num': 0}, f'{path_for_930}/{start_date}/StrategyIn/account_info{start_date}.pkl')


def get_holding_930(date,cash_added=0):
    summary = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    holding = summary['barly_holding_info'][1000]
    buy_time_info = summary['buy_time_info']
    if not os.path.exists(f'{path_for_930}{date}/'):
        os.mkdir(f'{path_for_930}{date}/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyIn/'):
        os.mkdir(f'{path_for_930}{date}/StrategyIn/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyOut/'):
        os.mkdir(f'{path_for_930}{date}/StrategyOut/')
    holding = holding.set_index('Symbol')['NetPosition']
    holding = dict(holding[holding > 0])
    holding['cash'] = summary['last_bar_initial_cash']+cash_added
    pd.to_pickle(holding, f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    pd.to_pickle(buy_time_info, f'{path_for_930}{date}/StrategyOut/buy_time_info{date}.pkl')


def daily_initial_generation930(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    if not os.path.exists(f'{path_for_930}{T_plus_1_date}/'):
        os.mkdir(f'{path_for_930}{T_plus_1_date}/')
    if not os.path.exists(f'{path_for_930}{T_plus_1_date}/StrategyIn/'):
        os.mkdir(f'{path_for_930}{T_plus_1_date}/StrategyIn/')
    if not os.path.exists(f'{path_for_930}{T_plus_1_date}/StrategyOut/'):
        os.mkdir(f'{path_for_930}{T_plus_1_date}/StrategyOut/')

    holding = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    cash = holding.pop('cash')
    holding = pd.Series(holding)

    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date)])
    if len(holding) > 0:
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        cap = close * holding
    else:
        cap = pd.Series()

    account_cap = cash + cap.sum()
    per_amt = max(account_cap * per_signal_ratio // 10000 * 10000, 10000)
    strategy_init = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': stk_min_amt,
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': '201001',
        'order_ratio': order_ratio
    }

    account_info = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    pd.to_pickle(strategy_init, f'{path_for_930}{T_plus_1_date}/StrategyIn/init{T_plus_1_date}.pkl')
    pd.to_pickle(account_info, f'{path_for_930}{T_plus_1_date}/StrategyIn/account_info{T_plus_1_date}.pkl')

    pre_account_values = pd.read_pickle(f'{path_for_930}{date}/StrategyIn/account_info{date}.pkl')['account_value']
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    lm.sendMessage(f'930 : {date}收盘现金+股票市值 {account_cap}，相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')


def calc_two_part_ratio(date):
    holding_7_bar = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    if not os.path.exists(ratio_path):
        os.mkdir(ratio_path)
    pd.to_pickle(ratio.drop('cash'), f'{ratio_path}{date}.pkl')

def get_vol_info(date):
    from StrongStockModel.conf.path_config import deal_price_path
    from dataApi.getData import trans_int2windcode
    next_day = get_pre_trade_date(date, -1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{path_for_930}{next_day}/'):
        os.mkdir(f'{path_for_930}{next_day}/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyIn/')
        os.mkdir(f'{path_for_930}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date, 930)].fillna(0), f'{path_for_930}{next_day}/StrategyIn/vol_info{next_day}.pkl')

# def initial_strategy()

def main_stat(date, T_plus_1,cash_added=0):
    get_holding(date,cash_added=cash_added)
    get_buy_time_info(date)
    daily_initial_generation(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1)

def main_stat_930(date, T_plus_1,cash_added=0):
    get_holding_930(date,cash_added)
    daily_initial_generation930(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=20000, per_signal_ratio=0.005, order_ratio=0.1)
    calc_two_part_ratio(date)
    get_vol_info(date)

def init_at_first_day(date,cash=20000000,per_ratio=0.005,order_ratio=0.1,stk_min_amt=0.2,barly_max_buy=100,reinitial_930=False):
    pre_date = get_pre_trade_date(date)
    pd.to_pickle({'cash':cash},f'{holding_info_path}{pre_date}.pkl')
    pd.to_pickle({},f'{buy_time_info_path}{pre_date}.pkl')
    daily_initial_generation(T_plus_1_date=date, date=pre_date, barly_max_buy=barly_max_buy, stk_min_amt=stk_min_amt, per_signal_ratio=per_ratio, order_ratio=order_ratio)
    if reinitial_930:
        pd.to_pickle({'cash':0},f'{path_for_930}{pre_date}/StrategyOut/holding{pre_date}.pkl')
        pd.to_pickle({},f'{path_for_930}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
    calc_two_part_ratio(pre_date)


path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
local_config_path, daily_out_path, holding_info_path, buy_time_info_path, init_conf_path, path_for_930, sub_output_path, ratio_path = \
    [path_conf[x] for x in ['local_config_path', 'daily_out_path', 'holding_info_path', 'buy_time_info_path', 'init_conf_path', 'path_for_930', 'sub_output_path', 'ratio_path']]

# init_at_first_day(20211115,reinitial_930=True)
# if __name__ == '__main__':
#
#     init_at_first_day(20210802,50000000,reinitial_930=True)
# initial_930_startegy(6000000,20210513,20210512,barly_max_buy=100,stk_min_amt=60000,per_signal_ratio=0.05,order_ratio=0.1)
# initial_a_strategy(20000000,20210302,20210301,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)
# pd.to_pickle(pd.DataFrame(columns=['bar_930', 'bar_7']),f'{ratio_path}20210507.pkl')
# calc_two_part_ratio(20210510)
# print(local_config_path)
# main_stat(20210301,20210302)
# daily_initial_generation(T_plus_1_date=20210324,date=20210323,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)
