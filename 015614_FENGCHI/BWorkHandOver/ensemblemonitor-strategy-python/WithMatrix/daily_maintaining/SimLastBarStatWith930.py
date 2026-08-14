# @Time : 2021/3/3 15:59
# @Author : Zhichen Lu
# @File : SimLastBarStat.py

import pandas as pd
import numpy as np
# from online_conf import local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,sub_output_path,path_for_930,ratio_path
from ApplicationNo930 import Application
from dataApi.dividend import getEXRightDividend
import os
from dataApi.getData import get_pre_trade_date, trans_int2windcode,get_recent_trade_date
import configparser
from xquant.factordata import FactorData
from xquant.xqutils.helper import link
import datetime
from ExtraTools import get_path_conf
from dataApi.sendInfo import send_file,send_message
from dataApi.getData import get_minute_1factor
from WithNewFactor.daily_maintaining.HoldingOneMoreDayWithoutTrading import holidng_one_more_day

lm = link.LinkMessage()
s = FactorData()


def get_holding(date, div_cash, buy_cost=0.0001, sell_cost=0.0011, final_holding_info=None):
    if final_holding_info is None:
        if os.path.exists(f'{daily_out_path}{date}/last_bar_holding.pkl'):
            holding_info = pd.read_pickle(f'{daily_out_path}{date}/last_bar_holding.pkl')
            if 'Symbol' in holding_info.columns:
                holding_info = holding_info.set_index('Symbol')
            holding_info.index.names = ['Symbol']
        else:
            holding_info = pd.read_pickle(f'{daily_out_path}{date}_fake_for_final.pkl')['barly_total_holding_info'][1000].set_index('Symbol')
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

    config = configparser.ConfigParser()
    config.read(init_conf_path + '%d.ini' % date)
    strategy_config = dict(config['strategy_init'])
    pre_holding_info = pd.read_pickle(holding_info_path + '%d.pkl' % int(strategy_config['pre_date']))
    # cash_left = pre_holding_info['cash'] - total_buy_amt*(1+buy_cost) + total_sell_amt*(1-sell_cost)
    cash_left = pre_holding_info['cash'] - total_buy_amt - total_buy_cost + total_sell_amt - total_sell_cost
    holding['cash'] = cash_left + div_cash
    div_info = getEXRightDividend()
    div_info = div_info.query(f'date=={date}')  # .set_index('code')
    div_info['code'] = div_info['code'].apply(trans_int2windcode)
    div_info = div_info[div_info['code'].isin(pre_holding_info.keys())].set_index('code')
    print('div len', div_info.shape[0])
    holding['cash'] += (pd.Series(pre_holding_info).loc[div_info.index] * div_info['payoutRatio']).sum()
    holding = holding.reindex(list(set(holding.index).union(set(div_info.index)))).fillna(0)
    holding.loc[div_info.index] += pd.Series(pre_holding_info).loc[div_info.index] * div_info['shareRatio']

    pd.to_pickle(holding_info.reset_index(), f'{daily_out_path}/{date}/final_bar_portfolio_df_1500.pkl')
    pd.to_pickle(dict(holding), holding_info_path + '%d.pkl' % date)
    return div_info


# buy time info preocess
def get_buy_time_info(date, div_info=pd.DataFrame()):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    holding_info = pd.read_pickle(f'{daily_out_path}/{date}/final_bar_portfolio_df_1500.pkl')
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
    if len(div_info) > 0:
        for each in div_info.index:
            if each not in buy_time_info:
                buy_time_info[each] = (date, 1000)
    if set(holding_stk_list) != set(buy_time_info.keys()):
        raise Exception('Holding and buy time info are not match')
    pd.to_pickle(buy_time_info, f'{buy_time_info_path}{date}.pkl')


# daily_initial_generaton
def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio, cash_add=0,initial=False):
    holding = pd.read_pickle(holding_info_path + '%d.pkl' % date)
    cash = holding.pop('cash') + cash_add
    holding = pd.Series(holding)
    if len(holding > 0):
        s = FactorData()
        close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date)])
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
        'stk_min_amt': int(min(stk_min_amt * per_amt, 500000)),
        'per_amt': per_amt,
        'cash': cash,
        'portfolio_id': 201001,
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
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    if not initial:
        config = configparser.ConfigParser()
        config.read(init_conf_path + '%d.ini' % date)
        account_info = dict(config['account_info'])
        pre_account_values = float(account_info['account_value'])
        print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
        lm.sendMessage(f'FIX：{date}收盘现金+股票市值 {round(account_cap, 2)},账面相对前日收益{round(account_cap - pre_account_values, 2)}，'
                       f'相对前日收益 {round((account_cap / pre_account_values - 1) * 100,4)}%，持仓股票 {len(holding)} 只，'
                       f'持仓市值 {round(cap.sum(),2)}， 剩余现金 {round(cash, 2)}')

