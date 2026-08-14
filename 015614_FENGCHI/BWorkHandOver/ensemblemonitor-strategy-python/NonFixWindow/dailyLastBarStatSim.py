# @Time : 2021/1/29 9:36
# @Author : Zhichen Lu
# @File : dailyLastBarStat.py

import pandas as pd
import numpy as np
from ExtraTools import get_path_conf
import os
from dataApi.getData import get_minute_1factor,_get_minute_1factor,trans_windcode2int,trans_int2windcode
from dataApi.tradeDate import get_date_range,get_pre_trade_date,get_recent_trade_date
from dataApi.dividend import getEXRightDividend
import configparser
from xquant.factordata import FactorData
from dataApi.sendInfo import  send_message,send_file
# from online_conf import non_fix_in_path,non_fix_output_path,non_fix_path,non_fix_930_path
from ExtraTools import get_nonfix_in_val,save_nonfix_in_val
# non_fix_path = '/data/group/800319/strategy_local_path3/'
non_fix_path = '/data/group/800319/strategy_local_path_nonfixCondition/'
non_fix_930_path = f'{non_fix_path}FolderFor930/'
non_fix_in_path = f'{non_fix_path}daily_input/'
non_fix_output_path = f'{non_fix_path}daily_output/'
sub_output_path = f'{non_fix_path}daily_output/out_930/'

def get_last_bar_holding(path,date):
    file_list = os.listdir(path)
    file_list = sorted(list(filter(lambda x : x.startswith('Deal'),file_list)))
    deal_info = []
    for each in file_list:
        temp = pd.read_excel(path+each)
        deal_info.append(temp)

    deal_info = pd.concat(deal_info).drop_duplicates()


    deal_info['成交额'] = deal_info['成交数量']*deal_info['成交价格']
    deal_info['证券代码'] = deal_info['证券代码'].apply(trans_int2windcode)
    buy_info = deal_info[deal_info['委托方向']=='买']
    sell_info = deal_info[deal_info['委托方向']=='卖']

    pre_holding = get_nonfix_in_val('holding_info',date)
    cash = pre_holding.pop('cash')
    pre_holding = pd.Series(pre_holding)

    stk_list = sorted(list(set(pre_holding.index).union(set(buy_info['证券代码']))))
    buy_stat = buy_info.groupby('证券代码').sum().reindex(stk_list)
    sell_stat = sell_info.groupby('证券代码').sum().reindex(stk_list)

    holding_df = pd.DataFrame(index=stk_list,columns=['NetPosition','TotalBuyAmount', 'TotalSellAmount','SellAvailable'])

    holding_df['NetPosition'] = pre_holding.reindex(stk_list).fillna(0) + buy_stat['成交数量'].fillna(0) - sell_stat['成交数量'].fillna(0)
    holding_df['SellAvailable'] = pre_holding.reindex(stk_list).fillna(0) - sell_stat['成交数量'].fillna(0)
    holding_df['TotalBuyAmount'] = buy_stat['成交额'].fillna(0)
    holding_df['TotalSellAmount'] = sell_stat['成交额'].fillna(0)
    pd.to_pickle(holding_df,f'{non_fix_output_path}{date}/last_bar_holding.pkl')
    return holding_df

