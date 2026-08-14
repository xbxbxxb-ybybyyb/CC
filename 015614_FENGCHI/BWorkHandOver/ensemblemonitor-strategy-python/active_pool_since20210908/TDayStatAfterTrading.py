# @Time : 2021/3/3 15:17
# @Author : Zhichen Lu
# @File : statDealRecord.py

import pandas as pd
# from online_conf import daily_out_path,buy_time_info_path,local_config_path
from dataApi.getData import get_minute_1factor
from dataApi.tradeDate import get_pre_trade_date,get_date_range
import os
from xquant.factordata import FactorData
from active_pool_since20210908.simple_tool import get_path_conf
from dataApi.sendInfo import send_file,send_message

config_path = get_path_conf('/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')
indi_list = "daily_out_path,buy_time_info_path,local_config_path"
indi_list = indi_list.split(',')
indi_list = [x.strip() for x in indi_list]
daily_out_path,buy_time_info_path,local_config_path =\
[config_path[x] for x in indi_list]

s = FactorData()



def profit_stat(stat_date,buy_cost=0,sell_cost=0):
    pre_date = get_pre_trade_date(stat_date)
    holding_info = {}
    pre_time,pre_holding = None,None
    sold_list = []
    buy_time_info = pd.read_pickle(buy_time_info_path+'%d.pkl'%stat_date)
    pre_day_buy_time_info = pd.read_pickle(buy_time_info_path+'%d.pkl'%pre_date)
    stk_list = list(set([x for x in buy_time_info]).union(set([x for x in pre_day_buy_time_info])))
    close = s.get_factor_value('WIND_AShareEODPrices', factor_names=['TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_PRECLOSE', 'S_INFO_WINDCODE'], S_INFO_WINDCODE=stk_list,
                               TRADE_DT=[str(stat_date),str(pre_date)]).reindex(['TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_PRECLOSE', 'S_INFO_WINDCODE'],axis=1)
    pre_close = close.pivot_table(values='S_DQ_PRECLOSE',index='TRADE_DT',columns='S_INFO_WINDCODE').reindex([str(stat_date),str(pre_date)])
    close = close.pivot_table(values='S_DQ_CLOSE',index='TRADE_DT',columns='S_INFO_WINDCODE').reindex([str(stat_date),str(pre_date)])

    pre_close.index = pre_close.index.astype(int)
    close.index = close.index.astype(int)

    position_change = {}

    record = pd.DataFrame()
    holding_info = pd.read_pickle(f'{daily_out_path}{stat_date}.pkl')['barly_holding_info']

    if os.path.exists(f'{daily_out_path}{stat_date}/last_bar_holding.pkl'):
        fake_output = pd.read_pickle(f'{daily_out_path}{stat_date}/last_bar_holding.pkl')
        fake_output.index.names = ['Symbol']
    else:
        fake_output = pd.read_pickle(f'{local_config_path}fake_barly_info/{stat_date}/1500.pkl')

    holding_info[1500] = fake_output.reset_index()
    for time_point in [1000,1030,1100,1300,1330,1400,1430,1500]:
        holding_info[time_point] = holding_info[time_point].set_index('Symbol')
        if not pre_holding is None:
            holding_change = holding_info[time_point]['NetPosition'] - pre_holding['NetPosition']
            sold_amt_change = holding_info[time_point]['TotalSellAmount'] - pre_holding['TotalSellAmount']
            bought_amt_change = holding_info[time_point]['TotalBuyAmount'] - pre_holding['TotalBuyAmount']

            sold_vol = -1*holding_change[holding_change < 0]
            sold_price = sold_amt_change.loc[sold_vol.index]/holding_change.loc[sold_vol.index].apply(abs)
            sold_record = pd.DataFrame({'量':sold_vol,'成交价':sold_price,'昨收价':pre_close.loc[stat_date,sold_vol.index]})
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

        zero_stock_sell_record = pd.DataFrame({'量':zero_stock['NetPosition'],'成交价':temp_close.loc[zero_stock.index],'昨收价':pre_close.loc[stat_date,zero_stock.index]})
        zero_stock_sell_record['贡献收益'] = zero_stock_sell_record['量']*(zero_stock_sell_record['成交价']*(1-sell_cost)-zero_stock_sell_record['昨收价'])
        zero_stock_sell_record['交易时间'] = 1500
        zero_stock_sell_record['类型'] = '清零股'
    else:
        zero_stock_sell_record = pd.DataFrame()

    holding_over_night = pd.DataFrame({
        '量':holding_info[1500].loc[holding_over_night,'NetPosition'],
        '昨收价':pre_close.loc[stat_date,holding_over_night],
        '今收价':close.loc[stat_date,holding_over_night],
    })
    holding_over_night['类型'] = '隔夜持仓'
    holding_over_night['贡献收益'] = holding_over_night['量']*(holding_over_night['今收价']-holding_over_night['昨收价'])
    holding_over_night.index.names = ['Symbol']
    zero_stock_sell_record.index.names = ['Symbol']
    record = pd.concat([record,zero_stock_sell_record.reset_index(),holding_over_night.reset_index()])
    send_message(['015664'],f'收益分解表计算收益'+str(record['贡献收益'].sum()))
    return record

def out_profit(day,reseive_user=[]):
    out_path = f'/{local_config_path}/逐笔收益统计/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    if not os.path.exists(f'{out_path}{day}/'):
        os.mkdir(f'{out_path}{day}/')
    # all_record = get_all_trading_record(day)
    profit_record = profit_stat(day)
    out_file = f'{out_path}{day}/活跃股票池跟踪_成交_收益信息统计{day}.xlsx'
    with pd.ExcelWriter(out_file) as writer:
        # all_record.to_excel(writer,sheet_name='成交信息统计')
        profit_record.to_excel(writer,sheet_name='逐笔收益统计')
    writer.close()
    send_file(reseive_user,out_file)
    print(day)

# import datetime
# day = int(datetime.date.today().strftime('%Y%m%d'))#20210310
# out_profit(day)