def out_transfer_file(date,account):
    holding_info_path,local_config_path = path_conf['holding_info_path'],path_conf['local_config_path']
    path_for_930 = path_conf['path_for_930']
    holding_930 = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    holding_930.pop('cash')
    holding_930 = pd.Series(holding_930)
    holding = pd.read_pickle(holding_info_path+'%d.pkl'%date)
    holding.pop('cash')
    holding = pd.Series(holding)
    union_stk_list = list(set(holding_930.index).union(set(holding.index)))
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
    transfer.set_index('编号').to_excel(f'{local_config_path}transfer_file/in{date}_{account}_sim.xlsx')
    send_file(['015664'],f'{local_config_path}transfer_file/in{date}_{account}_sim.xlsx')

def out_transfer_file_930(date, account):
    holding = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    holding.pop('cash')
    holding = pd.Series(holding)
    holding.index = [x[:-3] for x in holding.index]
    holding = holding.reset_index()
    transfer = pd.DataFrame(columns=['编号', '划出交易账户', '划入交易账户', '虚拟账户', '证券代码', '证券市场', '划转数量', '划转成本', '业务标志', '备注', '调仓模式', '持仓类型', '持仓模式'],
                            index=holding.index)

    transfer['编号'] = [x + 1 for x in holding.index]
    transfer['证券代码'] = holding['index']
    transfer['划入交易账户'] = account
    transfer['证券市场'] = holding['index'].apply(lambda x: 1 if int(x) > 400000 else 2)
    transfer['划转数量'] = holding[0]
    transfer['划转成本'] = 10
    transfer['业务标志'] = 5
    transfer['调仓模式'] = 'OMS'
    transfer['持仓类型'] = 0
    transfer['持仓模式'] = 'cash'
    transfer.set_index('编号').to_excel(f'{local_config_path}transfer_file/in{date}_{account}_930.xlsx')
    send_file(['015664'], f'{local_config_path}transfer_file/in{date}_{account}_930.xlsx')


