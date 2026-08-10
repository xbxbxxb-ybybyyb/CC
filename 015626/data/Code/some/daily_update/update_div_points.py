import pandas as pd
import numpy as np
import datetime as dt
import math
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
from multifactor.utility.dt import *
from tqdm import tqdm


def minute_flag_check(date):
    path1 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_RDF.success'
    path2 = '/data/group/800080/warehouse/prod/LOCAL_DATA/FLAG/' + str(date) + '/' + str(date) + '_INDEX_WEIGHT.success'
    return os.path.exists(path1) and os.path.exists(path2)


h5_path = '/data/user/015626/data/share/IndexDividends/details/IndexDividends_Details.h5'
temp = pd.read_hdf('/data/user/015626/data/share/IndexDividends/details/IndexDividends_Details.h5').reset_index()
start_date = int(temp.iloc[-1]['dt'].date().strftime('%Y%m%d'))
_,flag_date,_ = check_update_date()
end_date = int(get_trading_day_offset(flag_date,1)[0].date().strftime('%Y%m%d'))
print(start_date, end_date)

flag_root = '/data/user/015626/data/share/LOCAL_DATA/FLAG/' + str(flag_date) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(flag_date) + '_' + 'div_points.start'
with open(flag_path_start,'w') as file:
    pass 

print('------wait minute flag')
while True:
    if minute_flag_check(flag_date):
        break
    time.sleep(60)
print('flag check finished!')


idxdata = IO.read_data([start_date, end_date], columns=['S_DQ_CLOSE'], alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AIndexEODPrices/AIndexEODPrices.h5')
idxdata.columns = ['close']

cdatelist = get_trading_date_range(start_date, end_date)
clist = [str(x)[:10].replace('-','') for x in cdatelist]

totalresult = pd.DataFrame()
for futurecode in ['IC','IF','IH','IM']:
    if futurecode == 'IF':
        tmp = '000300.SH'
        aim = 'HS300'
        weight_column = 'index_weight_hs300'
    elif futurecode == 'IC':
        tmp = '000905.SH'
        aim = 'ZZ500'
        weight_column = 'index_weight_zz500'
    elif futurecode == 'IH':
        tmp = '000016.SH'
        aim = 'SH50'
        weight_column = 'index_weight_sh50'
    elif futurecode == 'IM':
        tmp = '000852.SH'
        aim = 'ZZ1000'
        weight_column = 'index_weight_zz1000'
        
    result = pd.DataFrame()    
    for i in tqdm(range(1, len(clist))):
        tday = clist[i]
        lasttday = clist[i-1]
#        weightsdf = pd.read_csv('/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/stock_universe/%s/%s.csv' % (aim, lasttday))
#        weightsdf = weightsdf.rename(columns={aim:'weight'})
        weightsdf = IO.read_data([lasttday], columns = [weight_column], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/INDEXWEIGHT_CHINA_STOCK_DAILY_CSI.h5')
        weightsdf = weightsdf.rename(columns={weight_column:'weight'})
        weightsdf = weightsdf[weightsdf['weight'] > 0].reset_index()[['Ticker', 'weight']]
        tickers = list(weightsdf['Ticker'])
        idx_close = idxdata.loc[lasttday, tmp]['close'] #w.wsd(tmp, "close", lasttday, lasttday, "").Data[0][0]

        asdpath = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareDividend/AShareDividend.h5'
        a = IO.read_data([(int(lasttday[:4]) - 1) * 10000 + 1231], alt = asdpath)
        b = IO.read_data([(int(lasttday[:4])) * 10000 + 630], alt = asdpath)
        a = a.append(b)
        a = a[(a['CASH_DVD_PER_SH_PRE_TAX'] > 0) & (a['S_DIV_OBJECT'] == '普通股股东')]
        a['EX_DT'] = a.EX_DT.apply(lambda x: str(int(x)) if x == x else np.nan)
        res1 = a.reset_index()[['Ticker','CASH_DVD_PER_SH_PRE_TAX','EX_DT']]
        res1.columns = ['wind_code','dividendsper_share_pretax','exrights_exdividend_date']

        bonusdf = res1[res1.wind_code.isin(tickers)]
        bonusdf = bonusdf[bonusdf.exrights_exdividend_date == tday]
        bonusdf = bonusdf.rename(columns={'wind_code':'Ticker'})
        sto_close = IO.read_data([lasttday], columns='close', dfreq=DFreq.DAILY, dtype=DType.STOCK, dsource=DSource.WIND, ftype=FType.MD).reset_index()
        df = pd.merge(bonusdf,sto_close,how='left')
        df = pd.merge(df, weightsdf,how='left')
#        df['point'] = df['dividendsper_share_pretax'] / df['close'] * df['weight'] * idx_close / 100
        df['point'] = df['dividendsper_share_pretax'] / df['close'] * df['weight'] * idx_close
        thisdaypoint = df.point.sum()
        result.loc[tday, 'divpoint'] = thisdaypoint
        result.loc[tday, 'tickers'] = str(df.Ticker.tolist())
        result.loc[tday, 'point_every_ticker'] = str(df.point.tolist())
    result['Ticker'] = futurecode+'.CFE'
    totalresult = totalresult.append(result)
    
totalresult.index.name = 'dt'
totalresult.index = pd.to_datetime(totalresult.index)
totalresult = totalresult.reset_index().set_index(['dt','Ticker']).sort_index()

print(totalresult)

IO.pd_hdf5_writer(totalresult,h5_path, dataset='IndexDividends_Details', append=True)

flag_path_success = flag_root + str(flag_date) + '_' + 'div_points.success'
with open(flag_path_success,'w') as file:
    pass 