# @Time : 2021/3/8 9:31
# @Author : Zhichen Lu
# @File : stock_pool_analysis.py

import pandas as pd
from online_conf import local_config_path,daily_out_path,code_list_path
import os
from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range


s = FactorData()


def get_daily_stat(date_list):
    res = {}
    for date in date_list:
        summary = pd.read_pickle(f'{daily_out_path}{date}.pkl')
        code_list = pd.read_pickle(f'{code_list_path}{date}.pkl')
        signal_stk = set()
        for time_point in summary['signal']:
            signal_stk = signal_stk.union(set(summary['signal'][time_point].index))
        signal_stk = sorted(list(signal_stk))

        boughted_stk = pd.Series(summary['buy_time_info']).apply(lambda x : x[0]==date)
        boughted_stk = boughted_stk[boughted_stk].index.tolist()

        cap = s.get_factor_value('Basic_factor',factor_names=['a_mkt_cap'],mddate=[str(date)]).loc[str(date),'a_mkt_cap']
        amt = s.get_factor_value('Basic_factor',factor_names=['amt'],mddate=[str(date)]).loc[str(date),'amt']

        stat = {
            '全市场市值中位数':cap.median(),
            '股票池市值中位数':cap.loc[code_list].median(),
            '触发信号所涉及股票市值中位数':cap.loc[signal_stk].median(),
            '买入股票市值中位数':cap.loc[boughted_stk].median(),
            '股票池市值中位数在全市场的分位值':(cap<cap.loc[code_list].median()).sum()/cap.count(),
            '触发信号股票市值中位数在全市场的分位值':(cap<cap.loc[signal_stk].median()).sum()/cap.count(),
            '买入股票市值中位数在全市场的分位值':(cap<cap.loc[boughted_stk].median()).sum()/cap.count(),

            '全市场成交额中位数': amt.median(),
            '股票池成交额中位数': amt.loc[code_list].median(),
            '触发信号所涉及股票成交额中位数': amt.loc[signal_stk].median(),
            '买入股票成交额中位数': amt.loc[boughted_stk].median(),
            '股票池成交额中位数在全市场的分位值': (cap < cap.loc[code_list].median()).sum() / cap.count(),
            '触发信号股票成交额中位数在全市场的分位值': (amt < amt.loc[signal_stk].median()).sum() / amt.count(),
            '买入股票成交额中位数在全市场的分位值': (amt < amt.loc[boughted_stk].median()).sum()/ amt.count(),

            '触发信号涉及股票数':len(signal_stk),
            '买入股票数':len(boughted_stk)
        }
        res[date] = pd.Series(stat)


    return pd.DataFrame(res).T

date_list = get_date_range(20210222,20210308)
res = get_daily_stat(date_list[1:])
winda = s.get_factor_value('WIND_AIndexWindIndustriesEOD',S_INFO_WINDCODE=['881001.WI'],TRADE_DT=[str(x) for x in date_list]).rename(columns={'881001.WI':'万德全A'}).set_index('TRADE_DT')['S_DQ_CLOSE']
index = s.get_factor_value('Basic_factor',['000001.SH','000300.SH','000905.SH','000852.SH'],factor_names=['close'],mddate=[str(x) for x in date_list]).reset_index().pivot_table(index='mddate',columns='stock',values='close')
index = index.rename(columns={'000001.SH':'上证指数','000300.SH':'沪深300','000905.SH':'中证500','000852.SH':'中证1000'})
index['万德全A'] = winda
index.index = index.index.astype(int)
res = pd.concat([res,index.pct_change()[1:]],axis=1)
res.to_excel('/data/user/015664/AFuckingTrigger/限制买入和持仓/仿真回测线下跟踪/市值成交额统计.xlsx')

