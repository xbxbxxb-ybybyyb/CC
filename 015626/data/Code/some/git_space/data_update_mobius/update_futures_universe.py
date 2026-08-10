from multifactor.IO import IO
import pandas as pd
import os
import datetime
from multifactor.data.utils import *
import multifactor.utility.dt as udt
import time
import re
from xquant.futuredata import FutureData
fd = FutureData()

univ_h5path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
daily_h5path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_SIF_DAILY_ALL_CONTRACT.h5'
# 更新日频率数据
# 获取各个合约的终止日期
def get_contract_end_dt():
    from xquant.factordata import FactorData
    s = FactorData()
    contract_end_dt = s.get_factor_value('WIND_CFuturesDescription', FS_INFO_SCCODE=['IF'])
    contract_end_dt = contract_end_dt[['S_INFO_CODE','S_INFO_DELISTDATE']].dropna().rename(columns = {'S_INFO_CODE':'contract','S_INFO_DELISTDATE':'end_dt'})
    contract_end_dt['contract'] = contract_end_dt.contract.apply(lambda x:int(x[2:6]))
    contract_end_dt['end_dt'] = pd.to_datetime(contract_end_dt['end_dt'])
    return contract_end_dt.set_index('contract').sort_index()

contract_end_dt = get_contract_end_dt()

def update_future_daily_data(end_date):
    
    end_date = str(end_date)
    contract_list = []
    for x in ['IC','IF','IH']:
        contract_list = contract_list + fd.get_instrument_all(x, end_date, end_date)
    assert len(contract_list) == 12
    daily_list = []
    for x in contract_list:
        daily_list.append(fd.get_future_data(x, "%s 000000000" % end_date, "%s 230000000" % end_date, 'K_DAY'))
    daily_df = pd.concat(daily_list, axis = 0)

    name_dict = { 'SecurityID':'Ticker',  'MDDate':'dt',
            'OpenPx':'open', 'ClosePx':'close', 'HighPx':'high', 'LowPx':'low',
           'TotalVolumeTrade':'volume', 'TotalValueTrade':'amount', 
           'OpenInterest':'position', 'SettlePrice':'settle'}
    daily_df = daily_df[list(name_dict.keys())].rename(columns = name_dict)

    daily_df['dt'] = pd.to_datetime(daily_df['dt'])
    daily_df['contract'] = daily_df.Ticker.apply(lambda x:int(x[2:6]))
    daily_df['Ticker'] = daily_df.Ticker.apply(lambda x:x+'.CFE')
    daily_df['prod_id'] = daily_df.Ticker.apply(lambda x:x[:2] + '.CFE')

    daily_df = daily_df.set_index('contract').join(contract_end_dt, how = 'left')
    daily_df['expiration_days'] = daily_df.apply(lambda x:len(udt.get_trading_date_range(x['dt'], x['end_dt'])) - 1, axis = 1)
    daily_df = daily_df.reset_index().drop(['end_dt','contract'], axis = 1).set_index(['dt','Ticker'])
    IO.pd_hdf5_writer(daily_df, daily_h5path, dataset = 'MD_SIF_TICK_TO_DAILY_ALL_CONTRACT', append = True)

df = IO.read_data([20200101,21000101], alt = daily_h5path)
sdate,edate,cdate_list = check_update_date(int(str(df.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
if len(cdate_list) > 1:
    for cdate in cdate_list[1:]:
        print('update daily data: ', cdate)
        update_future_daily_data(cdate)

# 以下为更新universe

df = IO.read_data([20200101,21000101], alt = univ_h5path)
sdate,edate,cdate_list = check_update_date(int(str(df.reset_index().iloc[-1]['dt'])[:10].replace('-','')),None)
start_date = cdate_list[1]
end_date = cdate_list[-1]
print(start_date, end_date)

flag_root = flag_rootpath + str(end_date) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(end_date) + '_' + 'stock_index_future_universe.start'
#with open(flag_path_start,'w') as file:
#    pass 

index00 = pd.DataFrame()
for TICKER in ['IC.CFE','IF.CFE','IH.CFE']:
    pd_data_daily = IO.read_data([start_date, end_date], alt = daily_h5path)
    IC_daily = pd_data_daily[pd_data_daily.prod_id == TICKER]
    df00 = IC_daily.groupby('dt').apply(lambda x: x.iloc[0:1, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','expiration_days']]
    df01 = IC_daily.groupby('dt').apply(lambda x: x.iloc[1:2, :]).reset_index(level=0, drop=True).reset_index(level=1)[['Ticker','expiration_days']]

    df00 = df00.rename(columns = {x:x+'_00' for x in df00.columns.tolist()})
    df01 = df01.rename(columns = {x:x+'_01' for x in df01.columns.tolist()})

    df = df00.join(df01)
    df.loc[df.expiration_days_00 <= 2,'Ticker_00'] = np.nan
    df['Ticker_00'].fillna(df['Ticker_01'], inplace = True)
    df = df[['Ticker_00']]
    df['Ticker'] = TICKER
    df = df.reset_index().rename(columns = {'Ticker_00':'contract_00'}).set_index(['dt','Ticker'])
    index00 = index00.append(df)

index00 = index00.sort_index()
index00 = index00.unstack()['contract_00']
index00['T.CFE'] = 'NaN'
index00 = index00.stack().to_frame()
index00.columns = ['contract_00']

indexdf = index00.reset_index()
indexdf['contract_main'] = indexdf.apply(lambda x:fd.get_change_date(x['Ticker'].split('.')[0], x['dt'].strftime('%Y%m%d'), 'ZL00')[0] + 'E', axis = 1)
indexdf['wind_main'] = 'Nan'
indexdf = indexdf.set_index(['dt','Ticker']).sort_index()
IO.pd_hdf5_writer(indexdf, univ_h5path, dataset='universe', append = True)

flag_path_success = flag_root + str(end_date) + '_' + 'stock_index_future_universe.success'
with open(flag_path_success,'w') as file:
    pass