def get_holding_930(date, final_total_holding, cash_added=0):

    summary = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    holding = summary['barly_holding_info'][1000]
    buy_time_info = summary['buy_time_info']
    if not os.path.exists(f'{path_for_930}{date}/'):
        os.mkdir(f'{path_for_930}{date}/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyIn/'):
        os.mkdir(f'{path_for_930}{date}/StrategyIn/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyOut/'):
        os.mkdir(f'{path_for_930}{date}/StrategyOut/')

    if final_total_holding is None:
        if os.path.exists(f'{daily_out_path}{date}/last_bar_holding.pkl'):
            final_total_holding = pd.read_pickle(f'{daily_out_path}{date}/last_bar_holding.pkl')
            final_total_holding.index.names = ['Symbol']
        else:
            final_total_holding = pd.read_pickle(f'{daily_out_path}{date}_fake_for_final.pkl')['barly_total_holding_info'][1000].set_index('Symbol')
        # close = get_minute_1factor('close', start_datetime=f'{date}1500', end_datetime=f'{date}1500').loc[(date, 1500)]
        final_total_holding['buy_cost'] = final_total_holding['TotalBuyAmount'] * 0.0001
        final_total_holding['sell_cost'] = final_total_holding['TotalSellAmount'] * 0.0011
    ###############################
    holding = holding.set_index('Symbol')  # ['NetPosition']
    holding['buy_cost'] = (holding['TotalBuyAmount'] / final_total_holding['TotalBuyAmount']).fillna(0) * final_total_holding['buy_cost']
    holding['sell_cost'] = (holding['TotalSellAmount'] / final_total_holding['TotalSellAmount']).fillna(0) * final_total_holding['sell_cost']

    pre_930_holding = pd.read_pickle(f'{path_for_930}{get_pre_trade_date(date)}/StrategyOut/holding{get_pre_trade_date(date)}.pkl')
    holding = holding[((holding['NetPosition'] > 0) + (holding['TotalSellAmount'] > 0)) > 0]
    holding_930 = summary['barly_holding_info'][930].set_index('Symbol').loc[holding.index]
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'],
                               S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date), str(get_pre_trade_date(date))])
    # div_info = getEXRightDividend()
    # div_info['code'] = div_info['code'].apply(trans_int2windcode)
    # div_info = div_info[div_info['code'].isin(pre_930_holding.keys()) & div_info['date'].eq(today)]
    if len(close) > 0:

        close = close.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE').sort_index()
        zero_stock = holding[(holding['NetPosition'] <= 100) & (holding['NetPosition'] > 0)].index
        holding.loc[zero_stock, 'TotalSellAmount'] += holding.loc[zero_stock, 'NetPosition'] * close.loc[str(date), zero_stock]
        holding.loc[zero_stock, 'NetPosition'] = 0
        holding.loc[zero_stock, 'SellAvailable'] = 0

        detail = pd.DataFrame({
            '昨收价': close.iloc[0],
            '今收价': close.iloc[-1],
            '买入成交价': holding['TotalBuyAmount'] / (holding['NetPosition'] - holding_930['NetPosition']),
            '卖出成交价': holding['TotalSellAmount'] / (holding_930['NetPosition'] - holding['NetPosition']),
            '量': holding['NetPosition'] - holding_930['NetPosition'],
            '费用': holding['buy_cost'] + holding['sell_cost'],
        })
        holding_part = holding[holding['NetPosition'] > 0]['NetPosition']
        detail.loc[holding_part.index, '隔夜持仓'] = holding_part - detail.loc[holding_part.index, '量'].clip(0, np.inf)
        detail['买入收益'] = ((detail['今收价'] - detail['买入成交价'].replace(0, np.nan)) * detail['量'])
        detail['卖出收益'] = (detail['卖出成交价'].replace(0, np.nan) - detail['昨收价']) * detail['量'] * -1
        detail['隔夜持仓收益'] = detail['隔夜持仓'].fillna(0) * (detail['今收价'] - detail['昨收价'])
        detail['费后收益'] = detail['买入收益'].fillna(0) + detail['卖出收益'].fillna(0) + detail['隔夜持仓收益'] - detail['费用']

        close_minute = get_minute_1factor('close', code_list=detail.index.tolist(), start_datetime=today, end_datetime=today).loc[today].loc[930:959]
        vol = get_minute_1factor('vol', code_list=detail.index.tolist(), start_datetime=today, end_datetime=today).loc[today].loc[930:959]
        vwap = (close_minute * vol).sum() / vol.sum()
        vwap.index = vwap.index.map(trans_int2windcode)
        detail['vwap'] = vwap
        detail['买入调仓收益'] = (1 - detail['买入成交价'] / detail['vwap']).replace(1, np.nan).replace(-1, np.nan)
        detail['卖出调仓收益'] = (detail['卖出成交价'] / detail['vwap'] - 1).replace(1, np.nan).replace(-1, np.nan)
        union_stk_list = list(set(summary['sell_order_record'][930].keys()).union(summary['buy_order_record'][930].keys()).union(set(detail.index)))
        detail = detail.reindex(union_stk_list)
        detail['量'] = detail['量'].fillna(0)
        if set(summary['sell_order_record'][930].keys()).intersection(summary['buy_order_record'][930].keys()):
            raise Exception('买卖信号存在交集')
        detail['下单量'] = np.nan
        detail.loc[list(summary['sell_order_record'][930].keys()),'下单量'] = -1*summary['sell_order_record'][930]
        detail.loc[list(summary['buy_order_record'][930].keys()),'下单量'] = summary['buy_order_record'][930]
        detail['完成率'] = detail['量']/detail['下单量']
        detail['tag'] = ''
        detail.loc[list(summary['buy_order_record'][930].keys()),'tag']='当日买入'
        detail.loc[list(summary['sell_order_record'][930].keys()),'tag']='当日卖出'

    else:
        detail = pd.DataFrame()

    if not os.path.exists(f'/data/user/015664/AFuckingTrigger/对比930/{today}/'):
        os.makedirs(f'/data/user/015664/AFuckingTrigger/对比930/{today}/')
    detail.to_excel(f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}.xlsx')
    send_file(['015664'], f'/data/user/015664/AFuckingTrigger/对比930/{today}/逐笔收益930_{today}.xlsx')
    left_cash = pre_930_holding['cash'] - holding['TotalBuyAmount'].sum() + holding['TotalSellAmount'].sum() - holding['buy_cost'].sum() - holding['sell_cost'].sum()

    holding = holding['NetPosition']
    holding = dict(holding[holding > 0])

    holding['cash'] = left_cash + cash_added
    if date == 20210617:
        check = pd.read_pickle('/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/20210616/StrategyOut/holding20210616_suspend_backup.pkl')
        holding['002812.SZ'] = check['002812.SZ']
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
        'stk_min_amt': int(min(stk_min_amt * per_amt, 500000)),
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
    pd.to_pickle(strategy_init, f'{path_for_930}{T_plus_1_date}/StrategyIn/init{T_plus_1_date}.pkl')
    pd.to_pickle(account_info, f'{path_for_930}{T_plus_1_date}/StrategyIn/account_info{T_plus_1_date}.pkl')

    pre_account_values = pd.read_pickle(f'{path_for_930}{date}/StrategyIn/account_info{date}.pkl')['account_value']
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    lm.sendMessage(f'930 : {date}收盘现金+股票市值 {account_cap}，'
                   f'相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
                   f'收益金额{account_cap - pre_account_values}，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')


