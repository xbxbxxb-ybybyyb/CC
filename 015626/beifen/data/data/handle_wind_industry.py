# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 09:16:58 2018

@author: 012315
"""

from multifactor.data.utils import * 
import multifactor.utility.dt as tdt
import datetime as dt
import pandas as pd





def industry_parser(ind_code):
    ind2 = ind_code[:6]
    if 'b10m' in ind2:
        ind_lv2_code = ind2
    else:
        ind_lv2_code = ind2[:4] + '00'
    return ind_lv2_code

#### update industry h5
sql = "select * from wind_AshareIndClassCITICS"
data_raw = sql_parser(queryUserTableData(sql))




sdate,edate = 2018710,20180710

#### transform to industry level 2 number 
industry_code = ['b10100', 'b10200', 'b10300', 'b10400', 'b10500', 'b10600',
                 'b10700', 'b10800', 'b10900', 'b10a00', 'b10b00', 'b10c00', 
                 'b10d00', 'b10e00', 'b10f00', 'b10g00', 'b10h00', 'b10i00',
                 'b10j00', 'b10k00', 'b10l00', 'b10n00', 'b10o00', 'b10p00', 
                 'b10q00', 'b10r00', 'b10s00', 'b10t00','b10m01', 'b10m02', 'b10m03']

industry_num = [i+1 for i in range(len(industry_code))]
industry_dict = dict(zip(industry_code,industry_num))

data_raw['lv2_ind_code'] = data_raw['CITICS_IND_CODE'].apply(industry_parser)
data_raw['lv2_ind_num'] = data_raw['lv2_ind_code'].apply(lambda x:industry_dict[x])
data_raw['dt'] = data_raw['ENTRY_DT'].apply(lambda x: pd.Timestamp(dt.datetime.strptime(str(x), '%Y%m%d')))
data = data_raw.set_index(['dt','WIND_CODE']).sort_index()
data.index.names = ['dt','Ticker']
data = data['lv2_ind_num'].unstack()

orig_dt = pd.Timestamp(dt.datetime.strptime(str(20000101), '%Y%m%d'))
sdate_dt = pd.Timestamp(dt.datetime.strptime(str(sdate), '%Y%m%d'))
edate_dt = pd.Timestamp(dt.datetime.strptime(str(edate), '%Y%m%d'))

full_day_range = pd.date_range(start = orig_dt,end = edate_dt,freq='1D')
print(full_day_range)
print(data)
data = data.reindex(index=full_day_range).fillna(method='ffill')
print(data)
print(tdt.get_trading_date_range(sdate_dt, edate_dt))
data = data.reindex(index=tdt.get_trading_date_range(sdate_dt, edate_dt))

# use this data to dump to industry h5 
industry_data = data.stack()
# print(industry_data)
# stk = '002034.SZ' - different for a week

