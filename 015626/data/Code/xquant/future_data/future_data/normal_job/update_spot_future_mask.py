from multifactor.IO import IO
import pandas as pd
import os
import datetime
import numpy as np
from tqdm import tqdm
from multiprocessing import Pool
import multifactor.utility.dt as udt

import warnings
warnings.filterwarnings('ignore')

def get_dt(a, b):
    year = a//10000
    month = a%10000//100
    day = a%100
    
    hour = b//100
    minute = b%100
    return datetime.datetime(year,month,day,hour,minute,0)
savenamedict = {'IC.CFE':'zz500','IF.CFE':'hs300','IH.CFE':'sh50'}

# update spot mask
fdf = IO.read_data([20161201,20200101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
spot_dict = {}
for x in ['IC.CFE','IF.CFE','IH.CFE']:
    d = fdf.xs(x, level = 1)
    if x == 'IF.CFE':
        d = d.add_suffix('_if')
    if x == 'IH.CFE':
        d = d.add_suffix('_ih')
    for c in d.columns:
        spot_dict[c] = d[[c]]
save_pickle(spot_dict, '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/SPOT_DATA_insample.pkl')

#update future mask
futures_data = IO.read_data([20161201, 20200101],columns = ['open', 'close', 'high', 'low', 'amount', 'volume', 'vwap', 'twap','position','share'], alt=os.path.join('/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_ALL_CONTRACT.h5'))
futures_data = futures_data.reset_index()
futures_data['contract'] = futures_data.Ticker.apply(lambda x: x[2:])
futures_data['Ticker'] = futures_data.Ticker.apply(lambda x: x[:2] + x[-4:])
futures_data = futures_data.set_index(['dt', 'contract', 'Ticker'])

df = futures_data.unstack(level = 1)

u = IO.read_data([20161201, 20200101], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
u = u.xs('IC.CFE', level = 1)[['contract_00']]
u['contract'] = u.contract_00.apply(lambda x:x[2:])
u = u.reset_index().rename(columns = {'dt':'date'})[['date','contract']].set_index('date')

t_days_list = udt.get_trading_date_range(str(u.index[0].date()).replace('-',''),str(u.index[-1].date()).replace('-',''))
t_days_list = [str(i)[:10] for i in t_days_list]
t_mins_list = pd.date_range('09:30:00','11:29:00', freq='min').to_list() + pd.date_range('13:00:00','14:57:00', freq='min').to_list()
t_mins_list = [str(i)[-8:] for i in t_mins_list]
index_list = []
for d in t_days_list:
    for m in t_mins_list:
        index_list.append(d + ' ' + m)
index_df = pd.DataFrame({'dt':index_list})
index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['date'] = index_df.dt.apply(lambda x:x.date())
index_df = index_df.set_index('date')

udf = index_df.join(u).reset_index().set_index(['dt','contract']).sort_index()
udf['date'] = 100
udf = udf.unstack().droplevel(0, axis = 1)

mask = udf > 0

maskcolumns = mask.columns.tolist()

future_dict = {}
for x in ['IC.CFE','IF.CFE','IH.CFE']:
    d = df.xs(x, level = 1)
    if x == 'IC.CFE':
        su = ''
    if x == 'IF.CFE':
        su = '_if'
    if x == 'IH.CFE':
        su = '_ih'
    for c in d.columns.get_level_values(0).unique():
        future_dict[c + su] = d[c].sort_index()[maskcolumns]
future_dict['recent_month_mask'] = mask

''' shengcheng mask
mihclist = main_ih_mask.columns.tolist()
allclist = future_dict['open'].columns.tolist()
reslist = list(set(allclist) - set(mihclist))
for c in reslist:
    main_ih_mask[c] = False
main_ih_mask = main_ih_mask.sort_index(axis = 1)
'''