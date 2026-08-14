# @Time : 2021/3/3 15:17
# @Author : Zhichen Lu
# @File : statDealRecord.py

import pandas as pd
# from online_conf import daily_out_path,buy_time_info_path
from dataApi.getData import get_minute_1factor
from dataApi.tradeDate import get_pre_trade_date
import os,datetime
from xquant.factordata import FactorData
from ExtraTools import get_path_conf



s = FactorData()

def get_all_trading_record(date):
    summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
    if os.path.exists(f'{daily_out_path}{date}/last_bar_holding.pkl'):
        fake_holding = pd.read_pickle(f'{daily_out_path}{date}/last_bar_holding.pkl')
        fake_holding.index.names = ['Symbol']
    else:
        fake_holding = pd.read_pickle(f'{daily_out_path}{date}_fake_for_final.pkl')['barly_holding_info'][1000].set_index('Symbol')

    pre_time = None
    pre_holding = None

    all_record = pd.DataFrame()
    for time_point in [1000,1030,1100,1300,1330,1400,1430,1500]:
        if time_point==1500:
            holding_info = fake_holding
        else:
            holding_info = summary['barly_holding_info'][time_point].set_index('Symbol')
        if not pre_time is None:
            buy_order, sell_order = summary['buy_order_record'][pre_time], summary['sell_order_record'][pre_time]
            trading_stk = buy_order.index.tolist() + sell_order.index.tolist()
            dealed_info = holding_info.loc[trading_stk,['NetPosition','TotalBuyAmount', 'TotalSellAmount']] - pre_holding.loc[trading_stk,['NetPosition','TotalBuyAmount', 'TotalSellAmount']]
            sell_info = pd.DataFrame({'委托方向':'卖出',
                                      '委托时间': pre_time,
                                     '委托量':sell_order,
                                     '成交量':-1*dealed_info.loc[sell_order.index, 'NetPosition'],
                                     '成交价': -1 * dealed_info.loc[sell_order.index, 'TotalSellAmount'] / dealed_info.loc[sell_order.index, 'NetPosition']})
            buy_info = pd.DataFrame({
                '委托方向': '买入',
                '委托时间':pre_time,
                '委托量': buy_order,
                '成交量': dealed_info.loc[buy_order.index, 'NetPosition'],
                '成交价': dealed_info.loc[buy_order.index, 'TotalBuyAmount'] / dealed_info.loc[buy_order.index, 'NetPosition']
            })
            trading_record = pd.concat([buy_info,sell_info])
            trading_record['完成率'] = trading_record['成交量']/trading_record['委托量']

            vol = get_minute_1factor('vol', start_datetime=f'{date}{pre_time}', end_datetime=f'{date}{time_point}')#[:-1]
            close = get_minute_1factor('close', start_datetime=f'{date}{pre_time}', end_datetime=f'{date}{time_point}')#[:-1]

            trading_record['市场成交量'] = vol[5:].sum().rename(index={x:str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in vol.columns}).loc[trading_record.index]
            trading_record['委托量占市场成交量比'] = trading_record['委托量']/trading_record['市场成交量']
            trading_record['成交量占市场成交量比'] = trading_record['成交量']/trading_record['市场成交量']

            vwap = (vol[:-1].fillna(0) * close[:-1].fillna(method='pad')).sum() / vol[:-1].sum()
            vwap.index = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in vwap.index]
            trading_record['vwap'] = vwap.loc[trading_record.index]
            trading_record['相对vwap调仓收益'] = trading_record['成交价']/trading_record['vwap'] - 1
            trading_record.loc[buy_order.index,'相对vwap调仓收益'] *= -1
            all_record = all_record.append(trading_record)
        pre_time = time_point
        pre_holding = holding_info


    zero_stock = holding_info[(holding_info['NetPosition']>0)&(holding_info['NetPosition']<100)]
    if len(zero_stock)>0:
        close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=zero_stock.index.tolist(),
                                   TRADE_DT=[str(date)])
        close = close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']
        zero_stock_record = pd.DataFrame({
              '委托方向':'零股卖出',
              '委托时间': 1500,
             '委托量':zero_stock['NetPosition'],
             '成交量':zero_stock['NetPosition'],
             '成交价':close.loc[zero_stock.index]
        })
    else:
        zero_stock_record = pd.DataFrame()
    all_record = pd.concat([all_record,zero_stock_record])
    return all_record


