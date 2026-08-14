import pandas as pd
import numpy as np
import IO
import os
from xquant.thirdpartydata.factordata import FactorData
# SHSCChannelholdings 陆港通通道持股数量统计(中央结算系统)
s = FactorData()
date_list = [20160630,20161231,
             20170630,20171231,
             20180630,20181231,
             20190630,20191231]
df = pd.DataFrame()
for i in range(len(date_list)-1):
    date_s = date_list[i]
    date_e = date_list[i+1]
    print([date_s,date_e])
    df_i = s.get_factor_value('WIND_SHSCChannelholdings',
                             factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_INFO_EXCHMARKETNAME', 'S_QUANTITY'],
                             TRADE_DT=[f'>{date_s}', f'<={date_e}'],
                             S_INFO_EXCHMARKETNAME = ['SHN','SZN'])
    print(len(df_i))
    df = pd.concat([df,df_i])
    print(len(df))
df = df.rename(columns = {'S_INFO_WINDCODE':'Ticker', 'TRADE_DT':'dt','S_QUANTITY':'qty'})
df['dt'] = df['dt'].apply(lambda x : pd.Timestamp(str(x)))
df = df.set_index(['dt','Ticker'])
df = df.sort_values(['dt','Ticker'])
df.to_pickle('/data/user/015585/01-因子挖掘/20231128_北向资金/file/north_funds.pkl')
