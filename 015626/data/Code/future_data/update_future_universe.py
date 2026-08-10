from multifactor.IO import IO
import pandas as pd
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import time
import re

df = IO.read_data([20200101,21000101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
sdate,edate,cdate_list = check_update_date(int(str(df.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
start_date = cdate_list[1]
end_date = cdate_list[-1]

flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(end_date) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(end_date) + '_' + 'stock_index_future_universe.start'
with open(flag_path_start,'w') as file:
    pass 

def minute_flag_check(date):
    path1 = '/data/user/012245/warehouse/flags/' + str(date) + '/' + str(date) + '_COMMODITY_BASE.success'
    return os.path.exists(path1)

print('------wait doc.Xu flag')
while True:
    if minute_flag_check(edate):
        break
    time.sleep(60)

index00 = pd.DataFrame()
for TICKER in ['IC.CFE','IF.CFE','IH.CFE']:
    pd_data_daily = IO.read_data([start_date, end_date], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/WIND/MD_CHINA_FUTURES_DAILY_WIND.h5')
    IC_daily = pd_data_daily[pd_data_daily.PROD_ID == TICKER]
    df00 = IC_daily.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]
    df01 = IC_daily.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','EXPIRATION_DAYS']]

    df00 = df00.rename(columns = {x:x+'_00' for x in df00.columns.tolist()})
    df01 = df01.rename(columns = {x:x+'_01' for x in df01.columns.tolist()})

    df = df00.join(df01)
    df.loc[df.EXPIRATION_DAYS_00 <= 2,'Ticker_00'] = np.nan
    df['Ticker_00'].fillna(df['Ticker_01'], inplace = True)
    df = df[['Ticker_00']]
    df['Ticker'] = TICKER
    df = df.reset_index().rename(columns = {'Ticker_00':'contract_00'}).set_index(['dt','Ticker'])
    index00 = index00.append(df)
index00 = index00.sort_index()

finaldf = pd.DataFrame()
for TICKER in ['IC.CFE','IF.CFE','IH.CFE']:
    pd_data_daily = IO.read_data([start_date, end_date], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/MAIN/MD_CHINA_FUTURES_DAILY_MAIN.h5')
    ic_daily = pd_data_daily.xs(TICKER, level = 1)[['WIND_CODE']]
    ic_daily['future_kind'] = ic_daily['WIND_CODE'].apply(lambda x:x[:2] + x[-4:])

    finaldf = finaldf.append(ic_daily)
finaldf = finaldf.reset_index().rename(columns = {'WIND_CODE':'contract_main','future_kind':'Ticker'}).set_index(['dt','Ticker'])
finaldf = finaldf.sort_index()

indexdf = finaldf.join(index00)

def get_02_contract(x):
    ticker = x[:2]
    year = int(x[2:4])
    month = x[4:6]

    if month in ['11','12']:
        newmonth = '03'
        year += 1
    elif month in ['01']:
        newmonth = '03'
    elif month in ['02','03','04']:
        newmonth = '06'
    elif month in ['05','06','07']:
        newmonth = '09'
    elif month in ['08','09','10']:
        newmonth = '12'
    return ticker + str(year) + newmonth + '.CFE'

# return recent_contract and season_contract
def get_current_futures_contract(prod_id, trade_date=None, exp_cut_num=3, mode='recent'):
    assert mode in ['recent', 'season']
    if trade_date is None:
        trade_date = pd.Timestamp.now()
    else:
        trade_date = IO.str_date_parser(trade_date)
    last_trading_day = udt.get_trading_day_offset(trade_date.strftime('%Y%m%d'), -1)[0]
    data = IO.read_data(last_trading_day, columns=['PROD_ID', 'EXPIRATION_DAYS'], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/DAILY/WIND/MD_CHINA_FUTURES_DAILY_WIND.h5').loc[last_trading_day]
    data = data.loc[data.PROD_ID == prod_id]
    assert len(data) >= 4
    data = data.sort_values(by='EXPIRATION_DAYS')
    if data.EXPIRATION_DAYS[0] <= exp_cut_num:
        recent_index = 1
    else:
        recent_index = 0
    recent_contract = data.index[recent_index]
    if mode == 'recent':
        return recent_contract
    elif mode == 'season':
        for i in range(recent_index + 1, len(data)):
            contract = data.index[i]
            if int(re.sub("\D", "", contract)) % 100 in [3,6,9,12]:
                season_contract = contract
                return season_contract
        raise AssertionError
            
indexdf['contract_02'] = indexdf.contract_00.apply(lambda x:get_02_contract(x)) 
indexdf = indexdf.reset_index()  
indexdf['contract_season'] = indexdf.apply(lambda x:get_current_futures_contract(x.Ticker,x['dt'], mode = 'season'), axis = 1)
indexdf = indexdf.set_index(['dt','Ticker'])
IO.pd_hdf5_writer(indexdf, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5', dataset='universe', append = True)
    
#u = IO.read_data([20100101,21000101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
##u['contract_01'] = u.contract_00.apply(lambda x:get_01_contract(x))
#u['contract_02'] = u.contract_00.apply(lambda x:get_02_contract(x))

#IO.pd_hdf5_writer(u, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5', dataset='universe', override = True)
        
flag_path_success = flag_root + str(end_date) + '_' + 'stock_index_future_universe.success'
with open(flag_path_success,'w') as file:
    pass

'''
def get_01_contract(x):
    ticker = x[:2]
    year = int(x[2:4])
    month = int(x[4:6]) + 1
    if month == 13:
        year += 1
        month = 1
    month = str(month)
    if len(month) == 1:
        month = '0'+ month
    return ticker + str(year) + month + '.CFE'

def get_02_contract(x):
    ticker = x[:2]
    year = int(x[2:4])
    month = x[4:6]

    if month in ['11','12']:
        newmonth = '03'
        year += 1
    elif month in ['01']:
        newmonth = '03'
    elif month in ['02','03','04']:
        newmonth = '06'
    elif month in ['05','06','07']:
        newmonth = '09'
    elif month in ['08','09','10']:
        newmonth = '12'
    return ticker + str(year) + newmonth + '.CFE'

def get_03_contract(x):
    ticker = x[:2]
    year = int(x[2:4])
    month = x[4:6]

    if month in ['08','09','10']:
        newmonth = '03'
        year += 1
    elif month in ['01']:
        newmonth = '06'
    elif month in ['11','12']:
        newmonth = '06'
        year += 1
    elif month in ['02','03','04']:
        newmonth = '09'
    elif month in ['05','06','07']:
        newmonth = '12'
    return ticker + str(year) + newmonth + '.CFE'
    
u = IO.read_data([20100101,20201111], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
u['contract_01'] = u.contract_00.apply(lambda x:get_01_contract(x))
u['contract_02'] = u.contract_00.apply(lambda x:get_02_contract(x))
u['contract_03'] = u.contract_00.apply(lambda x:get_03_contract(x))
u.loc[u.groupby('contract_03').head(3).index,'contract_03'] = np.nan
'''