def calc_two_part_ratio(date):
    holding_7_bar = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding_930_bar = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    compare = pd.DataFrame({'bar_930': pd.Series(holding_930_bar), 'bar_7': pd.Series(holding_7_bar)}).fillna(0)
    ratio = (compare.T / compare.sum(axis=1)).T
    if not os.path.exists(ratio_path):
        os.mkdir(ratio_path)
    pd.to_pickle(ratio.drop('cash'), f'{ratio_path}{date}.pkl')


def main_stat(date, T_plus_1, final_holding, div_cash=0, cash_add=0):
    div_info = get_holding(date, div_cash, final_holding_info=final_holding)
    get_buy_time_info(date, div_info)
    daily_initial_generation(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100,
                             stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1,
                             cash_add=cash_add)


def main_stat_930(date, T_plus_1, final_holding, cash_added=0):
    get_holding_930(date, final_holding, cash_added=cash_added)
    daily_initial_generation930(T_plus_1_date=T_plus_1, date=date, barly_max_buy=100, stk_min_amt=0.2, per_signal_ratio=0.0, order_ratio=0.1)

    # calc_two_part_ratio(date)


def get_final_holding(date, buy_cost=0.0001, sell_cost=0.0011):
    if os.path.exists(f'{daily_out_path}{date}/last_bar_holding.pkl'):
        holding_info = pd.read_pickle(f'{daily_out_path}{date}/last_bar_holding.pkl')
        holding_info.index.names = ['Symbol']
        final_holding = holding_info
    else:
        final_holding = pd.read_pickle(f'{daily_out_path}{date}_fake_for_final.pkl')['barly_total_holding_info'][1000].set_index('Symbol')

    final_holding['buy_cost'] = final_holding['TotalBuyAmount'] * buy_cost
    final_holding['sell_cost'] = final_holding['TotalSellAmount'] * sell_cost
    return final_holding

def init_at_first_day(date,cash=20000000,per_ratio=0.005,order_ratio=0.1,stk_min_amt=0.2,barly_max_buy=100,reinitial_930=False,initial_cash_930=0):
    pre_date = get_pre_trade_date(date)
    pd.to_pickle({'cash':cash},f'{holding_info_path}{pre_date}.pkl')
    pd.to_pickle({},f'{buy_time_info_path}{pre_date}.pkl')
    daily_initial_generation(T_plus_1_date=date, date=pre_date, barly_max_buy=barly_max_buy,
                             stk_min_amt=stk_min_amt, per_signal_ratio=per_ratio, order_ratio=order_ratio,initial=True)

    if reinitial_930:
        if not os.path.exists(f'{path_for_930}{pre_date}/StrategyOut/'):
            os.makedirs(f'{path_for_930}{pre_date}/StrategyOut/')
        pd.to_pickle({'cash':initial_cash_930},f'{path_for_930}{pre_date}/StrategyOut/holding{pre_date}.pkl')
        pd.to_pickle({},f'{path_for_930}{pre_date}/StrategyOut/buy_time_info{pre_date}.pkl')
        if not os.path.exists(f'{path_for_930}{pre_date}/StrategyIn/'):
            os.makedirs(f'{path_for_930}{pre_date}/StrategyIn/')
        pd.to_pickle({ 'account_value': 0,'holding_num': 0},f'{path_for_930}{pre_date}/StrategyIn/account_info{pre_date}.pkl')
        daily_initial_generation930(T_plus_1_date=date, date=pre_date, barly_max_buy=100, stk_min_amt=20000, per_signal_ratio=0.015, order_ratio=0.1)
    calc_two_part_ratio(pre_date)

# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')