def profit_stat(stat_date,buy_cost=0.0001,sell_cost=0.0011):
    pre_date = get_pre_trade_date(stat_date)
    holding_info = {}
    pre_time,pre_holding = None,None
    sold_list = []
    buy_time_info = pd.read_pickle(buy_time_info_path+'%d.pkl'%stat_date)
    pre_day_buy_time_info = pd.read_pickle(buy_time_info_path+'%d.pkl'%pre_date)
    stk_list = list(set([x for x in buy_time_info]).union(set([x for x in pre_day_buy_time_info])))
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=stk_list,
                               TRADE_DT=[str(stat_date),str(pre_date)])
    close = close.pivot_table(values='S_DQ_CLOSE',index='TRADE_DT',columns='S_INFO_WINDCODE')
    close.index = close.index.astype(int)

    # close = get_daily_1factor('close',date_list=[pre_date,stat_date])
    # close_adj = get_daily_1factor('close_badj',date_list=[pre_date,stat_date])
    # adj_info = close_adj/close_adj.loc[stat_date]
    # close = close.loc[stat_date]*adj_info
    # close.columns = [str(x).zfill(6)+'.SZ' if x<400000 else str(x)+'.SH' for x in close.columns]

    position_change = {}

    record = pd.DataFrame()
    holding_info = pd.read_pickle(f'{daily_out_path}{stat_date}.pkl')['barly_holding_info']

    if os.path.exists(f'{daily_out_path}{stat_date}/last_bar_holding.pkl'):
        fake_output = pd.read_pickle(f'{daily_out_path}{stat_date}/last_bar_holding.pkl')
        fake_output.index.names = ['Symbol']
    else:
        fake_output = pd.read_pickle(f'{daily_out_path}{stat_date}_fake_for_final.pkl')['barly_holding_info'][1000].set_index('Symbol')

    holding_info[1500] = fake_output.reset_index()
    for time_point in [1000,1030,1100,1300,1330,1400,1430,1500]:
        holding_info[time_point] = holding_info[time_point].set_index('Symbol')
        if not pre_holding is None:
            holding_change = holding_info[time_point]['NetPosition'] - pre_holding['NetPosition']
            sold_amt_change = holding_info[time_point]['TotalSellAmount'] - pre_holding['TotalSellAmount']
            bought_amt_change = holding_info[time_point]['TotalBuyAmount'] - pre_holding['TotalBuyAmount']

            sold_vol = -1*holding_change[holding_change < 0]
            sold_price = sold_amt_change.loc[sold_vol.index]/holding_change.loc[sold_vol.index].apply(abs)
            sold_record = pd.DataFrame({'量':sold_vol,'成交价':sold_price,'昨收价':close.loc[pre_date,sold_vol.index]})
            sold_record['贡献收益'] = sold_record['量']*(sold_record['成交价']*(1-sell_cost)-sold_record['昨收价'])
            sold_record['交易时间'] = pre_time
            sold_record['类型'] = '卖出'

            bought_vol = holding_change[holding_change>0]
            bought_price = bought_amt_change.loc[bought_vol.index]/holding_change.loc[bought_vol.index].apply(abs)
            bough_record = pd.DataFrame({'量':bought_vol,'成交价':bought_price,'今收价':close.loc[stat_date,bought_vol.index]})
            bough_record['贡献收益'] = bough_record['量']*(bough_record['今收价']-bough_record['成交价']*(1+buy_cost))
            bough_record['交易时间'] = pre_time
            bough_record['类型'] = '买入'
            record = pd.concat([record,bough_record.reset_index(),sold_record.reset_index()])
            position_change[pre_time] = holding_change
        pre_holding = holding_info[time_point].copy()
        pre_time = time_point

    holding_over_night = holding_info[time_point].loc[[x for x in buy_time_info]]
    holding_over_night = holding_over_night[holding_over_night['TotalBuyAmount']==0].index.tolist()

    zero_stock = pre_holding[(pre_holding['NetPosition']>0)&(pre_holding['NetPosition']<100)]
    # temp_close = get_minute_1factor('close', start_datetime=f'{stat_date}{time_point}', end_datetime=f'{stat_date}{time_point}').loc[(stat_date,time_point)]
    # temp_close.index = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in temp_close.index]
    if zero_stock.shape[0]>0:
        temp_close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=zero_stock.index.tolist(),
                                   TRADE_DT=[str(stat_date)])
        temp_close = temp_close.set_index('S_INFO_WINDCODE')['S_DQ_CLOSE']

        zero_stock_sell_record = pd.DataFrame({'量':zero_stock['NetPosition'],'成交价':temp_close.loc[zero_stock.index],'昨收价':close.loc[pre_date,zero_stock.index]})
        zero_stock_sell_record['贡献收益'] = zero_stock_sell_record['量']*(zero_stock_sell_record['成交价']*(1-sell_cost)-zero_stock_sell_record['昨收价'])
        zero_stock_sell_record['交易时间'] = 1500
        zero_stock_sell_record['类型'] = '清零股'
    else:
        zero_stock_sell_record = pd.DataFrame()

    holding_over_night = pd.DataFrame({
        '量':holding_info[1500].loc[holding_over_night,'NetPosition'],
        '昨收价':close.loc[pre_date,holding_over_night],
        '今收价':close.loc[stat_date,holding_over_night],
    })
    holding_over_night['类型'] = '隔夜持仓'
    holding_over_night['贡献收益'] = holding_over_night['量']*(holding_over_night['今收价']-holding_over_night['昨收价'])
    record = pd.concat([record,zero_stock_sell_record.reset_index(),holding_over_night.reset_index()])
    return record
import datetime
from dataApi.sendInfo import send_file
day = int(datetime.date.today().strftime('%Y%m%d'))#20210310
today = int(datetime.date.today().strftime('%Y%m%d'))
path_conf = get_path_conf(f'/data/group/800319/strategy_local_path_sim/strategy_local_path3_sim{today}/')
daily_out_path,buy_time_info_path = [path_conf[x] for x in 'daily_out_path,buy_time_info_path'.split(',')]

out_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/'
if not os.path.exists(f'{out_path}{day}/'):
    os.mkdir(f'{out_path}{day}/')
all_record = get_all_trading_record(day)
profit_record = profit_stat(day)
with pd.ExcelWriter(f'{out_path}{day}/成交_收益信息统计{day}.xlsx') as writer:
    all_record.to_excel(writer,sheet_name='成交信息统计')
    profit_record.to_excel(writer,sheet_name='逐笔收益统计')
writer.close()
send_file(['015664'],f'{out_path}{day}/成交_收益信息统计{day}.xlsx')