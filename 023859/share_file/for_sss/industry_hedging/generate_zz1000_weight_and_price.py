import IO
import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20210701, 20220630
trading_days = s.tradingday(start_date, end_date)
#分钟收盘价
min_close = IO.read_data([start_date,end_date],alt='/data/group/800463/data/minute_close.h5')
#指数成分股
zz1000 = IO.read_data([start_date,end_date],columns=['index_1000'],alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
min_close['index_1000'] = zz1000['index_1000']
ZZ1000_min_close = min_close[min_close['index_1000']]

ZZ1000_sw_weight = []
for date in tqdm(trading_days):
    df_ZZ1000 = s.hset('INDEX',date,'ZZ1000',weightType=1) # 选择预估权重，避免回测用到未来数据
    if date < '20211213':
        flag = 'SW'
    else:
        flag = 'SW2021'
    ZZ1000_sw_weight_date = pd.DataFrame(index = df_ZZ1000['stock'], columns = ['sw_industry_code_1','sw_industry_name_1'])
    ZZ1000_sw_weight_date.index.names = ['stock']
    ZZ1000_sw1 = s.hsi(list(df_ZZ1000['stock']), date, flag, 1).set_index('stock')
    ZZ1000_sw_weight_date[['sw_industry_code_1','sw_industry_name_1']] = ZZ1000_sw1[['industry_code','industry_name']]
    ZZ1000_sw_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.reset_index()
    ZZ1000_sw_weight_date['dt'] = pd.to_datetime(date)
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.set_index(['dt','Ticker'])[['sw_industry_code_1','sw_industry_name_1','weight']]
    ZZ1000_sw_weight.append(ZZ1000_sw_weight_date)

ZZ1000_sw_weight = pd.concat(ZZ1000_sw_weight, axis=0)
ZZ1000_sw_weight_and_price = pd.concat([ZZ1000_sw_weight,ZZ1000_min_close], axis=1)

ZZ1000_sw_weight_and_price.to_pickle('/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_%s_%s.pkl'%(start_date,end_date))