def get_holding(date, cash_added, buy_cost=0.0001, sell_cost=0.0011, final_holding_info=None):
    if final_holding_info is None:
        if os.path.exists(f'{non_fix_output_path}{date}/last_bar_holding.pkl'):
            holding_info = pd.read_pickle(f'{non_fix_output_path}{date}/last_bar_holding.pkl')
            if 'Symbol' in holding_info.columns:
                holding_info = holding_info.set_index('Symbol')
            holding_info.index.names = ['Symbol']
        else:
            holding_info = pd.read_pickle(f'{non_fix_output_path}{date}_fake_for_final/final_summary.pkl')['barly_total_holding_info'][1000].set_index('Symbol')
        # close = get_minute_1factor('close', start_datetime=f'{date}1500', end_datetime=f'{date}1500').loc[(date, 1500)]
        holding_info['buy_cost'] = holding_info['TotalBuyAmount'] * buy_cost
        holding_info['sell_cost'] = holding_info['TotalSellAmount'] * sell_cost
    ###############################

    summary_930 = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    holding_930 = summary_930['barly_holding_info'][1000].set_index('Symbol')
    actual_holding_info = holding_info.loc[:, holding_930.columns] - holding_930

    actual_holding_info['buy_cost'] = (actual_holding_info['TotalBuyAmount'] / holding_info['TotalBuyAmount']).fillna(0) * holding_info['buy_cost']
    actual_holding_info['sell_cost'] = (actual_holding_info['TotalSellAmount'] / holding_info['TotalSellAmount']).fillna(0) * holding_info['sell_cost']

    holding_info = actual_holding_info
    s = FactorData()
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding_info.index.tolist(),
                               TRADE_DT=[str(date)])
    close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
    zero_stock = holding_info[(holding_info['NetPosition'] > 0) & (holding_info['NetPosition'] < 100)]
    zero_stk_sell_amt = zero_stock['NetPosition'] * close.loc[zero_stock.index]
    holding_info.loc[zero_stk_sell_amt.index, 'TotalSellAmount'] += zero_stk_sell_amt
    holding_info.loc[zero_stk_sell_amt.index, ['NetPosition', 'SellAvailable']] = 0
    holding_info.loc[zero_stk_sell_amt.index, 'sell_cost'] += zero_stk_sell_amt * sell_cost

    holding = holding_info[holding_info['NetPosition'] > 0]['NetPosition']

    total_buy_amt, total_sell_amt, total_buy_cost, total_sell_cost = holding_info[['TotalBuyAmount', 'TotalSellAmount', 'buy_cost', 'sell_cost']].sum().tolist()

    pre_holding_info = get_nonfix_in_val('holding_info',date,non_fix_path)
    # cash_left = pre_holding_info['cash'] - total_buy_amt*(1+buy_cost) + total_sell_amt*(1-sell_cost)
    cash_left = pre_holding_info['cash'] - total_buy_amt - total_buy_cost + total_sell_amt - total_sell_cost
    holding['cash'] = cash_left + cash_added
    div_info = getEXRightDividend()
    div_info = div_info.query(f'date=={date}')  # .set_index('code')
    div_info['code'] = div_info['code'].apply(trans_int2windcode)
    div_info = div_info[div_info['code'].isin(pre_holding_info.keys())].set_index('code')
    print('div len', div_info.shape[0])
    holding['cash'] += (pd.Series(pre_holding_info).loc[div_info.index] * div_info['payoutRatio']).sum()
    holding = holding.reindex(list(set(holding.index).union(set(div_info.index)))).fillna(0)
    holding.loc[div_info.index] += pd.Series(pre_holding_info).loc[div_info.index] * div_info['shareRatio']
    holding_info.loc[div_info.index,'NetPosition'] += pd.Series(pre_holding_info).loc[div_info.index] * div_info['shareRatio']

    if not os.path.exists(f'{non_fix_path}fake_barly_info/{date}/'):
        os.makedirs(f'{non_fix_path}fake_barly_info/{date}/')
    pd.to_pickle(holding_info.reset_index(), f'{non_fix_path}fake_barly_info/{date}/1500.pkl')
    # pd.to_pickle(dict(holding), holding_info_path + '%d.pkl' % date)
    holding = dict(holding)
    save_nonfix_in_val({x:int(holding[x]) if x!='cash' else holding[x] for x in holding},'holding_info',date,non_fix_path)
    return div_info

