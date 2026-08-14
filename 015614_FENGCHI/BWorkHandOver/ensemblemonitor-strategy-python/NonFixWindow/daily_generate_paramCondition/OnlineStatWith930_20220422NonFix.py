# @Time : 2021/4/1 10:52
# @Author : Zhichen Lu
# @File : OnlineStat.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

import pandas as pd
import numpy as np
from dataApi.getData import trans_int2windcode, get_minute_1factor

# from dataApi.getData import trans_windcode2int,trans_int2windcode,get_minute_pickle
from dataApi.tradeDate import get_date_range
from dataApi.tradeDate import get_pre_trade_date
import shutil, os
from xquant.factordata import FactorData
import configparser
from xquant.xqutils.helper import link
from dataApi.sendInfo import send_message
lm = link.LinkMessage()
s = FactorData()
import datetime, requests, json
from dataApi.sendInfo import send_file
from dataApi.stockList import get_stock_list
from dataApi.dividend import getEXRightDividend
from ExtraTools import get_nonfix_in_val,save_nonfix_in_val

def format_df(df, port_id, index=None):
    df['组合编号'] = df['组合编号'].apply(lambda x: str(x)[:len(port_id)])
    df = df[df['组合编号'].eq(port_id)].set_index('证券代码')
    if '交易市场' in df.columns:
        df = df[df['交易市场'].isin(['深交所A', '上交所A'])]
    df.index = df.index.astype(int).map(trans_int2windcode)
    return df


def get_holding_and_buy_time(pre_holding, afternoon_portfolio, trading_record, date, port_id, start_cash):
    trading_record = trading_record.reset_index()
    buy_record, sell_record = trading_record[trading_record['委托方向'].eq('买入')], trading_record[trading_record['委托方向'].eq('卖出')]
    buy_record = buy_record.groupby('证券代码').sum()[['累计成交数量', '成交金额']]
    buy_record['成交均价'] = buy_record['成交金额'] / buy_record['累计成交数量']
    sell_record = sell_record.groupby('证券代码').sum()[['累计成交数量', '成交金额']]
    sell_record['成交均价'] = sell_record['成交金额'] / sell_record['累计成交数量']
    stk_list = list(set(pre_holding.index).union(set(afternoon_portfolio.index)))
    calced_holding = pre_holding.reindex(stk_list).fillna(0) + buy_record['累计成交数量'].reindex(stk_list).fillna(0) - \
                     sell_record['累计成交数量'].reindex(stk_list).fillna(0)

    actual_holding = afternoon_portfolio['持仓'].reindex(stk_list).fillna(0)
    ###########持仓校验
    if not np.isclose((calced_holding - actual_holding).apply(abs).max(), 0):
        print('Calc holding are not equal to actual holding')
        # raise Exception('Calc holding are not equal to actual holding')

    actual_holding['cash'] = start_cash - buy_record['成交金额'].sum() + sell_record['成交金额'].sum() - \
                             afternoon_portfolio['当日买费用'].sum() - afternoon_portfolio['当日卖费用'].sum()

    buy_time_info = trading_record[trading_record['委托方向'].eq('买入') & \
                                   (trading_record['累计成交数量'] > 0)].sort_values(['证券代码', '委托时间'])  # .groupby('证券代码').first()
    buy_time_info['buy_signal_time'] = buy_time_info['委托时间'].apply(lambda x: int(str(x).replace(':', '')[:4]))
    buy_time_info['buy_signal_time'] = buy_time_info['buy_signal_time'].apply(lambda x: max(list(filter(lambda each: each < x, bar_list))) if x > bar_list[0] else 930)
    buy_time_info['buy_signal_time'] = buy_time_info['buy_signal_time'].apply(lambda x: (date, x))

    sell_time_info = trading_record[trading_record['委托方向'].eq('卖出') & \
                                    (trading_record['累计成交数量'] > 0)].sort_values(['证券代码', '委托时间'])  # .groupby('证券代码').first()
    sell_time_info['sell_signal_time'] = sell_time_info['委托时间'].apply(lambda x: int(str(x).replace(':', '')[:4]))
    sell_time_info['sell_signal_time'] = sell_time_info['sell_signal_time'].apply(lambda x: max(list(filter(lambda each: each < x, bar_list))) if x > bar_list[0] else 930)
    sell_time_info['sell_signal_time'] = sell_time_info['sell_signal_time'].apply(lambda x: (date, x))
    pre_holding = dict(pre_holding)
    pre_holding['cash'] = start_cash
    return dict(actual_holding[actual_holding != 0]), pre_holding, buy_time_info, sell_time_info, afternoon_portfolio


