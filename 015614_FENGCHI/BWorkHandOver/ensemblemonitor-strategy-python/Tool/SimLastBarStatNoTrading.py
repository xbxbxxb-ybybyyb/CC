# @Time : 2021/3/3 15:59
# @Author : Zhichen Lu
# @File : SimLastBarStat.py

import pandas as pd
import numpy as np
from online_conf import local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path
from ApplicationNo930 import Application
import os
from dataApi.getData import get_pre_trade_date
import configparser
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
import datetime
lm = link.LinkMessage()
s = FactorData()

def get_holding(date,buy_cost=0.0001,sell_cost=0.0011):
    holding = pd.read_pickle(holding_info_path+'%d.pkl'%get_pre_trade_date(date))
    pd.to_pickle(dict(holding),holding_info_path+'%d.pkl'%date)

#buy time info preocess
def get_buy_time_info(date):
    buy_time_info = pd.read_pickle(f'{buy_time_info_path}{get_pre_trade_date(date)}.pkl')
    pd.to_pickle(buy_time_info,f'{buy_time_info_path}{date}.pkl')

# daily_initial_generaton
def daily_initial_generation(T_plus_1_date,date,barly_max_buy,stk_min_amt,per_signal_ratio,order_ratio):
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)

    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices',factor_names=['TRADE_DT','S_DQ_CLOSE','S_INFO_WINDCODE'],S_INFO_WINDCODE=holding.index.tolist(),TRADE_DT=[str(date)])
    close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
    cap = close * holding
    account_cap = cash + cap.sum()
    config = configparser.ConfigParser()
    per_amt = max(account_cap * per_signal_ratio//10000*10000,10000)
    config['strategy_init'] = {
        'date': T_plus_1_date,
        'pre_date': date,
        'barly_max_buy': barly_max_buy,
        'stk_min_amt': stk_min_amt,
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': -1,
        'order_ratio':order_ratio
    }

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
        os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
        config.write(configfile)
    print({'holding':len(holding),'account_value':account_cap,'cash':cash,'equity_cap':cap.sum()})
    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    account_info = dict(config['account_info'])
    pre_account_values = float(account_info['account_value'])
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    lm.sendMessage(f'{date}收盘现金+股票市值 {round(account_cap,2)}，相对前日收益 {round((account_cap / pre_account_values - 1 )* 100,4)}%，持仓股票 {len(holding)} 只，持仓市值 {round(cap.sum(),2)}， 剩余现金 {round(cash,2)}')

def out_transfer_file(date):
    holding = pd.read_pickle(holding_info_path+'%d.pkl'%date)
    holding.pop('cash')
    holding = pd.Series(holding)
    holding.index = [x[:-3] for x in holding.index]
    holding = holding.reset_index()
    transfer = pd.DataFrame(columns=['编号', '划出交易账户', '划入交易账户', '虚拟账户', '证券代码', '证券市场', '划转数量', '划转成本', '业务标志', '备注', '调仓模式', '持仓类型', '持仓模式'],
                            index = holding.index)

    transfer['编号'] = [x+1 for x in holding.index]
    transfer['证券代码'] = holding['index']
    transfer['划入交易账户'] = 370301
    transfer['证券市场'] = holding['index'].apply(lambda x : 1 if int(x)>400000 else 2)
    transfer['划转数量'] = holding[0]
    transfer['划转成本'] = 10
    transfer['业务标志'] = 5
    transfer['调仓模式'] = 'OMS'
    transfer['持仓类型'] = 0
    transfer['持仓模式'] = 'cash'
    transfer.set_index('编号').to_excel(f'{local_config_path}transfer_file/in{date}.xlsx')


def main_stat(date,T_plus_1):
    get_holding(date)
    get_buy_time_info(date)
    daily_initial_generation(T_plus_1_date=T_plus_1,date=date,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)

today = int(datetime.date.today().strftime('%Y%m%d'))
print(today,get_pre_trade_date(today,-1))
main_stat(today,get_pre_trade_date(today,-1))
out_transfer_file(today)
# daily_initial_generation(T_plus_1_date=20210223,date=20210222,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)