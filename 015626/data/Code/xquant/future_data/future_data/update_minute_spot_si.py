from multifactor.IO import IO
import pandas as pd
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import time

def get_ticker(a):
    namedict = {16:'IH.CFE',300:'IF.CFE',905:'IC.CFE',852:'IM.CFE'}
    return namedict[a]
    
def get_dt(date, hourminute):
    year = date // 10000
    month = date % 10000 // 100
    day = date % 100
    hour = hourminute // 100
    minute = hourminute % 100
    return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    
def minute_flag_check(date):
    path = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_' + 'MINUTE.success'
    return os.path.exists(path)

sdate,edate,cdate_list = check_update_date()

flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(edate) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(edate) + '_' + 'spot_minute.start'

with open(flag_path_start,'w') as file:
    pass 


print('------wait minute flag')
while True:
    if minute_flag_check(sdate):
        break
    time.sleep(60)
    
print('start generate data')

icdf = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_000905.pkl', compression='gzip')
icdf = icdf.reset_index()
icdf['Ticker'] = 'IC.CFE'
icdf = icdf.rename(columns={'dt':'date'})
icdf['dt'] = icdf.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
icdf = icdf.drop(['date','minute'], axis = 1)

ifdf = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_000300.pkl', compression='gzip')
ifdf = ifdf.reset_index()
ifdf['Ticker'] = 'IF.CFE'
ifdf = ifdf.rename(columns={'dt':'date'})
ifdf['dt'] = ifdf.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
ifdf = ifdf.drop(['date','minute'], axis = 1)

ihdf = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_000016.pkl', compression='gzip')
ihdf = ihdf.reset_index()
ihdf['Ticker'] = 'IH.CFE'
ihdf = ihdf.rename(columns={'dt':'date'})
ihdf['dt'] = ihdf.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
ihdf = ihdf.drop(['date','minute'], axis = 1)

imdf = pd.read_pickle('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/indexMinute_000852.pkl', compression='gzip')
imdf = imdf.reset_index()
imdf['Ticker'] = 'IM.CFE'
imdf = imdf.rename(columns={'dt':'date'})
imdf['dt'] = imdf.apply(lambda x:get_dt(x.date, x.minute), axis = 1)
imdf = imdf.drop(['date','minute'], axis = 1)

df = icdf.append(ifdf).append(ihdf).append(imdf)
df = df.sort_values(['dt','Ticker'])
df = df.set_index(['dt','Ticker'])

idx = df.index.get_level_values(0)
t1 = df.loc[(idx.hour == 9) & (idx.minute >= 30)]
t2 = df.loc[(idx.hour == 10) | (idx.hour == 13)]
t3 = df.loc[(idx.hour == 11) & (idx.minute < 30)]
t4 = df.loc[(idx.hour == 14) & (idx.minute <= 57)]
t = t1.append(t2).append(t3).append(t4)
t = t.sort_index()

clist = t.columns.tolist()
cdict = {}
for c in clist:
    cdict[c] = c+'_spot'
t = t.rename(columns = cdict)
t = t.rename(columns = {'amt_spot':'amount_spot'})

result = pd.DataFrame()
for ticker in ['IF.CFE','IC.CFE','IH.CFE','IM.CFE']:
    mdf = t.xs(ticker,level = 1)
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

    mdf = index_df.join(mdf, how = 'left')
    for col in ['open_spot','high_spot','low_spot','close_spot']:
        mdf[col] = mdf[col].fillna(method = 'ffill')
    for col in ['volume_spot','amount_spot']:
        mdf[col] = mdf[col].fillna(value = 0)

    mdf['Ticker'] = ticker
    mdf = mdf.reset_index().set_index(['dt','Ticker']).sort_index()
    result = result.append(mdf)
result = result.sort_index()
result = result.reset_index(level = 1)
result = result.loc[result.index.year >= 2014]
result = result.reset_index().set_index(['dt','Ticker']).sort_index()

historydf = IO.read_data([20000101,20220101], alt='/data/user/015626/data/share/LOCAL_DATA/CSV/MINUTE/index_history/INDEX_HISTORY.h5')
t = historydf.append(result)
t = t.sort_index()

h5path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5'

if os.path.exists(h5path):
    os.remove(h5path)

IO.pd_hdf5_writer(t, h5path, dataset='spot')

flag_path_success = flag_root + str(edate) + '_' + 'spot_minute.success'
with open(flag_path_success,'w') as file:
    pass
    
print('start generate mask')
fdf = t.loc[pd.to_datetime('20200101'):].sort_index()

spot_dict = {}
for x in ['IC.CFE','IF.CFE','IH.CFE','IM.CFE']:
    d = fdf.xs(x, level = 1)
    if x == 'IF.CFE':
        d = d.add_suffix('_if')
    if x == 'IH.CFE':
        d = d.add_suffix('_ih')
    if x == 'IM.CFE':
        d = d.add_suffix('_im')
    for c in d.columns:
        spot_dict[c] = d[c]
        
import pickle

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
save_pickle(spot_dict, '/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/SPOT_DATA_2020.pkl')

# 以下为更新overnight收益
def delete_holidays(df):
    df = df.reset_index()
    datelist = df.dt.tolist()
    datedict = {}
    for i in range(len(datelist) - 1):
        datedict[datelist[i]] = (datelist[i+1] - datelist[i]).days
    daterange = pd.DataFrame(datedict, index = ['days']).T
    deletelist = daterange[~daterange.days.isin([1,3])].index.tolist()
    r = df[~df.dt.isin(deletelist)]
    r = r.set_index(['dt','Ticker'])
    return r
    