def calc_profit_decomposition(date, holding, pre_holding, buy_time_info_, sell_time_info, afternoon_holding):
    buy_price = buy_time_info_.groupby(['证券代码', 'buy_signal_time']).sum().reindex(['成交金额', '累计成交数量'],axis=1)
    buy_price['成交价格'] = buy_price['成交金额'] / buy_price['累计成交数量']
    sell_price = sell_time_info.reset_index().groupby(['证券代码', 'sell_signal_time']).sum().reindex(['成交金额', '累计成交数量'],axis=1)
    sell_price['成交价格'] = sell_price['成交金额'] / sell_price['累计成交数量']
    sold_stk = sorted(list(set([x[0] for x in sell_price.index])))
    bought_stk = sorted(list(set([x[0] for x in buy_price.index])))
    stk_list = sorted(list(set(sold_stk).union(set(bought_stk)).union(set(holding.index))))

    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE', 'S_DQ_PRECLOSE'], S_INFO_WINDCODE=stk_list,
                               TRADE_DT=[str(date)])
    if len(close) == 0:
        close = pd.Series()
        pre_close = pd.Series()
    else:
        close['S_DQ_PRECLOSE'] = close['S_DQ_PRECLOSE'].astype(float)
        close['S_DQ_CLOSE'] = close['S_DQ_CLOSE'].astype(float)
        pre_close = close.pivot_table(values='S_DQ_PRECLOSE', index='TRADE_DT', columns='S_INFO_WINDCODE').loc[str(date)]
        close = close.pivot_table(values='S_DQ_CLOSE', index='TRADE_DT', columns='S_INFO_WINDCODE').loc[str(date)]

    sell_price, buy_price = \
        sell_price.reset_index().reindex(['证券代码', 'sell_signal_time','成交金额', '累计成交数量','成交价格'],axis=1), \
        buy_price.reset_index().reindex(['证券代码', 'buy_signal_time','成交金额', '累计成交数量','成交价格'],axis=1)
    sell_price['sell_signal_time'], buy_price['buy_signal_time'] = \
        sell_price['sell_signal_time'].apply(lambda x: x[0] * 10000 + x[1]), \
        buy_price['buy_signal_time'].apply(lambda x: x[0] * 10000 + x[1])

    sell_price['昨收价'] = sell_price['证券代码'].apply(lambda x: pre_close[x])
    buy_price['今收价'] = buy_price['证券代码'].apply(lambda x: close[x])
    sell_price['贡献收益'] = (sell_price['成交价格'] - sell_price['昨收价']) * sell_price['累计成交数量']
    buy_price['贡献收益'] = (buy_price['今收价'] - buy_price['成交价格']) * buy_price['累计成交数量']
    buy_price['类型'] = '当日买入'
    sell_price['类型'] = '当日卖出'
    total_buy = buy_price[['证券代码', '成交金额']].groupby('证券代码').sum()['成交金额']
    buy_price['费用'] = buy_price['成交金额'] * buy_price['证券代码'].apply(lambda x: afternoon_holding.loc[x, '当日买费用'] / total_buy[x])
    total_sell = sell_price[['证券代码', '成交金额']].groupby('证券代码').sum()['成交金额']
    sell_price['费用'] = sell_price['成交金额'] * sell_price['证券代码'].apply(lambda x: afternoon_holding.loc[x, '当日卖费用'] / total_sell[x])

    bought_holding = buy_price.reset_index().groupby('证券代码').sum()['累计成交数量']  # .reindex(holding.index).fillna(0)
    union_stk_list = list(set(bought_holding.index).union(set(holding.index)))
    holding_over_night = pd.DataFrame({'累计成交数量': holding.reindex(union_stk_list).fillna(0) - \
                                                 bought_holding.reindex(union_stk_list).fillna(0)})
    holding_over_night = holding_over_night[holding_over_night['累计成交数量'] > 0]
    holding_over_night['今收价'] = close.loc[holding_over_night.index]
    holding_over_night['昨收价'] = pre_close.loc[holding_over_night.index]
    holding_over_night['贡献收益'] = (holding_over_night['今收价'] - holding_over_night['昨收价']) * holding_over_night['累计成交数量']
    holding_over_night['类型'] = '隔夜持仓'
    holding_over_night.index.names = ['证券代码']
    holding_over_night['费用'] = 0

    record = pd.concat([buy_price, sell_price, holding_over_night.reset_index()])
    record['费后收益'] = record['贡献收益'] - record['费用']
    record.index = list(range(record.shape[0]))
    return record

