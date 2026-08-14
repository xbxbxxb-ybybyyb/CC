# @Time : 2021/1/29 9:36
# @Author : Zhichen Lu
# @File : dailyLastBarStat.py

import pandas as pd
import numpy as np
from ApplicationNo930 import Application
import os
from dataApi.getData import get_minute_1factor
import configparser
from xquant.factordata import FactorData

local_config_path, daily_out_path, holding_info_path, buy_time_info_path, init_conf_path = \
    ('/data/group/800319/strategy_local_pathXtrader/',
     '/data/group/800319/strategy_local_pathXtrader/daily_output/',
     '/data/group/800319/strategy_local_pathXtrader/holding_info/',
     '/data/group/800319/strategy_local_pathXtrader/buy_time_info/',
     '/data/group/800319/strategy_local_pathXtrader/daily_init_config/')


#
#


def get_holding(date):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    holding_info = summary['barly_holding_info'][1430]
    last_buy, last_sell = summary['buy_order_record'][1430], summary['sell_order_record'][1430]
    vol = get_minute_1factor('vol', start_datetime=f'{date}1431', end_datetime=f'{date}1500')
    close = get_minute_1factor('close', start_datetime=f'{date}1431', end_datetime=f'{date}1500')
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
    holding['cash'] = cash_left
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
def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio):
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)

    s = FactorData()
    close = s.get_factor_value('Basic_factor', holding.index.tolist(), [str(date)],
                               factor_names=['close']).droplevel(0)['close']
    cap = close * holding
    account_cap = cash + cap.sum()
    config = configparser.ConfigParser()
    config['strategy_init'] = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': stk_min_amt,
        'per_amt': account_cap * per_signal_ratio,
        'cash': cash,
        'portfolio_id': -1
    }

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
        os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
        config.write(configfile)


def main_stat(date, T_plus_1):
    get_holding(date)
    get_buy_time_info(date)
    daily_initial_generation(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=20000, per_signal_ratio=0.005)


backtest_list = [(20210105, 20210106), (20210106, 20210107), (20210107, 20210108), (20210108, 20210111),
                 (20210111, 20210112), (20210112, 20210113), (20210113, 20210114), (20210114, 20210115)]
main_stat(20210114, 20210115)
