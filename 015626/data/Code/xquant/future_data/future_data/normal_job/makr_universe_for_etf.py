import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob, os
import bottleneck as bk
from xquant.factordata import FactorData
%matplotlib inline

from xquant.xqutils.helper import link
from pandas.testing import assert_frame_equal, assert_series_equal
from xquant.factordata import FactorData
s = FactorData()

corr_threshold = 0.95

df = pd.read_hdf('/data/user/015626/data/share/MD/CHINA_FUND/DAILY/MD_CHINA_ETF_DAILY.h5')

df[['close']].groupby('dt').count().plot()

# 找出黑名单
etf_track_index = s.get_factor_value('WIND_ChinaMutualFundTrackingIndex')
etf_track_index = etf_track_index[etf_track_index.S_INFO_WINDCODE.isin(df.index.get_level_values(1).unique().tolist())]
black_list = [etf_track_index['S_INFO_WINDCODE'].iloc[i] for i in range(etf_track_index.shape[0]) if 
               etf_track_index['S_INFO_INDEXWINDCODE'].iloc[i].split('.')[-1] in ['DCE', 'SHF', 'CZC', 'SPI', 'MI', 'CS', 'XI', 'SGE', 'HI', 'GI']]  # 跟踪标的为标普系列指数的ETF
etf_track_index = etf_track_index[~etf_track_index.S_INFO_WINDCODE.isin(black_list)]
# etf_track_index.drop(['OBJECT_ID','OPDATE','OPMODE'], axis =1).to_csv('/data/user/015626/data/share/MD/CHINA_FUND/UNIVERSE/track_index_info.csv', index=False)
df = df.loc[(slice(None),etf_track_index.S_INFO_WINDCODE.tolist()),:]

len(df)

amount = df['amount'].unstack()
amount = amount.rolling(30, min_periods=20).mean()
amount_mask = amount > 3e7
amount_select3 = amount_mask.shift(1).stack().reindex(df.index).to_frame()
amount_select3.columns = ['amount_select3']
amount_mask = amount > 2e7
amount_select2 = amount_mask.shift(1).stack().reindex(df.index).to_frame()
amount_select2.columns = ['amount_select2']
amount_mask = amount > 5e6
amount_select5 = amount_mask.shift(1).stack().reindex(df.index).to_frame()
amount_select5.columns = ['amount_select5']

etf_track_index = etf_track_index.rename(columns = {'S_INFO_WINDCODE':'Ticker'})
df = df.reset_index()
df = pd.merge(df, etf_track_index[['Ticker','ENTRY_DT','REMOVE_DT']], on=['Ticker'],how = 'left')

df['ENTRY_DT'] = pd.to_datetime(df['ENTRY_DT'])
df['REMOVE_DT'] = pd.to_datetime(df['REMOVE_DT'])
df['list_days'] = df.apply(lambda x:(x['dt'] - x['ENTRY_DT']).days, axis = 1)
df['res_days'] = df.apply(lambda x:(x['REMOVE_DT'] - x['dt']).days, axis = 1)
df = df[df.list_days >= 0]
df = df[~(df.res_days <= 0)]
df['list_days_30'] = df['list_days'] >= 30

df = df.set_index(['dt','Ticker']).sort_index()

df = df.join(amount_select2, how = 'left').join(amount_select3, how = 'left').join(amount_select5, how = 'left')
df[['list_days_30','amount_select2','amount_select3','amount_select5']] = df[['list_days_30','amount_select2','amount_select3','amount_select5']].fillna(False)
df['temp_univ'] = df['list_days_30'] & df['amount_select5']

def get_lowcorr_stock(date):
    start_day = udt.get_trading_day_offset(str(date),-60)[0].strftime('%Y%m%d')
    stock_list = df.loc[str(date)]['temp_univ']
    stock_list = stock_list[stock_list == True].index.get_level_values(1).tolist()

    temp = df[['close','amount']].loc[pd.to_datetime(start_day):pd.to_datetime(str(date))].loc[(slice(None), stock_list),:].unstack()

    temp_close = temp['close']
    temp_close_corr = temp_close.corr().unstack().to_frame()
    temp_close_corr.index.names = ['Ticker1','Ticker2']
    temp_close_corr.columns = ['corre']
    temp_close_corr = temp_close_corr.loc[temp_close_corr.index.get_level_values(0) != temp_close_corr.index.get_level_values(1)]
    temp_close_corr = temp_close_corr.loc[temp_close_corr.corre >= corr_threshold].reset_index()

    high_corr_list = list(set(temp_close_corr.Ticker1.tolist() + temp_close_corr.Ticker2.tolist()))
    low_corr_list = list(set(stock_list) - set(high_corr_list))

    temp_amount = temp['amount']
    temp_amount = temp_amount.mean().loc[high_corr_list].sort_values(ascending = False)
    high_corr_list = temp_amount.index.tolist()

    for x in high_corr_list:
        if temp_close[low_corr_list].corrwith(temp_close[x]).max() < corr_threshold:
            low_corr_list.append(x)
    return pd.DataFrame(low_corr_list, index = [date for i in range(len(low_corr_list))], columns = ['Ticker'])

datelist = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(20180522,20210617)]
with Pool(24) as pool:
    rlist = pool.map(get_lowcorr_stock, datelist)

result = pd.concat(rlist, axis = 0).reset_index()
result['corr_select'] = True
result.columns = ['dt','Ticker','corr_select']
result['dt'] = pd.to_datetime(result['dt'])

df = df.join(result.set_index(['dt','Ticker']), how = 'left')

df['corr_select'] = df['corr_select'].fillna(False)

df['univ2'] = df['list_days_30'] & df['amount_select2'] & df['corr_select']
df['univ3'] = df['list_days_30'] & df['amount_select3'] & df['corr_select']
df['univ'] = df['list_days_30'] & df['amount_select5'] & df['corr_select']
IO.pd_hdf5_writer(df[['univ']],'/data/user/015626/data/share/MD/CHINA_FUND/UNIVERSE/CHINA_FUND_UNIVERSE.h5', dataset = 'CHINA_FUND_UNIVERSE', override=True)