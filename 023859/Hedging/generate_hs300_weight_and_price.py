import IO
import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20210701, 20240630
end_date_next = int(s.tradingday(end_date,2)[-1])
trading_days = s.tradingday(start_date, end_date_next)
#分钟收盘价
min_close = IO.read_data([start_date,end_date_next],alt='/data/group/800463/data/minute_close.h5')
min_close['931_941_twap'] = min_close[['m931','m932','m933','m934','m935','m936','m937','m938','m939','m940']].mean(axis=1)
min_close['twap'] = min_close.mean(axis=1)
min_close['next_twap'] = min_close.groupby('Ticker')['twap'].shift(-1)
min_close['next_0931'] = min_close.groupby('Ticker')['m931'].shift(-1)
#指数成分股
hs300 = IO.read_data([start_date,end_date_next],columns=['index_300'],alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
min_close['index_300'] = hs300['index_300']
hs300_min_close = min_close[min_close['index_300']]

hs300_sw_weight = []
for date in tqdm(trading_days):
    df_hs300 = s.hset('INDEX',date,'HS300',weightType=1) # 选择预估权重，避免回测用到未来数据
    if date < '20211213':
        flag = 'SW'
    else:
        flag = 'SW2021'
    hs300_sw_weight_date = pd.DataFrame(index = df_hs300['stock'], columns = ['sw_industry_code_1','sw_industry_name_1'])
    hs300_sw_weight_date.index.names = ['stock']
    hs300_sw1 = s.hsi(list(df_hs300['stock']), date, flag, 1).set_index('stock')
    hs300_sw2 = s.hsi(list(df_hs300['stock']), date, flag, 2).set_index('stock')
    hs300_sw_weight_date[['sw_industry_code_1','sw_industry_name_1']] = hs300_sw1[['industry_code','industry_name']]
    hs300_sw_weight_date[['sw_industry_code_2','sw_industry_name_2']] = hs300_sw2[['industry_code','industry_name']]
    hs300_sw_weight_date['sw_industry_code'] = hs300_sw_weight_date.apply(lambda row: row['sw_industry_code_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_code_1'],axis=1)
    hs300_sw_weight_date['sw_industry_name'] = hs300_sw_weight_date.apply(lambda row: row['sw_industry_name_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_name_1'],axis=1)
    hs300_sw_weight_date['weight'] = df_hs300.set_index('stock')['weight']/100
    hs300_sw_weight_date = hs300_sw_weight_date.reset_index()
    hs300_sw_weight_date['dt'] = pd.to_datetime(date)
    hs300_sw_weight_date = hs300_sw_weight_date.rename(columns={'stock':'Ticker'})
    hs300_sw_weight_date = hs300_sw_weight_date.set_index(['dt','Ticker'])[['sw_industry_code','sw_industry_name','sw_industry_code_1','sw_industry_name_1','sw_industry_code_2','sw_industry_name_2','weight']]
    hs300_sw_weight.append(hs300_sw_weight_date)

hs300_sw_weight = pd.concat(hs300_sw_weight, axis=0)
hs300_sw_weight_and_price = pd.concat([hs300_sw_weight, hs300_min_close], axis=1)

hs300_sw_weight_and_price.to_pickle('/data/user/023859/Hedging/hs300_sw_weight_and_price_%s_%s.pkl'%(start_date,end_date))