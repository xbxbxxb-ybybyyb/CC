########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
import copy
from xquant.thirdpartydata.factordata import FactorData
import datetime
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest
sys.path.append('/data/group/800319')
from dataApi import dividend
from dataApi import getData
from dataApi import indName
from dataApi import stockList
from dataApi import tradeDate
Start_time=20170101
End_time=20191231
stock_pool = getData.get_daily_1factor('common_stock_list').loc[Start_time:End_time]
#######################获取个股一年内是否有研报###################
###获取交易日
trade_day = tradeDate.get_date_range(start_date=20170101, end_date=20191231, period='D', dividing_point=15)
###获取自然日
def getEveryDay(begin_date,end_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y%m%d")
    end_date = datetime.datetime.strptime(end_date,"%Y%m%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y%m%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list
date_list=getEveryDay('20160101','20191231')

#########要求一：获取过去一年内存在研报的（会剔除300个）##############
s = FactorData()
df1 = s.get_factor_value("GOGOAL_DER_REPORT_RESEARCH", factors=['Code', 'Code_Name','Title','Type_ID','Create_Date'],
                          Create_Date=date_list[:800])
df2 = s.get_factor_value("GOGOAL_DER_REPORT_RESEARCH", factors=['Code', 'Code_Name','Title','Type_ID','Create_Date'],
                          Create_Date=date_list[800:])
data_research = df1.append(df2)
data_research['CREATE_DATE']=data_research['CREATE_DATE'].apply(lambda x:datetime.datetime.strptime(x[:10],"%Y-%m-%d").strftime("%Y%m%d"))
data_research['CREATE_DATE']=data_research['CREATE_DATE'].astype(int)
data_research['CODE']=data_research['CODE'].astype(int)
stock_research_time=pd.pivot_table(data_research,index='CREATE_DATE',columns='CODE',values='TYPE_ID')
stock_research_count=stock_research_time.sort_index().rolling(365).count().shift(1).loc[trade_day]
stock_pool_research=(stock_research_count>0)
stock_pool_research=stock_pool_research[list(set(stock_pool.columns).intersection(set(stock_pool_research.columns)))]

############要求二：前一个交易日无停牌，过去60个交易日累计停牌时间不超过5天（会剔除大概160个）##############
stock_pause=getData.get_daily_1factor('pause', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
stock_pause_yesterday=stock_pause.shift(1).loc[trade_day]
stock_pause_60=(stock_pause.rolling(60).sum()>=5).shift(1).loc[trade_day]
stock_no_pause=(1-stock_pause_60)*(1-stock_pause_yesterday)

############要求三：前一交易日非一字板涨跌停，过去60个交易日累计一字板数量不超过5个(非常少，每天平均9个）##############
AMT_day = getData.get_daily_1factor('amt', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
High_day = getData.get_daily_1factor('high', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
Low_day = getData.get_daily_1factor('low', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
Limit_day=(High_day==Low_day)*(AMT_day>0)
Limit_yesterday=Limit_day.shift(1).loc[trade_day]
Limit_60=(Limit_day.rolling(60).sum()>=5).shift(1).loc[trade_day]
stock_no_limit=(1-Limit_yesterday)*(1-Limit_60)

############要求四：过去20个交易日成交额中位数大于3000万#####################
AMT_day = getData.get_daily_1factor('amt', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
AMT_median=(AMT_day.rolling(20).median()>30000).shift(1).loc[trade_day]


############要求五：股价不能低于3元#################
Close_day = getData.get_daily_1factor('close', date_list=None, code_list=list(stock_pool.columns), type='stock', diy_address=None)
stock_bigger_3=(Close_day>3).shift(1).loc[trade_day]

New_stock_pool=(stock_pool_research*stock_no_pause*stock_no_limit*stock_bigger_3*stock_pool*AMT_median)
New_stock_pool=New_stock_pool[New_stock_pool.sum()[New_stock_pool.sum()>0].index]
New_stock_pool.to_hdf('/data/group/800319/New_stock_pool.h5', key='New_stock_pool')

New_stock_pool=pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')