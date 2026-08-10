import json,datetime,os,glob
from multiprocessing.pool import Pool
import pandas as pd
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import numpy as np
pd.set_option('max_columns', 200)
import glob
from tqdm import tqdm
from multifactor.data.utils import *

past_days = 5

_,now_tday,_ = check_update_date()

def minute_flag_check(date):
    path1 = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_kzz_minute.success'
    return os.path.exists(path1)

print('------wait minute flag')
while True:
    if minute_flag_check(now_tday):
        break
    time.sleep(60)
print('flag check finished!')


end_date = udt.get_trading_day_offset(str(now_tday), 1)[0].strftime('%Y%m%d')
tday = pd.to_datetime(str(end_date)).date()

df = IO.read_data(columns = ['close','amount'], alt = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/MINUTE/CHINA_CONVERTIBLE_BOND_MINUTE.h5')
df = df.unstack()

amt_last10 = df['amount'].between_time(datetime.time(14,50),datetime.time(15,0))
amt_last10 = amt_last10.groupby(amt_last10.index.date).sum()#.shift(1)
amt_last10.index = pd.to_datetime(amt_last10.index)
amt_last10 = amt_last10.stack().to_frame()
amt_last10.index.names = ['dt', 'Ticker']
amt_last10.columns = ['amount_last_10mins']

amt = df['amount']
amt = amt.groupby(amt.index.date).sum()
amt.loc[tday] = 1
amt.index = pd.to_datetime(amt.index)
amt_mask_1000 = amt > 10000000
amt_mask_1000 = amt_mask_1000.rolling(past_days, min_periods=past_days//2).sum()
amt_mask_1000 = (amt_mask_1000 == past_days).shift(1).fillna(False)

amt_mask_2000 = amt > 20000000
amt_mask_2000 = amt_mask_2000.rolling(past_days, min_periods=past_days//2).sum()
amt_mask_2000 = (amt_mask_2000 == past_days).shift(1).fillna(False)

amt_mask_3000 = amt > 30000000
amt_mask_3000 = amt_mask_3000.rolling(past_days, min_periods=past_days//2).sum()
amt_mask_3000 = (amt_mask_3000 == past_days).shift(1).fillna(False)

amt_mask_5000 = amt > 50000000
amt_mask_5000 = amt_mask_5000.rolling(2, min_periods=2//2).sum()
amt_mask_5000 = (amt_mask_5000 == 2).shift(1).fillna(False)

amt_mask_1000 = amt_mask_1000.stack().to_frame()
amt_mask_1000.columns = ['amount_1000']
amt_mask_2000 = amt_mask_2000.stack().to_frame()
amt_mask_2000.columns = ['amount_2000']
amt_mask_3000 = amt_mask_3000.stack().to_frame()
amt_mask_3000.columns = ['amount_3000']
amt_mask_5000 = amt_mask_5000.stack().to_frame()
amt_mask_5000.columns = ['amount_5000']
amt_mask = amt_mask_3000.join(amt_mask_5000, how = 'left').join(amt_mask_2000, how = 'left').join(amt_mask_1000, how = 'left')
amt_mask.index.names = ['dt','Ticker']

# 获取债券余额 以及评级
amt_daily = amt.stack().to_frame()
amt_daily.columns = ['amount_daily']
amt_daily = amt_daily[amt_daily.amount_daily != 0]
amt_daily.index.names = ['dt','Ticker']

tickerlist = amt_daily.index.get_level_values(1).unique().tolist()

from xquant.factordata import FactorData
s = FactorData()
cbondamount = s.get_factor_value('WIND_CBondAmount', S_INFO_ENDDATE=['<20220101']).append(s.get_factor_value('WIND_CBondAmount', S_INFO_ENDDATE=['>=20220101']))
cbondamount = cbondamount[['S_INFO_WINDCODE','S_INFO_ENDDATE','B_INFO_CHANGEREASON','B_INFO_OUTSTANDINGBALANCE']]
cbondamount = cbondamount.rename(columns = {'S_INFO_WINDCODE':'Ticker', 'S_INFO_ENDDATE':'dt'})
cbondamount['dt'] = pd.to_datetime(cbondamount['dt'])
cbondamount = cbondamount[cbondamount.Ticker.isin(tickerlist)].set_index(['dt','Ticker'])[['B_INFO_OUTSTANDINGBALANCE']].sort_index() * 1e8
# 债券评级
#cbondrating = IO.read_data(columns=['B_CREDITRATING_CHANGE', 'B_INFO_CREDITRATING'] , alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/CBondRating/CBondRating.h5')
cbondrating = s.get_factor_value('WIND_CBondRating',ANN_DT=['>=20100101','<=%s' % now_tday])[['ANN_DT','S_INFO_WINDCODE','B_CREDITRATING_CHANGE', 'B_INFO_CREDITRATING']]
cbondrating = cbondrating.rename(columns = {'ANN_DT':'dt', 'S_INFO_WINDCODE':'Ticker'}).set_index(['dt','Ticker']).sort_index()
# 正股评级
csvinfo = pd.read_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv')
csvinfo = csvinfo[['Ticker', 'stockcode', 'COMPCODE']]
#stock_rating = IO.read_data(columns=['B_RATE_RATINGOUTLOOK','B_INFO_CREDITRATING','B_INFO_PRECREDITRATING','B_CREDITRATING_CHANGE'],
#                 alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/CBondIssuerRating/CBondIssuerRating.h5')
stock_rating = s.get_factor_value('WIND_CBondIssuerRating',ANN_DT=['>=20100101','<=%s' % now_tday])[['ANN_DT','S_INFO_COMPCODE','B_RATE_RATINGOUTLOOK','B_INFO_CREDITRATING','B_INFO_PRECREDITRATING','B_CREDITRATING_CHANGE']]
stock_rating = stock_rating.rename(columns = {'ANN_DT':'dt', 'S_INFO_COMPCODE':'Ticker'}).set_index(['dt','Ticker']).sort_index()
stock_rating = stock_rating.reset_index().rename(columns = {'Ticker':'COMPCODE'})
stock_rating = pd.merge(stock_rating, csvinfo, on='COMPCODE', how = 'inner').set_index(['dt','Ticker']).sort_index()
stock_rating = stock_rating.drop(['COMPCODE','stockcode'], axis = 1).add_suffix('_stock')
stock_rating = stock_rating.loc[~stock_rating.index.duplicated()]

rlist = []
for t in tqdm(tickerlist):
    t_amt = amt_daily.xs(t, level = 1)
    t_yue = cbondamount.xs(t, level = 1)
    tdf = t_amt.join(t_yue, how = 'outer')
    tdf['B_INFO_OUTSTANDINGBALANCE'] = tdf['B_INFO_OUTSTANDINGBALANCE'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
    try:
        t_rating = cbondrating.xs(t, level = 1)
        tdf = tdf.join(t_rating, how = 'outer')
        tdf['B_INFO_CREDITRATING'] = tdf['B_INFO_CREDITRATING'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
        tdf['B_CREDITRATING_CHANGE'] = tdf['B_CREDITRATING_CHANGE'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
    except Exception as e:
        print(e)
    try:
        stk_rating = stock_rating.xs(t, level = 1)
        tdf = tdf.join(stk_rating, how = 'outer')
        tdf[['B_INFO_CREDITRATING_stock']] = tdf['B_INFO_CREDITRATING_stock'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
        tdf['B_RATE_RATINGOUTLOOK_stock'] = tdf['B_RATE_RATINGOUTLOOK_stock'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
        tdf[['B_INFO_PRECREDITRATING_stock']] = tdf['B_INFO_PRECREDITRATING_stock'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
        tdf['B_CREDITRATING_CHANGE_stock'] = tdf['B_CREDITRATING_CHANGE_stock'].shift(1).fillna(method = 'ffill').fillna(method = 'bfill')
    except Exception as e:
        print('stock_rating: ',e)
    tdf['Ticker'] = t
    rlist.append(tdf.reset_index().set_index(['dt','Ticker']))

outamt = pd.concat(rlist, axis = 0).sort_index()
outamt = outamt.reindex(amt_daily.index)

def rating_flag(x):
    if 'A' in str(x):
        if str(x) in ['A-','A']:
            return False
        else:
            return True
    else:
        return False
outamt['rating_A'] = outamt['B_INFO_CREDITRATING'].apply(lambda x:rating_flag(x))
outamt['rating_A_stock'] = outamt['B_INFO_CREDITRATING_stock'].apply(lambda x:rating_flag(x))

amt_mask = amt_mask.reindex(amt_daily.index)
amt_last10 = amt_last10.reindex(amt_daily.index)
amt_mask = amt_mask.join(outamt, how = 'left').join(amt_last10,how = 'left')

# 增加换手率筛选
turnover_rate = (amt_mask['amount_daily'] / amt_mask['B_INFO_OUTSTANDINGBALANCE']).unstack()
turnover_rate = turnover_rate > 0.2
turnover_rate = turnover_rate.rolling(2, min_periods=2//2).sum()
turnover_rate = (turnover_rate == 2).shift(1).fillna(False)

turnover_rate = turnover_rate.stack().to_frame()
turnover_rate.columns = ['turnover_rate']

turnover_rate = turnover_rate.reindex(amt_daily.index)
amt_mask = amt_mask.join(turnover_rate, how = 'left')

# 债券余额
outmoney = amt_mask['B_INFO_OUTSTANDINGBALANCE'].unstack()
outmoney = (outmoney > 3e7).fillna(False)
outmoney = outmoney.stack().to_frame()
outmoney.columns = ['out_standing_balance']
outmoney = outmoney.reindex(amt_daily.index)
amt_mask = amt_mask.join(outmoney, how = 'left')

# ret = close.pct_change()
# ret = ret.replace([np.inf,-np.inf], np.nan)
# ret_std = ret.rolling(past_days * 242, min_periods = int(past_days * 242 / 2)).std()

# 获取可转债上市日期及转股期，最后交易日等
datedf = pd.read_csv('/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/CHINA_CONVERTIBLE_BOND_INFO.csv', index_col=0)[['stockcode','LISTEDDATE']]
#converdf = pd.read_hdf('/data/group/800080/warehouse/prod/DATABASE/WIND/CCBondConversion/CCBondConversion.h5')
#converdf = converdf.reset_index(level = 0, drop = True)
from xquant.factordata import FactorData
s = FactorData()
converdf = s.get_factor_value('WIND_CCBondConversion').rename(columns = {'S_INFO_WINDCODE':'Ticker'}).set_index('Ticker')

datedf = datedf.join(converdf)[['LISTEDDATE','CONV_STARTDATE','CONV_ENDDATE','TRADE_DT_LAST','stockcode']]

date_mask = amt_mask.reset_index(level = 0).join(datedf, how = 'left')#.drop(0, axis = 1)

if date_mask.loc['123049.SZ','LISTEDDATE'].isna().sum() > 0:
    date_mask.loc['123049.SZ','LISTEDDATE'] = 20200512
if date_mask.loc['110091.SH','LISTEDDATE'].isna().sum() > 0:
    date_mask.loc['110091.SH','LISTEDDATE'] = 20230106
if date_mask.loc['123049.SZ','TRADE_DT_LAST'].isna().sum() > 0:
    date_mask.loc['123049.SZ','TRADE_DT_LAST'] = 20260413

date_mask['TRADE_DT_LAST'] = date_mask['TRADE_DT_LAST'].fillna(21000101)

for y in ['LISTEDDATE', 'CONV_STARTDATE', 'CONV_ENDDATE', 'TRADE_DT_LAST']:
    date_mask[[y]] = date_mask[[y]].apply(lambda x:pd.to_datetime(str(int(x))), axis = 1)

date_mask['dt'] = pd.to_datetime(date_mask['dt'])

date_mask.head()

date_mask['res_days'] = date_mask.apply(lambda x:(x['TRADE_DT_LAST'] - x['dt']).days, axis = 1)
date_mask['res_days_conv'] = date_mask.apply(lambda x:(x['CONV_ENDDATE'] - x['dt']).days, axis = 1)
date_mask['list_days'] = date_mask.apply(lambda x:(x['dt'] - x['LISTEDDATE']).days, axis = 1)

date_mask.loc[date_mask.res_days > 30,'res_days_30'] = True
date_mask.loc[date_mask.res_days_conv > 20,'res_days_conv_20'] = True
date_mask.loc[date_mask.list_days > 20,'list_days_20'] = True
date_mask.loc[date_mask['dt'] >= date_mask['CONV_STARTDATE'],'is_conv'] = True
date_mask[['res_days_30','res_days_conv_20','list_days_20','is_conv']] = date_mask[['res_days_30','res_days_conv_20','list_days_20','is_conv']].fillna(False)

date_mask.head()

date_mask = date_mask.reset_index().set_index(['dt','Ticker']).sort_index()

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

@static_vars(cache=None)
def retrieve_st_stocks(date):
    date = IO.str_date_parser(date)
    if retrieve_st_stocks.cache is None:
        cache = IO.read_data(columns=['REMOVE_DT', 'ENTRY_DT'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareST/AShareST.h5').reset_index('dt', drop=True)
        cache['REMOVE_DT'] = pd.to_datetime(cache['REMOVE_DT'], format='%Y%m%d')
        cache['ENTRY_DT'] = pd.to_datetime(cache['ENTRY_DT'], format='%Y%m%d')
        cache['REMOVE_DT'].loc[cache['REMOVE_DT'].isnull()] = pd.Timestamp.max
        retrieve_st_stocks.cache = cache
    else:
        cache = retrieve_st_stocks.cache
    return cache[(cache['ENTRY_DT'] <= date) & (cache['REMOVE_DT'] > date)].index.unique().tolist()

stk = date_mask[['stockcode']]
datelist = stk.index.get_level_values(0).unique().tolist()

templist = []
def get_ST_by_date(date):
    stlist = retrieve_st_stocks(date)
    temp = pd.DataFrame(stlist,columns = ['stockcode'])
    temp['dt'] = date
    return temp
for date in tqdm(datelist):
    templist.append(get_ST_by_date(date))
stdf = pd.concat(templist, axis = 0).set_index(['dt','stockcode']).sort_index()
stdf['stk_not_ST'] = False

stk = stk.reset_index().set_index(['dt','stockcode'])
stkst = stk.join(stdf,how = 'left')
stkst['stk_not_ST'] = stkst['stk_not_ST'].fillna(True)
stkst = stkst.reset_index().set_index(['dt','Ticker'])[['stk_not_ST']]

date_mask = date_mask.join(stkst,how = 'left')

date_mask['overnight_v1'] = date_mask['amount_2000'] & date_mask['stk_not_ST'] & date_mask['rating_A'] & date_mask['rating_A_stock'] & date_mask['out_standing_balance'] & date_mask['res_days_conv_20'] & date_mask['res_days_30'] & date_mask['list_days_20']
date_mask = date_mask.loc[~date_mask.index.duplicated()]

save_path = '/data/user/015626/data/share/MD/CHINA_CONVERTIBLE_BOND/UNIVERSE/CHINA_CONVERTIBLE_BOND_UNIVERSE.h5'
if os.path.exists(save_path):
    IO.pd_hdf5_writer(date_mask, save_path, dataset='CHINA_CONVERTIBLE_BOND_UNIVERSE', override = True)
else:
    IO.pd_hdf5_writer(date_mask, save_path, dataset='CHINA_CONVERTIBLE_BOND_UNIVERSE')