def daily_initial_generation(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio, afternoon_holding, portfolio):
    # init_conf_path, holding_info_path = path_conf['init_conf_path'], path_conf['holding_info_path']
    holding = get_nonfix_in_val('holding_info',T_plus_1_date,non_fix_path)
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
    # if os.path.exists(init_conf_path + '%d.ini' % T_plus_1_date):
    #     os.remove(init_conf_path + '%d.ini' % T_plus_1_date)
    # with open(init_conf_path + '%d.ini' % T_plus_1_date, 'w') as configfile:
    #     config.write(configfile)
    save_nonfix_in_val(config,'ini',date,non_fix_path)
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    configT = get_nonfix_in_val('ini',date,non_fix_path)
    account_info = dict(configT['account_info'])
    pre_account_values = float(account_info['account_value'])
    print({'holding': len(holding), 'account_value': account_cap, 'cash': cash, 'equity_cap': cap.sum()})
    holding_series = pd.Series(holding)  # .drop('cash')
    if POSITION_CHANGING:
        send_message(['015664'],
                     f'FIX:{date}收盘现金+股票市值 {round(account_cap, 2)}，账面相对前日收益{round(account_cap - pre_account_values, 2)}，'
                     f'相对前日收益 {round((account_cap / pre_account_values - 1) * 100, 4)}%，持仓股票 {len(holding_series)} 只,'
                     f'其中0股{len(holding_series[holding_series < 100])}只，持仓市值 {round(cap.sum(), 2)}， 剩余现金 {round(cash, 2)}')
    else:
        send_message(['015664', '003186', '016385', '015836', '011669'],
                     f'FIX:{date}收盘现金+股票市值 {round(account_cap, 2)}，账面相对前日收益{round(account_cap - pre_account_values, 2)}，'
                     f'相对前日收益 {round((account_cap / pre_account_values - 1) * 100, 4)}%，持仓股票 {len(holding_series)} 只,'
                     f'其中0股{len(holding_series[holding_series < 100])}只，持仓市值 {round(cap.sum(), 2)}， 剩余现金 {round(cash, 2)}')
    lm.sendMessage(str(dict(T_plus_1_conf)))


def get_deal_detatil(date, record):
    buy, sell = record[record['类型'].eq('当日买入')].set_index(['证券代码', 'buy_signal_time']), record[record['类型'].eq('当日卖出')].set_index(['证券代码', 'sell_signal_time'])
    buy['委托量'], sell['委托量'] = np.nan, np.nan
    # summary = pd.read_pickle(path_conf['daily_out_path']+'%d.pkl'%date)
    stk_list = list(set(buy.index.levels[0]).union(set(sell.index.levels[0])))
    if not stk_list:
        return pd.DataFrame()
    minute_close = get_minute_1factor('close', start_datetime=date, end_datetime=date, code_list=[int(x[:-3]) for x in stk_list])
    minute_vol = get_minute_1factor('vol', start_datetime=date, end_datetime=date, code_list=[int(x[:-3]) for x in stk_list])

    # minute_close = get_minute_pickle('close',date_list=get_date_range(20210601,date), code_list=[int(x[:-3]) for x in stk_list]).loc[[date]]
    # minute_vol = get_minute_pickle('volume',date_list=get_date_range(20210601,date), code_list=[int(x[:-3]) for x in stk_list]).loc[[date]]
    vwap_30min = (minute_close * minute_vol).rolling(30).sum() / minute_vol.rolling(30).sum()
    vwap_30min = vwap_30min.shift(-29).swaplevel(0, 1).loc[bar_list].swaplevel(0, 1)
    vwap_30min.columns = vwap_30min.columns.map(trans_int2windcode)
    vwap_30min.index = [x[0] * 10000 + x[1] for x in vwap_30min.index.tolist()]
    vwap_30min = vwap_30min.stack().swaplevel(0, 1)
    buy['vwap'] = vwap_30min.loc[buy.index]
    sell['vwap'] = vwap_30min.loc[sell.index]
    buy['调仓收益'] = 1 - buy['成交价格'] / buy['vwap']
    sell['调仓收益'] = sell['成交价格'] / sell['vwap'] - 1

    for time_point in bar_list:
        if os.path.exists(f'{non_fix_output_path}/{date}/{time_point}_summary.pkl'):
            summary = pd.read_pickle(f'{non_fix_output_path}/{date}/{time_point}_summary.pkl')
        else:
            continue
        buy_order = summary['buy_order_record']  # [time_point]
        sell_order = summary['sell_order_record']  # [time_point]
        for each in buy_order.index:
            buy.loc[(each, date * 10000 + time_point), '委托量'] = buy_order[each]
        for each in sell_order.index:
            sell.loc[(each, date * 10000 + time_point), '委托量'] = sell_order[each]
    buy.index.names = ['证券代码', '委托时间']
    sell.index.names = ['证券代码', '委托时间']
    deal_detail = pd.concat([buy, sell]).drop(['buy_signal_time', 'sell_signal_time'], axis=1)
    deal_detail = deal_detail[['类型', '委托量', '累计成交数量', '成交价格', 'vwap', '调仓收益']].rename(columns={'累计成交数量': '实际成交量'}).reset_index()
    deal_detail['委托时间'] = (deal_detail['委托时间'] % 10000).astype(int)
    deal_detail['完成率'] = deal_detail['实际成交量'] / deal_detail['委托量']
    return deal_detail