# buy time info preocess
def get_buy_time_info(date,div_info):
    summary = pd.read_pickle(f'{non_fix_output_path}/{date}/final_summary.pkl')
    holding_info = pd.read_pickle(f'{non_fix_path}fake_barly_info/{date}/1500.pkl')
    buy_time_info = summary['buy_time_info']
    holding_change = holding_info.set_index('Symbol')['NetPosition'] - summary['barly_holding_info'][1430].set_index('Symbol')['NetPosition']
    holding_change = holding_change[~holding_change.eq(0)]
    for each in holding_change.index:
        if holding_change[each] > 0 and each not in buy_time_info:
            buy_time_info[each] = 2
        if holding_change[each] < 0 and holding_info.set_index('Symbol').loc[each, 'NetPosition'] == 0 and each in buy_time_info:
            buy_time_info.pop(each)
    holding = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)#pd.read_pickle(holding_info_path + '%d.pkl' % date)
    holding.pop('cash')
    holding_stk_list = list(holding.keys())
    if set(holding_stk_list) - set(buy_time_info.keys()):
        raise Exception('Holding and buy time info are not match')
    for each in buy_time_info:
        buy_time_info[each]-=1
        if buy_time_info[each]<0:
            print(f'{each} left {buy_time_info[each]} bars')
    extra_list = set(buy_time_info.keys()) - set(holding_stk_list)
    for each in extra_list:
        buy_time_info.pop(each)
    if len(div_info) > 0:
        for each in div_info.index:
            if each not in buy_time_info:
                buy_time_info[each] = 1
    # pd.to_pickle(buy_time_info, f'{buy_time_info_path}{date}.pkl')
    save_nonfix_in_val(buy_time_info,'left_holding_bar',date,non_fix_path)

