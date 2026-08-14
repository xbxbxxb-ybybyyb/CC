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

def get_holding(date,div_cash,buy_cost=0.0001,sell_cost=0.0011,):
    if os.path.exists(f'{daily_out_path}{date}/last_bar_holding.pkl'):
        holding_info = pd.read_pickle(f'{daily_out_path}{date}/last_bar_holding.pkl')
        holding_info.index.names = ['Symbol']
    else:
        holding_info = pd.read_pickle(f'{daily_out_path}{date}_fake_for_final.pkl')['barly_holding_info'][1430].set_index('Symbol')
    # close = get_minute_1factor('close', start_datetime=f'{date}1500', end_datetime=f'{date}1500').loc[(date, 1500)]
    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding_info.index.tolist(), TRADE_DT=[str(date)])
    close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
    zero_stock = holding_info[(holding_info['NetPosition'] > 0) & (holding_info['NetPosition'] < 100)]
    zero_stk_sell_amt = zero_stock['NetPosition']*close.loc[zero_stock.index]
    holding_info.loc[zero_stk_sell_amt.index,'TotalSellAmount'] += zero_stk_sell_amt
    holding_info.loc[zero_stk_sell_amt.index,['NetPosition','SellAvailable']] = 0

    holding = holding_info[holding_info['NetPosition']>0]['NetPosition']

    total_buy_amt, total_sell_amt = holding_info[['TotalBuyAmount', 'TotalSellAmount']].sum().tolist()

    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    strategy_config = dict(config['strategy_init'])
    pre_holding_info = pd.read_pickle(holding_info_path + '%d.pkl' % int(strategy_config['pre_date']))
    cash_left = pre_holding_info['cash'] - total_buy_amt*(1+buy_cost) + total_sell_amt*(1-sell_cost)
    holding['cash'] = cash_left+div_cash
    pd.to_pickle(holding_info.reset_index(),f'{daily_out_path}/{date}/final_bar_portfolio_df_1500.pkl')
    pd.to_pickle(dict(holding),holding_info_path+'%d.pkl'%date)

#buy time info preocess
def get_buy_time_info(date):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    holding_info = pd.read_pickle(f'{daily_out_path}/{date}/final_bar_portfolio_df_1500.pkl')
    buy_time_info = summary['buy_time_info']
    holding_change = holding_info.set_index('Symbol')['NetPosition'] -  summary['barly_holding_info'][1430].set_index('Symbol')['NetPosition']
    holding_change = holding_change[~holding_change.eq(0)]
    for each in holding_change.index:
        if holding_change[each] > 0 and each not in buy_time_info:
            buy_time_info[each] = (date, 1430)
        if holding_change[each] < 0 and holding_info.set_index('Symbol').loc[each, 'NetPosition'] == 0 and each in buy_time_info:
            buy_time_info.pop(each)
    holding = pd.read_pickle(holding_info_path+'%d.pkl'%date)
    holding.pop('cash')
    holding_stk_list = list(holding.keys())
    if set(holding_stk_list)!=set(buy_time_info.keys()):
        raise Exception('Holding and buy time info are not match')
    pd.to_pickle(buy_time_info,f'{buy_time_info_path}{date}.pkl')

# daily_initial_generaton
def daily_initial_generation(T_plus_1_date,date,barly_max_buy,stk_min_amt,per_signal_ratio,order_ratio):
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash')
    holding = pd.Series(holding)
    if len(holding>0):
        s = FactorData()
        close = s.get_factor_value('WIND_AShareEODPrices',factor_names=['TRADE_DT','S_DQ_CLOSE','S_INFO_WINDCODE'],S_INFO_WINDCODE=holding.index.tolist(),TRADE_DT=[str(date)])
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        cap = close * holding
    else:
        cap = pd.Series()
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
        'portfolio_id': 201001,
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
    lm.sendMessage(f'仿真：{date}收盘现金+股票市值 {round(account_cap,2)},账面相对前日收益{round(account_cap - pre_account_values,2)}，相对前日收益 {round((account_cap / pre_account_values - 1 )* 100,4)}%，持仓股票 {len(holding)} 只，持仓市值 {round(cap.sum(),2)}， 剩余现金 {round(cash,2)}')

def out_transfer_file(date,account):
    holding = pd.read_pickle(holding_info_path+'%d.pkl'%date)
    holding.pop('cash')
    holding = pd.Series(holding)
    holding.index = [x[:-3] for x in holding.index]
    holding = holding.reset_index()
    transfer = pd.DataFrame(columns=['编号', '划出交易账户', '划入交易账户', '虚拟账户', '证券代码', '证券市场', '划转数量', '划转成本', '业务标志', '备注', '调仓模式', '持仓类型', '持仓模式'],
                            index = holding.index)

    transfer['编号'] = [x+1 for x in holding.index]
    transfer['证券代码'] = holding['index']
    transfer['划入交易账户'] = account
    transfer['证券市场'] = holding['index'].apply(lambda x : 1 if int(x)>400000 else 2)
    transfer['划转数量'] = holding[0]
    transfer['划转成本'] = 10
    transfer['业务标志'] = 5
    transfer['调仓模式'] = 'OMS'
    transfer['持仓类型'] = 0
    transfer['持仓模式'] = 'cash'
    transfer.set_index('编号').to_excel(f'{local_config_path}transfer_file/in{date}_{account}.xlsx')


def main_stat(date,T_plus_1,div_cash=0):
    get_holding(date,div_cash)
    get_buy_time_info(date)
    daily_initial_generation(T_plus_1_date=T_plus_1,date=date,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)

today = int(datetime.date.today().strftime('%Y%m%d'))
# print(today,get_pre_trade_date(today,-1))
main_stat(today,get_pre_trade_date(today,-1)) #20210428
# main_stat(today,get_pre_trade_date(today,-1))
# out_transfer_file(today,201001)
# daily_initial_generation(T_plus_1_date=20210223,date=20210222,barly_max_buy=100,stk_min_amt=20000,per_signal_ratio=0.005,order_ratio=0.1)