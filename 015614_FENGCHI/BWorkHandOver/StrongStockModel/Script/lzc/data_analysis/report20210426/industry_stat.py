# @Time : 2021/4/26 12:14
# @Author : Zhichen Lu
# @File : industry_stat.py
import pandas as pd
from dataApi.getData import get_daily_1factor,trans_windcode2int,trans_int2windcode
from dataApi.tradeDate import get_date_range
from online_conf import local_config_path,holding_info_path
from dataApi.indName import sw_level2

signal_industry_count = {}
holding_industry_count = {}


date_list = get_date_range(20210414,20210423)
for date in date_list:
    holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
    holding.pop('cash')
    ret_decomposition = pd.read_excel(f'/data/user/015664/AFuckingTrigger/实盘/{date}/成交明细及收盘持仓情况{date}.xlsx',sheet_name='收益明细')
    industry_info = get_daily_1factor('SW2',date_list=[date],code_list=list(set(ret_decomposition['证券代码'].apply(trans_windcode2int))))
    industry_info.columns = industry_info.columns.map(trans_int2windcode)
    industry_info = industry_info.loc[date].apply(lambda x : sw_level2[x])
    ret_decomposition['申万二级行业'] = ret_decomposition['证券代码'].apply(lambda x : industry_info[x])
    signal_industry_count[date] = ret_decomposition.groupby(['申万二级行业','类型']).size().reindex(list(sw_level2.keys())).fillna(0)
    holding_industry_count[date] = pd.DataFrame({'申万二级行业':pd.Series(industry_info).loc[list(holding.keys())]}).groupby('申万二级行业').size()