print('start generate overnight index return')
spot_data = IO.read_data([20010101, 21000101],columns = ['close_spot'], alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')

retdf = pd.DataFrame()
for ticker in ['IC.CFE', 'IF.CFE','IH.CFE','IM.CFE']:
    kind_data = spot_data.xs(ticker, level = 1)

    idx = kind_data.index
    close_noon = kind_data.loc[(idx.hour == 14) & (idx.minute >= 50)]
    close_morning = kind_data.loc[(idx.hour == 9) & (idx.minute <= 39)]

    close_noon = close_noon.groupby(close_noon.index.date).mean()
    close_morning = close_morning.groupby(close_morning.index.date).mean()

    close_noon.columns = ['close_noon']
    close_morning.columns = ['close_morning']

    close = close_noon.join(close_morning).sort_index()

    close['ret'] = close.close_morning.shift(-1) / close.close_noon - 1

    close['Ticker'] = ticker
#    close = close[['Ticker','ret']]
    close.index.names = ['dt']
    close = close[:-1]
    close = delete_holidays(close)
    
    retdf = retdf.append(close)

retdf = retdf.sort_index()

IO.pd_hdf5_writer(retdf, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_indexret_10minsclose.h5', dataset='overnight_indexret_10minsclose', override=True)

retdf = pd.DataFrame()
for ticker in ['IC.CFE', 'IF.CFE','IH.CFE', 'IM.CFE']:
    kind_data = spot_data.xs(ticker, level = 1)

    idx = kind_data.index
    close_noon_1450_1459 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 50) & (idx.minute <= 59)]
    close_noon_1440_1449 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 40) & (idx.minute <= 49)]
    close_noon_1430_1439 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 30) & (idx.minute <= 39)]
    close_noon_1420_1429 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 20) & (idx.minute <= 29)]
    close_noon_1410_1419 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 10) & (idx.minute <= 19)]
    close_noon_1400_1409 = kind_data.loc[(idx.hour == 14) & (idx.minute >= 0) & (idx.minute <= 9)]
    
    close_morning_930_939 = kind_data.loc[(idx.hour == 9) & (idx.minute >= 30) & (idx.minute <= 39)]
    close_morning_940_949 = kind_data.loc[(idx.hour == 9) & (idx.minute >= 40) & (idx.minute <= 49)]
    close_morning_950_959 = kind_data.loc[(idx.hour == 9) & (idx.minute >= 50) & (idx.minute <= 59)]

    close_noon_1450_1459 = close_noon_1450_1459.groupby(close_noon_1450_1459.index.date).mean()
    close_noon_1440_1449 = close_noon_1440_1449.groupby(close_noon_1440_1449.index.date).mean()
    close_noon_1430_1439 = close_noon_1430_1439.groupby(close_noon_1430_1439.index.date).mean()
    close_noon_1420_1429 = close_noon_1420_1429.groupby(close_noon_1420_1429.index.date).mean()
    close_noon_1410_1419 = close_noon_1410_1419.groupby(close_noon_1410_1419.index.date).mean()
    close_noon_1400_1409 = close_noon_1400_1409.groupby(close_noon_1400_1409.index.date).mean()
    
    close_morning_930_939 = close_morning_930_939.groupby(close_morning_930_939.index.date).mean()
    close_morning_940_949 = close_morning_940_949.groupby(close_morning_940_949.index.date).mean()
    close_morning_950_959 = close_morning_950_959.groupby(close_morning_950_959.index.date).mean()

    close_noon_1450_1459.columns = ['close_noon_1450_1459']
    close_noon_1440_1449.columns = ['close_noon_1440_1449']
    close_noon_1430_1439.columns = ['close_noon_1430_1439']
    close_noon_1420_1429.columns = ['close_noon_1420_1429']
    close_noon_1410_1419.columns = ['close_noon_1410_1419']
    close_noon_1400_1409.columns = ['close_noon_1400_1409']
    
    close_morning_930_939.columns = ['close_morning_930_939']
    close_morning_940_949.columns = ['close_morning_940_949']
    close_morning_950_959.columns = ['close_morning_950_959']

    close = pd.concat([close_morning_930_939,close_morning_940_949,close_morning_950_959,close_noon_1400_1409,close_noon_1410_1419,close_noon_1420_1429,close_noon_1430_1439,close_noon_1440_1449,close_noon_1450_1459], axis = 1)

    for am in ['close_morning_930_939', 'close_morning_940_949', 'close_morning_950_959']:
        for pm in ['close_noon_1400_1409', 'close_noon_1410_1419', 'close_noon_1420_1429', 'close_noon_1430_1439', 'close_noon_1440_1449', 'close_noon_1450_1459']:
            close['ret_'+am.split('_')[-2]+'_'+pm.split('_')[-2]] = close[am].shift(-1) / close[pm] - 1
     
    close['Ticker'] = ticker
#    close = close[['Ticker','ret']]
    close.index.names = ['dt']
    close = close[:-1]
    close = delete_holidays(close)
    
    retdf = retdf.append(close)

retdf = retdf.sort_index()

IO.pd_hdf5_writer(retdf, '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/overnight_indexret_10minsclose_multitime.h5', dataset='overnight_indexret_10minsclose_multitime', override=True)

#flag_path_success = flag_root + str(edate) + '_' + 'spot_minute.success'
#with open(flag_path_success,'w') as file:
#    pass