path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForMatrix/')
local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,sub_output_path,path_for_930,ratio_path =\
    [path_conf[x] for x in 'local_config_path,daily_out_path,holding_info_path,buy_time_info_path,init_conf_path,sub_output_path,path_for_930,ratio_path'.split(',')]

if __name__ == '__main__':
    # path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3/',True)
    # init_at_first_day(20211122,reinitial_930=True,initial_cash_930=3000000)
    today = get_recent_trade_date()#int(datetime.date.today().strftime('%Y%m%d'))
    import time
    print(today, get_pre_trade_date(today, -1))
    final_holding = None#get_final_holding(today)
    main_stat(today,get_pre_trade_date(today,-1),final_holding=final_holding,cash_add=0) #20210428
    main_stat_930(today, get_pre_trade_date(today,-1),final_holding,cash_added=0)

    # holidng_one_more_day(today,path_conf)
    # daily_initial_generation(T_plus_1_date=get_pre_trade_date(today,-1), date=today, barly_max_buy=100,
    #                          stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1,
    #                          cash_add=0)
    #
    # daily_initial_generation930(T_plus_1_date=get_pre_trade_date(today,-1),
    #                             date=today, barly_max_buy=100, stk_min_amt=0.2,
    #                             per_signal_ratio=0.0, order_ratio=0.1)

    out_transfer_file(today,'201001')
    send_message(['015664'],'OK Sim')


# out_transfer_file_930(today, '201001')

# daily_initial_generation930(T_plus_1_date=get_pre_trade_date(today, -1), date=today, barly_max_buy=100, stk_min_amt=0.2, per_signal_ratio=0.02, order_ratio=0.1)
#
# import shutil
#
#
# if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{today}/StrategyOut/'):
#     shutil.copytree(f'{path_for_930}{today}/StrategyOut/',f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{today}/StrategyOut/')
# if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{today}/StrategyOut/holding{today}.pkl'):
#     shutil.copy(f'{path_for_930}{today}/StrategyOut/holding{today}.pkl',f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{today}/StrategyOut/holding{today}.pkl')
# for each in os.listdir(f'{path_for_930}{today}/StrategyOut/'):
#     if '.' in each:
#         shutil.copy(f'{path_for_930}{today}/StrategyOut/{each}',
#                     f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{today}/StrategyOut/{each}')
# next_day = get_pre_trade_date(today,-1)
# if not os.path.exists(f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{next_day}'):
#     shutil.copytree(f'{path_for_930}{next_day}',f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{next_day}')
#
# for each in os.listdir(f'{path_for_930}{next_day}/StrategyIn/'):
#     shutil.copy(f'{path_for_930}{next_day}/StrategyIn/{each}',f'/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/{next_day}/StrategyIn/{each}')
#
# shutil.copy(f'{ratio_path}{today}.pkl',f'/data/group/800319/strategy_local_path3/ratio_sim/{today}.pkl')
#


"""
import pandas as pd
from dataApi.getData import trans_int2windcode
from dataApi.sendInfo import send_file
_,last_buy_time = pd.read_pickle('/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/daily_res_pn/20210630.pkl')

_,holding_series,_=last_buy_time
path_for_930 = '/data/group/800319/strategy_local_path3/FolderFor930_For_SIM/'

compare = {}
for date in [20210617,20210618,20210621,20210622,20210623,20210625,20210628,20210629]:
    online_holding = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    online_holding.pop('cash')
    offline = pd.Series(holding_series[date])
    offline.index = offline.index.map(trans_int2windcode)
    temp_compare = pd.DataFrame({'实盘':online_holding,'线下':offline}).fillna(0)
    temp_compare['diff'] = temp_compare['实盘'].eq(0) + temp_compare['线下']==0
    temp_compare = temp_compare.sort_values('diff',ascending=False).drop('diff',axis=1)

    detail = pd.read_excel(f'/data/user/015664/AFuckingTrigger/对比930/{date}/逐笔收益930_{date}.xlsx',index_col=0)
    detail = detail.loc[temp_compare.index,['下单量', '完成率', 'tag']].rename({'下单量':'实盘下单量'})
    temp_compare = pd.concat([temp_compare,detail],axis=1)
    compare[date] = temp_compare.copy()


out_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/实盘回测线下跟踪/930/每天收盘线上线下持仓比对.xlsx'
with pd.ExcelWriter(out_file) as writer:
    for each in compare:
        compare[each].to_excel(writer,sheet_name=str(each))

writer.close()
send_file(['015664'],out_file)

"""