# daily_initial_generaton
def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    holding = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)#pd.read_pickle(holding_info_path + '%d.pkl' % date)
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
    send_message(['015664'],f'SIM {dict(config["strategy_init"])}')

    config['account_info'] = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    save_nonfix_in_val(config,'ini',date,non_fix_path)

    if os.path.exists(f'{non_fix_in_path}/{date}/ini{date}.pkl'):
        config = get_nonfix_in_val('ini',date,non_fix_path)
        account_info = dict(config['account_info'])
        pre_account_values = float(account_info['account_value'])
        print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
        send_message(['015664'],f'仿真：{date}收盘现金+股票市值 {account_cap}，相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
                       f'收益额{round(account_cap - pre_account_values,2)}'
                       f'持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
        send_message(['015664'],f'仿真：{[date,account_cap,cap.sum(),cash]}')

    else:
        send_message(['015664'],f'仿真：Start Day')

def initial_a_strategy(start_cash, start_date, pre_date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    # pd.to_pickle({'cash': start_cash}, f'{holding_info_path}{pre_date}.pkl')
    save_nonfix_in_val({'cash': start_cash},'ini',pre_date,non_fix_path)
    save_nonfix_in_val({},'left_holding_bar',pre_date,non_fix_path)
    # pd.to_pickle({}, f'{buy_time_info_path}{pre_date}.pkl')
    daily_initial_generation(start_date, pre_date, barly_max_buy=barly_max_buy, stk_min_amt=stk_min_amt, per_signal_ratio=per_signal_ratio, order_ratio=order_ratio)


def initial_930_startegy(cash_start, start_date, pre_date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    if not os.path.exists(f'{non_fix_path}/FolderFor930/{start_date}/'):
        os.mkdir(f'{non_fix_path}/FolderFor930/{start_date}/')
        os.mkdir(f'{non_fix_path}/FolderFor930/{start_date}/StrategyOut/')
        os.mkdir(f'{non_fix_path}/FolderFor930/{start_date}/StrategyIn/')
    if not os.path.exists(f'{non_fix_path}/FolderFor930/{pre_date}/'):
        os.mkdir(f'{non_fix_path}/FolderFor930/{pre_date}/')
        os.mkdir(f'{non_fix_path}/FolderFor930/{pre_date}/StrategyOut/')
        os.mkdir(f'{non_fix_path}/FolderFor930/{pre_date}/StrategyIn/')
    pd.to_pickle({'cash': cash_start}, f'{non_fix_path}/FolderFor930/{pre_date}/StrategyOut/holding{pre_date}.pkl')
    pd.to_pickle({}, f'{non_fix_path}/FolderFor930/{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
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
    pd.to_pickle(conf, f'{non_fix_930_path}/{start_date}/StrategyIn/init{start_date}.pkl')
    pd.to_pickle({'account_value': cash_start, 'holding_num': 0}, f'{non_fix_930_path}/{start_date}/StrategyIn/account_info{start_date}.pkl')


def get_holding_930(date,cash_added=0):
    sub_output_path = f'{non_fix_output_path}/out_930/'
    if not os.path.exists(sub_output_path):
        os.makedirs(sub_output_path)
    summary = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    holding = summary['barly_holding_info'][1000]
    buy_time_info = summary['buy_time_info']
    if not os.path.exists(f'{non_fix_930_path}{date}/'):
        os.mkdir(f'{non_fix_930_path}{date}/')
    if not os.path.exists(f'{non_fix_930_path}{date}/StrategyIn/'):
        os.mkdir(f'{non_fix_930_path}{date}/StrategyIn/')
    if not os.path.exists(f'{non_fix_930_path}{date}/StrategyOut/'):
        os.mkdir(f'{non_fix_930_path}{date}/StrategyOut/')
    holding = holding.set_index('Symbol')['NetPosition'].astype(int)
    holding = dict(holding[holding > 0])
    holding['cash'] = summary['last_bar_initial_cash']+cash_added
    pd.to_pickle(holding, f'{non_fix_930_path}{date}/StrategyOut/holding{date}.pkl')
    pd.to_pickle(buy_time_info, f'{non_fix_930_path}{date}/StrategyOut/buy_time_info{date}.pkl')


def daily_initial_generation930(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    if not os.path.exists(f'{non_fix_930_path}{T_plus_1_date}/'):
        os.mkdir(f'{non_fix_930_path}{T_plus_1_date}/')
    if not os.path.exists(f'{non_fix_930_path}{T_plus_1_date}/StrategyIn/'):
        os.mkdir(f'{non_fix_930_path}{T_plus_1_date}/StrategyIn/')
    if not os.path.exists(f'{non_fix_930_path}{T_plus_1_date}/StrategyOut/'):
        os.mkdir(f'{non_fix_930_path}{T_plus_1_date}/StrategyOut/')

    holding = pd.read_pickle(f'{non_fix_930_path}{date}/StrategyOut/holding{date}.pkl')
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
    print(strategy_init)
    account_info = {
        'account_value': account_cap,
        'holding_num': len(holding)
    }
    pd.to_pickle(strategy_init, f'{non_fix_930_path}{T_plus_1_date}/StrategyIn/init{T_plus_1_date}.pkl')
    pd.to_pickle(account_info, f'{non_fix_930_path}{T_plus_1_date}/StrategyIn/account_info{T_plus_1_date}.pkl')

    pre_account_values = pd.read_pickle(f'{non_fix_930_path}{date}/StrategyIn/account_info{date}.pkl')['account_value']
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    send_message(['015664'],f'仿真：930 : {date}收盘现金+股票市值 {account_cap}，相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')


def calc_two_part_ratio(date):
    holding_7_bar = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)#pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{non_fix_930_path}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    save_nonfix_in_val(ratio.drop('cash'),'ratio',date,non_fix_path)

def get_vol_info(date):
    from StrongStockModel.conf.path_config import deal_price_path
    from dataApi.getData import trans_int2windcode
    next_day = get_pre_trade_date(date, -1)
    vol_info = pd.read_pickle(deal_price_path + 'vol_rolling_future_30min_sum_5day_mean.pkl')
    vol_info.columns = vol_info.columns.map(trans_int2windcode)
    if date not in vol_info.index:
        raise Exception(f'Vol info of 930 are not update in date {date}')
    if not os.path.exists(f'{non_fix_930_path}{next_day}/'):
        os.mkdir(f'{non_fix_930_path}{next_day}/')
        os.mkdir(f'{non_fix_930_path}{next_day}/StrategyIn/')
        os.mkdir(f'{non_fix_930_path}{next_day}/StrategyOut/')
    pd.to_pickle(vol_info.loc[(date, 930)].fillna(0), f'{non_fix_930_path}{next_day}/StrategyIn/vol_info{next_day}.pkl')

# def initial_strategy()

def main_stat(date, T_plus_1,cash_added=0):
    div_info = get_holding(date,cash_added=cash_added)
    get_buy_time_info(date,div_info)
    daily_initial_generation(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1)

def main_stat_930(date, T_plus_1,cash_added=0):
    # get_holding_930(date,cash_added)
    # daily_initial_generation930(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=20000, per_signal_ratio=0.005, order_ratio=0.1)
    calc_two_part_ratio(date)
    get_vol_info(date)

def init_at_first_day(date,cash=20000000,per_ratio=0.005,order_ratio=0.1,stk_min_amt=0.2,barly_max_buy=100,reinitial_930=False):
    pre_date = get_pre_trade_date(date)
    # pd.to_pickle({'cash':cash},f'{holding_info_path}{pre_date}.pkl')
    save_nonfix_in_val({'cash':cash},'holding_info',pre_date,non_fix_path)
    # pd.to_pickle({},f'{buy_time_info_path}{pre_date}.pkl')
    save_nonfix_in_val({},'left_holding_bar',pre_date,non_fix_path)
    daily_initial_generation(T_plus_1_date=date, date=pre_date, barly_max_buy=barly_max_buy, stk_min_amt=stk_min_amt, per_signal_ratio=per_ratio, order_ratio=order_ratio)
    if reinitial_930:
        pd.to_pickle({'cash':0},f'{non_fix_930_path}{pre_date}/StrategyOut/holding{pre_date}.pkl')
        pd.to_pickle({},f'{non_fix_930_path}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
    # calc_two_part_ratio(pre_date)


def out_transfer_file(date,account):
    # holding_info_path,local_config_path = path_conf['holding_info_path'],path_conf['local_config_path']
    path_for_930 = sub_output_path
    holding_930 = pd.read_pickle(f'{non_fix_930_path}{date}/StrategyOut/holding{date}.pkl')
    holding_930.pop('cash')
    holding_930 = pd.Series(holding_930)
    holding = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)
    holding.pop('cash')
    holding = pd.Series(holding)
    union_stk_list = list(set(holding_930.index).union(set(holding.index)))
    print(f'transfer 930 {len(holding_930)} fix {len(holding)} total {len(union_stk_list)}')
    holding = holding.reindex(union_stk_list).fillna(0) + holding_930.reindex(union_stk_list).fillna(0)


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
    transfer.set_index('编号').to_excel(f'{non_fix_in_path}/{get_pre_trade_date(date,-1)}/in{date}_{account}_sim.xlsx')
    send_file(['015664'],f'{non_fix_in_path}/{get_pre_trade_date(date,-1)}/in{date}_{account}_sim.xlsx')

import time
# time.sleep(120*60)
if __name__ == '__main__':
    today = get_recent_trade_date()
    tommorrow = get_pre_trade_date(today,-1)
    # # get_last_bar_holding(f'{non_fix_output_path}/{today}/deal{today}/',today)
    main_stat(today,tommorrow)
    main_stat_930(today,tommorrow,0)
    out_transfer_file(today,'201001')
    # time.sleep(60*150)
    # get_vol_info(today)

    # final_summary = pd.read_pickle(f'{non_fix_output_path}/20220324/final_summary.pkl')
