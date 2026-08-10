from multifactor.IO import IO
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt

def get_contract_fillna(contract, df):
    print(contract)
    mdf = df.xs(contract, level = 1)

    t_days_list = udt.get_trading_date_range(str(mdf.index[0].date()).replace('-',''),str(mdf.index[-1].date()).replace('-',''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:57:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    mdf = index_df.join(mdf,how = 'left')

    for col in ['open','high','low','close','position']:
        mdf[col] = mdf[col].fillna(method = 'ffill')
    for col in ['volume','amount']:
        mdf[col] = mdf[col].fillna(value = 0)
    mdf['Ticker'] = contract
    mdf['PROD_ID'] = mdf.Ticker.apply(lambda x:x[:2] + x[-4:])
    mdf = mdf.reset_index().set_index(['dt','Ticker']).sort_index()
    return mdf
    
def update_allcontract_data(startdate, df_allcontract, allcontract_path):
    df = IO.read_data([startdate, 21000101], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/WIND/MD_CHINA_FUTURES_MINUTE_WIND.h5')
    df = df[df.PROD_ID.isin(['IC.CFE','IF.CFE','IH.CFE'])]
    df = df.drop(['trading_day', 'PROD_ID', 'EXCHANGE'], axis = 1)
    contract_list = df.index.get_level_values(1).unique().tolist()
    
    for contract in contract_list:
        df_allcontract = df_allcontract.append(get_contract_fillna(contract, df))
    df_allcontract = df_allcontract.sort_index()
    
    os.remove(allcontract_path) if os.path.exists(allcontract_path) else None 
    IO.pd_hdf5_writer(df_allcontract, allcontract_path, dataset='contract')

def date_to_min_index(df, ticker, future_kind):
    indexdf = df.xs(ticker, level=1)[[future_kind]]
    t_days_list = udt.get_trading_date_range(str(indexdf.index[0].date()).replace('-', ''),
                                             str(indexdf.index[-1].date()).replace('-', ''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00',
                                                                                              '14:57:00',
                                                                                              freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    index_min['date'] = index_min['dt'].apply(lambda x: x.date())
    index_min['date'] = pd.to_datetime(index_min['date'])

    indexdf = indexdf.reset_index().rename(columns={'dt': 'date', future_kind: 'Ticker'})
    indexdf = pd.merge(indexdf, index_min, on='date')
    indexdf = indexdf[['dt', 'Ticker']].set_index(['dt', 'Ticker'])
    return indexdf

rootpath = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/WIND_MINUTE/'
allcontract_path = os.path.join(rootpath, 'MD_STOCK_INDEX_FUTURES_MINUTE_ALL_CONTRACT.h5')
continuity_path = os.path.join(rootpath, 'MD_STOCK_INDEX_FUTURES_MINUTE_CONTINUITY.h5')
recentmonth_path = os.path.join(rootpath, 'MD_STOCK_INDEX_FUTURES_RECENT_MONTH.h5')

df_allcontract = IO.read_data([20100101, 21000101], alt = allcontract_path)
sdate, _, cdate_list = check_update_date(int(str(df_allcontract.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
start_date = cdate_list[1]
end_date = cdate_list[-1]
assert sdate != start_date

# update all contract data
print('update all contract data')
update_allcontract_data(start_date, df_allcontract, allcontract_path)

# update recentmonth data
print('update recentmonth data')
df_recentmonth = IO.read_data([20200101, 21000101], alt = recentmonth_path)
sdate, _, cdate_list = check_update_date(int(str(df_recentmonth.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
start_date = cdate_list[1]
end_date = cdate_list[-1]
assert sdate != start_date

h5path = '/data/user/015626/data/share/MD/CHINA_FUTURES/'
rdf = pd.DataFrame()

for ticker in ['IC.CFE','IF.CFE','IH.CFE']:
    alldf = IO.read_data([start_date, 21000101], alt=allcontract_path)

    idf = IO.read_data([start_date, 21000101], alt=os.path.join(h5path, 'daily', 'MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'))
    idf = date_to_min_index(idf, ticker, future_kind='contract_00')

    alldf = alldf.join(idf, how='inner')
    origindata = alldf.reset_index().drop('PROD_ID', axis = 1).rename(columns = {'Ticker':'contract_00'})
    origindata['Ticker'] = ticker
    origindata = origindata.set_index(['dt','Ticker']).sort_index()
    
    rdf = rdf.append(origindata)
rdf = rdf.sort_index()
IO.pd_hdf5_writer(rdf, recentmonth_path, dataset='recent_month', append = True)

# update continuity data
print('update continuity data')
df_continuity = IO.read_data([20100101, 21000101], alt = continuity_path)
sdate, _, cdate_list = check_update_date(int(str(df_continuity.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
start_date = cdate_list[1]
end_date = cdate_list[-1]
assert sdate != start_date

pd_data_daily = IO.read_data([start_date, end_date], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/WIND/MD_CHINA_FUTURES_DAILY_WIND.h5')
ticker_dict = {'00.CFE':0,'01.CFE':1,'02.CFE':2,'03.CFE':3}
for TICKER in ['IC.CFE','IF.CFE','IH.CFE']:
    for key in ticker_dict.keys():
        IC_daily = pd_data_daily[pd_data_daily.PROD_ID == TICKER]
        IC02_daily = IC_daily.groupby('dt').apply(lambda x: x.iloc[ticker_dict[key]:ticker_dict[key]+1, :]).reset_index(level=0, drop=True).reset_index(level=1)
        pd_data = IO.read_data([start_date, 21000101], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/WIND/MD_CHINA_FUTURES_MINUTE_WIND.h5')
        IC = pd_data[pd_data.PROD_ID == TICKER].drop(['trading_day', 'PROD_ID', 'EXCHANGE'], axis = 1)

        IC02_minute_index = IC02_daily.reindex(IC.index.get_level_values(level=0).unique(), method='pad').reset_index().set_index(['dt', 'Ticker']).index
        # current month
        IC02 = IC.reindex(IC02_minute_index).reset_index(level=1).rename(columns = {'Ticker':'contract'})

        t_days_list = udt.get_trading_date_range(str(IC02.index[0].date()).replace('-',''),str(IC02.index[-1].date()).replace('-',''))
        t_days_list = [str(i)[:10] for i in t_days_list]
        t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:57:00', freq='min').to_list()
        t_mins_list = [str(i)[-8:] for i in t_mins_list]
        index_list = []
        for d in t_days_list:
            for m in t_mins_list:
                index_list.append(d + ' ' + m)
        index_df = pd.DataFrame({'dt':index_list})
        index_df['dt'] = pd.to_datetime(index_df['dt'])
        index_df = index_df.set_index('dt')

        newIC_02 = index_df.join(IC02,how = 'left')

        for col in ['open','high','low','close','position','contract']:
            newIC_02[col] = newIC_02[col].fillna(method = 'ffill')
        for col in ['volume','amount']:
            newIC_02[col] = newIC_02[col].fillna(value = 0)

        newIC_02 = newIC_02.dropna(subset=['close'])
        newIC_02['Ticker'] = TICKER[:2] + key
        newIC_02 = newIC_02.reset_index().set_index(['dt','Ticker']).sort_index()
        print(newIC_02.index[0])
        df_continuity = df_continuity.append(newIC_02)
df_continuity = df_continuity.sort_index()
os.remove(continuity_path) if os.path.exists(continuity_path) else None 
IO.pd_hdf5_writer(df_continuity, continuity_path, dataset='continuity')

