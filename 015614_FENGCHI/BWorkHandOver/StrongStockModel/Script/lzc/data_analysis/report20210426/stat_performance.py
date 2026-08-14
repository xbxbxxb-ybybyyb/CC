# @Time : 2021/4/26 11:00
# @Author : Zhichen Lu
# @File : stat_performance.py
import pandas as pd
from online_conf import local_config_path,holding_info_path
from  dataApi.tradeDate import get_pre_trade_date
from dataApi.getData import get_daily_1factor,get_date_range,trans_int2windcode,trans_windcode2int
from dataApi.indName import sw_level2
from xquant.factordata import FactorData
import os
s = FactorData()
turnover_num = {}
turnover_cap = {}
signal_industry_count = {}
holding_industry_count = {}

date_list = get_date_range(20210414,20210423)
for date in date_list:
    # date = 20210414
    pre_date = get_pre_trade_date(date)
    holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    pre_holding = pd.read_pickle(f'{holding_info_path}{pre_date}.pkl')
    holding_over_stk = set(holding.keys()).intersection(pre_holding.keys())
    holding_over_stk.remove('cash')
    turnover_num[date] = 1 - len(holding_over_stk)/(len(pre_holding)-1)

    close = get_daily_1factor('close',[pre_date],code_list=list(filter(lambda x : x!='cash',list(pre_holding.keys()))))
    close.columns = close.columns.map(trans_int2windcode)
    close = close.loc[pre_date]
    cap = close * pd.Series(pre_holding).drop('cash')
    turnover_cap[date] = 1 - cap.loc[list(holding_over_stk)].sum()/cap.sum()

    holding.pop('cash')
    ret_decomposition = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{date}/成交明细及收盘持仓情况{date}.xlsx', sheet_name='收益明细')
    industry_info = get_daily_1factor('SW2', date_list=[date], code_list=list(set(ret_decomposition['证券代码'].apply(trans_windcode2int))))
    industry_info.columns = industry_info.columns.map(trans_int2windcode)
    industry_info = industry_info.loc[date].apply(lambda x: sw_level2[x])
    ret_decomposition['申万二级行业'] = ret_decomposition['证券代码'].apply(lambda x: industry_info[x])
    signal_industry_count[date] = ret_decomposition.groupby(['申万二级行业', '类型']).size().reindex(list(sw_level2)).fillna(0)
    holding_industry_count[date] = pd.DataFrame({'申万二级行业': pd.Series(industry_info).loc[list(holding.keys())]}).groupby('申万二级行业').size()

turn_over = pd.DataFrame({'换手率(数量)':turnover_num,'换手率(市值)':turnover_cap})
# turn_over.to_excel('换手率.xlsx')

signal_industry_count = pd.DataFrame(signal_industry_count).fillna(0).T
holding_industry_count = pd.DataFrame(holding_industry_count).fillna(0).T

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/汇报20210426/换手率_行业统计_sw_all.xlsx') as writer:
    signal_industry_count.to_excel(writer,'信号行业统计')
    holding_industry_count.to_excel(writer,'持仓行业统计')
    turn_over.to_excel(writer,'换手率')
