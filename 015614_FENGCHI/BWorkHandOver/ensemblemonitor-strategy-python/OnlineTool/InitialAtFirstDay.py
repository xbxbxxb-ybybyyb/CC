# @Time : 2021/12/29 14:15
# @Author : Zhichen Lu
# @File : InitialAtFirstDay.py

import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from dataApi.sendInfo import send_message
import pandas as pd
import numpy as np
from dataApi.getData import trans_int2windcode, get_minute_1factor
from dataApi.tradeDate import get_pre_trade_date
import shutil, os
from xquant.factordata import FactorData
import configparser
from Tool930.daily_update_pre_night import calc_two_part_ratio,get_vol_info
from OnlineTool.OnlineStatWith930_after20211018 import get_path_conf




def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio,
                             afternoon_holding=pd.DataFrame(columns=['市值']), portfolio='201001',initial=False):
    init_conf_path, holding_info_path = path_conf['init_conf_path'], path_conf['holding_info_path']
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)
    if len(holding > 0):
        s = FactorData()
        close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date)])
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        cap = close * holding
    else:
        cap = pd.Series()
    if not np.isclose(cap.sum(), afternoon_holding['市值'].sum()):
        raise Exception('市值不一致')
    account_cap = cash + cap.sum()
    config = configparser.ConfigParser()
    per_amt = max(account_cap * per_signal_ratio // 10000 * 10000, 10000)
    config['strategy_init'] = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': int(min(stk_min_amt * per_amt, 500000)),
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': portfolio,
        'order_ratio': order_ratio
    }

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    T_plus_1_conf = dict(config['strategy_init'])
    if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
        os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
        config.write(configfile)
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    if not initial:
        configT = configparser.ConfigParser()
        configT.read(init_conf_path + '%d.ini' % date)
        account_info = dict(configT['account_info'])
        pre_account_values = float(account_info['account_value'])
        print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
        holding_series = pd.Series(holding)  # .drop('cash')
        if POSITION_CHANGING:
            send_message(['015664'],
                         f'FIX:{date}收盘现金+股票市值 {round(account_cap, 2)}，账面相对前日收益{round(account_cap - pre_account_values, 2)}，'
                         f'相对前日收益 {round((account_cap / pre_account_values - 1) * 100,4)}%，持仓股票 {len(holding_series)} 只,'
                         f'其中0股{len(holding_series[holding_series < 100])}只，持仓市值 {round(cap.sum(), 2)}， 剩余现金 {round(cash, 2)}')
        else:
            send_message(['015664', '003186', '016385', '015836', '011669'],
                         f'FIX:{date}收盘现金+股票市值 {round(account_cap, 2)}，账面相对前日收益{round(account_cap - pre_account_values, 2)}，'
                         f'相对前日收益 {round((account_cap / pre_account_values - 1) * 100,4)}%，持仓股票 {len(holding_series)} 只,'
                         f'其中0股{len(holding_series[holding_series < 100])}只，持仓市值 {round(cap.sum(), 2)}， 剩余现金 {round(cash, 2)}')
    send_message(['015664'],str(dict(T_plus_1_conf)))


def daily_initial_generation930(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio,initial=False):
    path_for_930 = path_conf['path_for_930']
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
        'stk_min_amt': int(min(stk_min_amt * per_amt, 500000)),
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': '201001',
        'order_ratio': order_ratio
    }
    print(strategy_init)
    send_message(['015664'],f'930 init {strategy_init}')
    account_info = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    pd.to_pickle(strategy_init, f'{path_for_930}{T_plus_1_date}/StrategyIn/init{T_plus_1_date}.pkl')
    pd.to_pickle(account_info, f'{path_for_930}{T_plus_1_date}/StrategyIn/account_info{T_plus_1_date}.pkl')
    if not initial:
        pre_account_values = pd.read_pickle(f'{path_for_930}{date}/StrategyIn/account_info{date}.pkl')['account_value']
        print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
        if POSITION_CHANGING:
            send_message(['015664'], f'930 : {date}收盘现金+股票市值 {account_cap}，'
            f'相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
            f'收益金额{account_cap - pre_account_values}，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
        else:
            send_message(['015664', '003186', '016385', '015836', '011669'], f'930 : {date}收盘现金+股票市值 {account_cap}，'
            f'相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
            f'收益金额{account_cap - pre_account_values}，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
        send_message(['015664'], f'930:{strategy_init}')


def init_at_first_day(date,cash=20000000,cash_930=3000000,per_ratio=0.005,order_ratio=0.1,stk_min_amt=0.2,barly_max_buy=100,reinitial_930=False):
    pre_date = get_pre_trade_date(date)
    pd.to_pickle({'cash':cash},f'{holding_info_path}{pre_date}.pkl')
    pd.to_pickle({},f'{buy_time_info_path}{pre_date}.pkl')
    daily_initial_generation(T_plus_1_date=date, date=pre_date, barly_max_buy=barly_max_buy, stk_min_amt=stk_min_amt,
                             per_signal_ratio=per_ratio, order_ratio=order_ratio,initial=True)
    if reinitial_930:
        pd.to_pickle({'cash':cash_930},f'{path_for_930}{pre_date}/StrategyOut/holding{pre_date}.pkl')
        pd.to_pickle({},f'{path_for_930}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
        daily_initial_generation930(T_plus_1_date=date, date=pre_date, barly_max_buy=100,
                                    stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1,initial=True)

        calc_two_part_ratio(pre_date)
        get_vol_info(pre_date)


path_conf = get_path_conf()
local_config_path, daily_out_path, holding_info_path, buy_time_info_path, init_conf_path, path_for_930, sub_output_path, ratio_path = \
    [path_conf[x] for x in ['local_config_path', 'daily_out_path', 'holding_info_path', 'buy_time_info_path', 'init_conf_path', 'path_for_930', 'sub_output_path', 'ratio_path']]

POSITION_CHANGING = True
init_at_first_day(20220112,cash=50000000,cash_930=7000000,reinitial_930=True)