def get_holding_930(date, final_total_holding, cash_added=0, div_cash=0, holding_added=pd.Series()):
    sub_output_path = f'{non_fix_output_path}/out_930/'
    path_for_930 = non_fix_930_path
    summary = pd.read_pickle(f'{sub_output_path}{date}.pkl')
    holding = summary['barly_holding_info'][1000]
    buy_time_info = summary['buy_time_info']
    if not os.path.exists(f'{path_for_930}{date}/'):
        os.mkdir(f'{path_for_930}{date}/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyIn/'):
        os.mkdir(f'{path_for_930}{date}/StrategyIn/')
    if not os.path.exists(f'{path_for_930}{date}/StrategyOut/'):
        os.mkdir(f'{path_for_930}{date}/StrategyOut/')
    holding = holding.set_index('Symbol')  # ['NetPosition']
    holding.loc[holding_added.index, 'NetPosition'] += holding_added
    holding.loc[holding_added.index, 'SellAvailable'] += holding_added
    holding[['NetPosition', 'SellAvailable']] = round(holding[['NetPosition', 'SellAvailable']]).astype(int)

    holding['buy_cost'] = (holding['TotalBuyAmount'] / final_total_holding['TotalBuyAmount']).fillna(0) * final_total_holding['buy_cost']
    holding['sell_cost'] = (holding['TotalSellAmount'] / final_total_holding['TotalSellAmount']).fillna(0) * final_total_holding['sell_cost']

    pre_930_holding = pd.read_pickle(f'{path_for_930}{get_pre_trade_date(date)}/StrategyOut/holding{get_pre_trade_date(date)}.pkl')
    holding = holding[((holding['NetPosition'] > 0) + (holding['TotalSellAmount'] > 0)) > 0]
    holding_930 = summary['barly_holding_info'][930].set_index('Symbol').loc[holding.index]
    holding_930.loc[holding_added.index, 'NetPosition'] += holding_added
    holding_930.loc[holding_added.index, 'SellAvailable'] += holding_added
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE', 'S_DQ_PRECLOSE'],
                               S_INFO_WINDCODE=holding.index.tolist(), TRADE_DT=[str(date), str(get_pre_trade_date(date))])
    # div_info = getEXRightDividend()
    # div_info['code'] = div_info['code'].apply(trans_int2windcode)
    # div_info = div_info[div_info['code'].isin(pre_930_holding.keys()) & div_info['date'].eq(today)]
    if len(close) > 0:
        pre_close = close.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_PRECLOSE').sort_index()
        close = close.pivot_table(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE').sort_index()
        detail = pd.DataFrame({
            '昨收价': pre_close.iloc[-1],
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

        close_minute = get_minute_1factor('close', code_list=detail.index.tolist(), start_datetime=date, end_datetime=date).loc[date].loc[930:959]
        #
        vol = get_minute_1factor('vol', code_list=detail.index.tolist(), start_datetime=date, end_datetime=date).loc[date].loc[930:959]
        # close_minute = get_minute_pickle('close', code_list=list(map(trans_windcode2int,detail.index.tolist())),date_list=get_date_range(20210601,date)).loc[date].loc[930:959]
        # vol = get_minute_pickle('volume', code_list=list(map(trans_windcode2int,detail.index.tolist())),date_list=get_date_range(20210601,date)).loc[date].loc[930:959]
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
        detail.loc[list(summary['sell_order_record'][930].keys()), '下单量'] = -1 * summary['sell_order_record'][930]
        detail.loc[list(summary['buy_order_record'][930].keys()), '下单量'] = summary['buy_order_record'][930]
        detail['完成率'] = detail['量'] / detail['下单量']
        detail['tag'] = ''
        detail.loc[list(summary['buy_order_record'][930].keys()), 'tag'] = '当日买入'
        detail.loc[list(summary['sell_order_record'][930].keys()), 'tag'] = '当日卖出'

    else:
        detail = pd.DataFrame(columns=['tag'])

    if not os.path.exists(f'/data/user/015664/AFuckingTrigger/对比930/{date}/'):
        os.makedirs(f'/data/user/015664/AFuckingTrigger/对比930/{date}/')
    detail.sort_values('tag').to_excel(f'/data/user/015664/AFuckingTrigger/对比930/{date}/逐笔收益930_{date}.xlsx')
    if not POSITION_CHANGING:
        send_file(['015664', '015836', '003186'], f'/data/user/015664/AFuckingTrigger/对比930/{date}/逐笔收益930_{date}.xlsx')
    else:
        send_file(['015664'], f'/data/user/015664/AFuckingTrigger/对比930/{date}/逐笔收益930_{date}.xlsx')
    left_cash = pre_930_holding['cash'] - holding['TotalBuyAmount'].sum() + holding['TotalSellAmount'].sum() - holding['buy_cost'].sum() - holding['sell_cost'].sum()
    holding_df = holding.copy()
    holding = holding['NetPosition']
    holding = dict(holding[holding > 0])

    for each in holding:
        if each not in buy_time_info:
            buy_time_info[each] = (date, 930)

    buy_time_info_key = list(buy_time_info.keys())
    for each in buy_time_info_key:
        if each not in holding:
            buy_time_info.pop(each)

    holding['cash'] = left_cash + cash_added + div_cash
    pd.to_pickle(holding, f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    pd.to_pickle(buy_time_info, f'{path_for_930}{date}/StrategyOut/buy_time_info{date}.pkl')
    if set(buy_time_info.keys()) != (set(buy_time_info.keys()) & set(holding.keys())):
        raise Exception('Buy time info and holding are not match')

    return holding_df, left_cash


def daily_initial_generation930(T_plus_1_date, date, barly_max_buy, stk_min_amt, per_signal_ratio, order_ratio):
    path_for_930 = non_fix_930_path
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
    if POSITION_CHANGING:
        send_message(['015664'], f'930 : {date}收盘现金+股票市值 {account_cap}，'
        f'相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
        f'收益金额{account_cap - pre_account_values}，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
    else:
        send_message(['015664', '003186', '016385', '015836', '011669'], f'930 : {date}收盘现金+股票市值 {account_cap}，'
        f'相对前日收益 {((account_cap / pre_account_values - 1) * 100)}%,'
        f'收益金额{account_cap - pre_account_values}，持仓股票 {len(holding)} 只，持仓市值 {cap.sum()}， 剩余现金 {cash}')
    send_message(['015664'], f'930:{strategy_init}')


def get_info(date, port_id):
    local_config_path = non_fix_path
    morning_portfolio = pd.read_excel(f'{morning_path}综合信息查询_组合证券{date}_516.xls')
    if os.path.exists(f'{afternoon_path}综合信息查询_组合证券_{date}.xls'):
        print('read afternoot from 011477')
        afternoon_portfolio = pd.read_excel(f'{afternoon_path}综合信息查询_组合证券_{date}.xls')
    elif os.path.exists(f'{local_config_path}restrict_list/{date}/综合信息查询_组合证券.xls'):
        afternoon_portfolio = pd.read_excel(f'{local_config_path}restrict_list/{date}/综合信息查询_组合证券.xls')
        print('read afternoon file from 800319')
    else:
        raise Exception('No Afternoon file exist')
    if os.path.exists(f'{trading_record_path}综合信息查询_委托流水_{date}_EM.xls'):
        trading_record = pd.read_excel(f'{trading_record_path}综合信息查询_委托流水_{date}_EM.xls')
    else:
        trading_record = pd.read_excel(f'{local_config_path}restrict_list/{date}/综合信息查询_委托流水.xls')

    morning_portfolio = format_df(morning_portfolio, port_id)
    afternoon_portfolio = format_df(afternoon_portfolio, port_id)
    trading_record = format_df(trading_record, port_id)
    return morning_portfolio, afternoon_portfolio, trading_record

def get_buy_time_info(date,div_info=None):
    if div_info is None:
        div_info = pd.DataFrame()
    summary = pd.read_pickle(f'{non_fix_output_path}/{date}/final_summary.pkl')
    holding_info = pd.read_pickle(f'{non_fix_output_path}{date}/last_bar_holding.pkl')
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
    extra = set(holding.keys()) - set(buy_time_info.keys()) - set(['cash'])
    if extra:
        raise Exception(f'存在无buy time info 的持仓{extra}')
    # pd.to_pickle(buy_time_info, f'{buy_time_info_path}{date}.pkl')
    save_nonfix_in_val(buy_time_info,'left_holding_bar',date,non_fix_path)

def AfterHoursStat(pre_date, today, T_plus_1_day, portfolio, cash_add, actual_all_cash, cash_add_930):
    start_cash = get_nonfix_in_val('holding_info',today,non_fix_path)['cash']

    ratio = get_nonfix_in_val('ratio',today,non_fix_path)

    morning_portfolio, afternoon_portfolio, trading_record = get_info(today, portfolio)
    _, pre_afternoon_holding, _ = get_info(pre_date, portfolio)
    div_info = getEXRightDividend()
    div_info['code'] = div_info['code'].apply(trans_int2windcode)
    holding = afternoon_portfolio[afternoon_portfolio['持仓'] > 0]
    holding_div_info = div_info[div_info['code'].isin(morning_portfolio.index) & div_info['date'].eq(today)].set_index('code')

    extra_cash = (pre_afternoon_holding['持仓'] * holding_div_info['payoutRatio']).fillna(0)
    extra_holding = (pre_afternoon_holding['持仓'] * holding_div_info['shareRatio']).fillna(0)

    extra_holding_930, extra_holding_fix = (extra_holding * ratio['bar_930']).fillna(0), (extra_holding * ratio['bar_7']).fillna(0)
    extra_cash_930, extra_cash_fix = (extra_cash * ratio['bar_930']).sum(), (extra_cash * ratio['bar_7']).sum()

    morning930_portfolio, morning_fix_portfolio = morning_portfolio['持仓'] * ratio['bar_930'], morning_portfolio['持仓'] * ratio['bar_7']
    final_total_holding = afternoon_portfolio[['持仓', '当日买金额(净价)', '当日卖金额(净价)', '当日买费用', '当日卖费用']].rename(columns={
        '持仓': 'NetPosition', '当日买金额(净价)': 'TotalBuyAmount', '当日卖金额(净价)': 'TotalSellAmount', '当日买费用': 'buy_cost', '当日卖费用': 'sell_cost'
    })
    final_holding_930, cash_930 = get_holding_930(today, final_total_holding, cash_added=cash_add_930, div_cash=extra_cash_930,
                                                  holding_added=extra_holding_930[extra_holding_930 > 0])
    daily_initial_generation930(T_plus_1_date=get_pre_trade_date(today, -1), date=today, barly_max_buy=barly_max_buy930, stk_min_amt=0.2, per_signal_ratio=0.005, order_ratio=0.1)

    final_fix_holding = final_total_holding - final_holding_930.drop('SellAvailable', axis=1).reindex(final_total_holding.index).fillna(0)
    pd.to_pickle(final_fix_holding.reset_index().rename(columns={'证券代码':'Symbol'}),f'{non_fix_output_path}{date}/last_bar_holding.pkl')
    final_fix_holding = final_fix_holding.rename(columns={
        'NetPosition': '持仓', 'TotalBuyAmount': '当日买金额(净价)', 'TotalSellAmount': '当日卖金额(净价)', 'buy_cost': '当日买费用', 'sell_cost': '当日卖费用'
    })
    final_fix_holding['市值'] = afternoon_portfolio['市值'] * (final_fix_holding['持仓'] / afternoon_portfolio['持仓'].replace(0, np.nan)).sort_values().fillna(0)
    holding, pre_holding, buy_time_info, sell_time_info, afternoon_holding = get_holding_and_buy_time(morning_fix_portfolio, final_fix_holding,
                                                                                                      trading_record[trading_record['委托时间'] > '10:00:00'],
                                                                                                      today, portfolio, start_cash + extra_cash_fix.sum())

    actual_cash = actual_all_cash - cash_930 - extra_cash_930
    if round(holding['cash'] - actual_cash) != 0:
        calc_cash = holding['cash']
        lm.sendMessage(f'{today} 结算资金{calc_cash}和实际资金{actual_cash}不一致')
    holding['cash'] = actual_cash
    holding['cash'] += cash_add
    save_nonfix_in_val(holding,'holding_info',today,non_fix_path)
    get_buy_time_info(date)

    record = calc_profit_decomposition(today, pd.Series(holding).drop('cash'), pre_holding,
                                                      buy_time_info, sell_time_info, afternoon_holding)
    # holding_series = pd.Series(holding).drop('cash')
    zero_stock = afternoon_portfolio[(afternoon_portfolio['持仓'] < 100) & (afternoon_portfolio['持仓'] > 0)]['持仓']
    zero_stock.index.names = ['证券代码']
    if len(zero_stock) > 0:
        pd.DataFrame({'持仓数量': zero_stock}).to_excel(f'/data/user/015664/AFuckingTrigger/share/zero_stock/{today}.xlsx')
        # send_message(['015664','015390'],f'EnsembleMontitor 今日有0股，详细信息已保存至 /data/user/015664/AFuckingTrigger/share/zero_stock/{today}.xlsx')

    daily_initial_generation(T_plus_1_date=T_plus_1_day, date=today, barly_max_buy=barly_maxbuy, stk_min_amt=0.2, per_signal_ratio=0.005,
                             order_ratio=0.1, afternoon_holding=afternoon_holding, portfolio=portfolio)

    deal_detail = get_deal_detatil(today, record)
    local_config_path = non_fix_path
    if not os.path.exists(f'/data/user/015664/AFuckingTrigger/实盘/{today}/'):
        os.mkdir(f'/data/user/015664/AFuckingTrigger/实盘/{today}/')
    if os.path.exists(f'{afternoon_path}综合信息查询_组合证券_{today}.xls'):
        shutil.copy(f'{afternoon_path}综合信息查询_组合证券_{today}.xls',
                    f'/data/user/015664/AFuckingTrigger/实盘/{today}/综合信息查询_组合证券_{today}.xls')
    else:
        shutil.copy(f'{local_config_path}restrict_list/{today}/综合信息查询_组合证券.xls',
                    f'/data/user/015664/AFuckingTrigger/实盘/{today}/综合信息查询_组合证券_{today}.xls')
    if os.path.exists(f'{trading_record_path}综合信息查询_委托流水_{today}_EM.xls'):
        shutil.copy(f'{trading_record_path}综合信息查询_委托流水_{today}_EM.xls',
                    f'/data/user/015664/AFuckingTrigger/实盘/{today}/综合信息查询_委托流水_{today}_EM.xls')
    else:
        shutil.copy(f'{local_config_path}restrict_list/{today}/综合信息查询_委托流水.xls',
                    f'/data/user/015664/AFuckingTrigger/实盘/{today}/综合信息查询_委托流水_{today}_EM.xls')

    with pd.ExcelWriter(f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx') as writer:
        deal_detail.to_excel(writer, sheet_name='委托成交明细')
        record.to_excel(writer, sheet_name='收益明细')
    writer.close()
    if not POSITION_CHANGING:
        send_file(['015664', '003186', '015836'], f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx')
    else:
        send_file(['015664'], f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx')


def out_transfer_file(date, account):
    # holding_info_path, local_config_path = path_conf['holding_info_path'], path_conf['local_config_path']
    path_for_930 = non_fix_930_path
    holding_930 = pd.read_pickle(f'{path_for_930}{date}/StrategyOut/holding{date}.pkl')
    holding_930.pop('cash')
    holding_930 = pd.Series(holding_930)
    holding = get_nonfix_in_val('holding_info',get_pre_trade_date(date,-1),non_fix_path)
    holding.pop('cash')
    holding = pd.Series(holding)
    union_stk_list = list(set(holding_930.index).union(set(holding.index)))
    holding = holding.reindex(union_stk_list).fillna(0) + holding_930.reindex(union_stk_list).fillna(0)

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
    # transfer.set_index('编号').to_excel(f'{local_config_path}transfer_file/in{date}_{account}.xlsx')
    # if not POSITION_CHANGING:
    #     send_file(['015664'], f'{local_config_path}transfer_file/in{date}_{account}.xlsx')


def out_order(date):
    if not os.path.exists(f'/data/user/015664/share/{date}/'):
        os.mkdir(f'/data/user/015664/share/{date}/')

    # summary = pd.read_pickle(path_conf['daily_out_path']+'%d.pkl'%date)

    for time_point in bar_list:
        if os.path.exists(f'{non_fix_output_path}/{date}/{time_point}_summary.pkl'):
            summary = pd.read_pickle(f'{non_fix_output_path}/{date}/{time_point}_summary.pkl')
        else:
            continue
        order = pd.DataFrame({'Buy': summary['buy_order_record'], 'Sell': summary['sell_order_record']}).fillna(0)
        order.index.names = ['Symbol']
        pd.to_pickle(order, f'/data/user/015664/share/{date}/volume_df_{date}{time_point}.pkl')
    # send_message(['011477','015664'],f'{date} EnsembleMonitor调仓指令文件已存至 /data/user/015664/share/{date}/')


def update_restrict_list(date):
    local_config_path = non_fix_path
    available_pool = pd.read_excel(f'{local_config_path}restrict_list/{date}/自营交易证券池.xls')
    black_list = pd.read_excel(f'{local_config_path}restrict_list/{date}/自营黑名单.xls')
    shutil.copy(f'{local_config_path}restrict_list/{date}/自营交易证券池.xls', f'/data/group/800442/800319/strategy_local_path/restrict_list/证券池{date}.xls')
    shutil.copy(f'{local_config_path}restrict_list/{date}/自营黑名单.xls', f'/data/group/800442/800319/strategy_local_path/restrict_list/黑名单{date}.xls')
    black_list = black_list[black_list['证券类别'] == '股票']
    available_pool = available_pool[available_pool['交易市场'].isin(['上交所A', '深交所A'])]

    black_list = black_list['证券代码'].astype(int)  # .apply(trans_int2windcode)
    available_pool = available_pool['证券代码'].astype(int)  # .apply(trans_int2windcode)

    all_pool = get_stock_list(date)
    restrict_list = (set(all_pool) - set(available_pool)).union(set(black_list))
    max_day = max(list(extra_restrict_list.keys()))
    restrict_list = restrict_list.union(set(extra_restrict_list[max_day]))
    restrict_list = set(list(map(trans_int2windcode, restrict_list)))

    # extra_pool = pd.read_excel(f'/data/group/800319/strategy_local_path3/restrict_list/{date}/解禁池.xlsx',index_col=0)
    # extra_pool = extra_pool[extra_pool['是否解除禁买'].apply(lambda x : '是' not in str(x))]
    # from dataApi.getData import trans_windcode2int
    # restrict_list = restrict_list.union(set(extra_pool.index.map(trans_windcode2int).map(trans_int2windcode).tolist()))
    lm.sendMessage(f'不可交易名单长度  {len(restrict_list)}')
    save_nonfix_in_val(restrict_list,'restrict_list',date,non_fix_path)
    # pd.to_pickle(restrict_list, f'{local_config_path}restrict_list.pkl')


# path_conf = get_path_conf('/data/group/800319/strategy_local_path3_validation/')
non_fix_path = '/data/group/800319/strategy_local_path3/'
non_fix_930_path = f'{non_fix_path}FolderFor930/'
non_fix_in_path = f'{non_fix_path}daily_input/'
non_fix_output_path = f'{non_fix_path}daily_output/'

morning_path = '/data/user/011477/order/O32/morning/'
afternoon_path = '/data/user/011477/order/O32/afternoon/'
trading_record_path = '/data/user/011477/order/O32/514/trade/'
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
from Tool.FTPTransfer import transfer_dir_from_FTP60
from dataApi.tradeDate import get_recent_trade_date


def main(actual_cash):
    today = get_recent_trade_date()  # int(datetime.date.today().strftime('%Y%m%d'))
    print(today)
    os.system(f'cp -r /data/xtrader/800442/StrategyOutput/{today}*  {non_fix_output_path}')
    os.system(f'cp -r /data/xtrader/800442/StrategyOutput/out_930/{today}*  {non_fix_output_path}/out_930/')
    transfer_dir_from_FTP60(f'/data/group/800319/strategy_local_path3/restrict_list/{today}/', file_path=f'015664/股票池/{today}/')
    transfer_dir_from_FTP60(f'/data/group/800319/strategy_local_path3/restrict_list/{get_pre_trade_date(today)}/',
                            file_path=f'015664/股票池/{get_pre_trade_date(today)}/')
    pre_date = get_pre_trade_date(today, 1)
    T_plus_1_day = get_pre_trade_date(today, -1)
    portfolio = '201001'
    if today in cash_flow:
        cash_add, cash_add_930 = cash_flow[today]
    else:
        cash_add = 0  # 30000000#-100000000-7925804.88
        cash_add_930 = 0  # 4500000#-15000000-173508.90871492773
    AfterHoursStat(pre_date, today, T_plus_1_day, portfolio, cash_add, actual_cash, cash_add_930=cash_add_930)
    # out_transfer_file(today, int(portfolio))
    out_order(today)
    update_restrict_list(today)


cash_flow = {
    20220526:[48000000,6300000]
}

extra_restrict_list = {
                       20220401: ['002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
                                  '600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
                                  '600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
                                  '601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
                                  '600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ','600057.SH'],
    20220428: [
'002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
'600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
'600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
'601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
'600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ', '600057.SH', '300202.SZ',
        '300526.SZ','300038.SZ'
    ],

20220506: [
'002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
'600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
'600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
'601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
'600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ', '600057.SH', '300202.SZ',
        '300526.SZ','300038.SZ'
    ],
20220526: [
'002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
'600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
'600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
'601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
'600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ', '600057.SH', '300202.SZ',
        '300526.SZ','300038.SZ','301163.SZ','000957.SZ'
    ],

20220609: [
'002682.SZ', '603176.SH', '300427.SZ', '300362.SZ', '002432.SZ', '600880.SH', '300437.SZ', '600078.SH', '603032.SH', '300052.SZ', '301089.SZ',
'600112.SH', '300688.SZ', '600145.SH', '000537.SZ', '001317.SZ', '600218.SH', '600856.SH', '605286.SH', '600306.SH', '601798.SH', '600071.SH',
'600995.SH', '300612.SZ', '300412.SZ', '600396.SH', '000812.SZ', '002750.SZ', '603123.SH', '605333.SH', '603169.SH', '600275.SH', '600698.SH',
'601068.SH', '300350.SZ', '002761.SZ', '300649.SZ', '603316.SH', '600146.SH', '601789.SH', '603122.SH', '600078.SH', '000815.SZ', '600190.SH',
'600083.SH', '600734.SH', '600090.SH', '600275.SH', '600818.SH', '600056.SH', '603538.SH', '600077.SH', '002613.SZ', '600057.SH', '300202.SZ',
        '300526.SZ','300038.SZ','301163.SZ','000957.SZ','600890.SH','600091.SH','600652.SH','600209.SH'
    ],
}

max_buy_change = {
    # 20220331:[0,0],
    # 20220418:[100,100]
    20220422:[2,2],
    20220425:[0,0],
    20220525:[100,0],
}


date =get_recent_trade_date()

target_date = list(filter(lambda x : x<=date,list(max_buy_change.keys())))
if target_date:
    target_date = max(max_buy_change.keys())
    barly_maxbuy, barly_max_buy930 = max_buy_change[target_date]
else:
    barly_maxbuy, barly_max_buy930 = 100, 100
print(f'-------------------max_buy {barly_maxbuy,barly_max_buy930}----------------------')
# POSITION_CHANGING = False
POSITION_CHANGING = True
# import time
# time.sleep(60*)
if __name__ == "__main__":
    # update_restrict_list(20220303)
    main(6994794.53+142786.6)#20220610
    # main(6994794.53+44904830.27)#20220607
    # main(6994794.53+48592254.48)#20220607
    # main(6994794.53+49985507.11)#20220607
    # main(6994794.53+47669605.18)#20220606
    # main(6994794.53+21567033.84)#20220602
    # main(6994794.53+46694672.9)#20220601
    # main(6994794.53+26011132.27)#20220531
    # main(6994794.53+39998445.3)#20220530
    # main(6994794.53+44746948.05)#20220527
    # main(2608239.9+20101.08+66453.55)
    # main(2608239.9+20101.08)
    # main(2608239.9)
