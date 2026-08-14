import IO
import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()
import decimal

def round_(x, n=0):
    x=x+1e-13
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

start_date, end_date = 20210701, 20240630
end_date_next = int(s.tradingday(end_date,2)[-1])
trading_days = s.tradingday(start_date, end_date_next)
md = IO.read_data([start_date, end_date_next],columns=['pre_close','vwap','adjfactor','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['ul_price'] = md['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md['dl_price'] = md['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md.loc[md['zcz'],'ul_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md.loc[md['zcz'],'dl_price'] = md.loc[md['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))
md = md[md['amt']>0]
md['vwap'] = md['vwap'].mask((md['vwap']==md['ul_price'])|(md['vwap']==md['dl_price']))
md['vwap_adj'] = md['vwap']*md['adjfactor']
md['next_vwap_adj'] = md['vwap_adj'].groupby('Ticker').apply(lambda x: x.shift(-1).bfill())

ZZ1000_sw_weight_and_price = pd.read_pickle('/data/user/023859/Hedging/ZZ1000_sw_weight_and_price_20210701_20240630.pkl')
ZZ1000_sw_weight_and_price['931_941_twap_adj'] = ZZ1000_sw_weight_and_price['931_941_twap'] * md['adjfactor']
ZZ1000_sw_weight_and_price['next_vwap_adj'] = md['next_vwap_adj']

for date in tqdm(trading_days):
    stockPool = list(ZZ1000_sw_weight_and_price.xs(pd.Timestamp(date), level=0).index)
    stockPool_st_out = s.stock_filter(stockPool, date, 'STPT')['stock'].tolist()
    mask = (ZZ1000_sw_weight_and_price.index.get_level_values(0) == pd.Timestamp(date)) & (ZZ1000_sw_weight_and_price.index.get_level_values(1).isin(stockPool_st_out))
    ZZ1000_sw_weight_and_price.loc[mask, 'STPT'] = False

ZZ1000_sw_weight_and_price.to_pickle('/dfs/user/023859/industry_hedging/ZZ1000_sw_weight_and_price_%s_%s.pkl'%(start_date,end_date))

'''
#分钟收盘价
min_close = IO.read_data([start_date,end_date_next],alt='/data/group/800463/data/minute_close.h5')
min_close['m931_adj'] = min_close['m931']*md['adj_factor']
min_close['931_941_twap'] = min_close[['m931','m932','m933','m934','m935','m936','m937','m938','m939','m940']].mean(axis=1)
min_close['931_941_twap_adj'] = min_close['931_941_twap']*md['adjfactor']
min_close['twap'] = min_close.mean(axis=1)
min_close['twap_adj'] = min_close['twap']*md['adjfactor']
min_close['next_twap_adj'] = min_close.groupby('Ticker')['twap_adj'].shift(-1)
min_close['next_0931_adj'] = min_close.groupby('Ticker')['m931_adj'].shift(-1)
#指数成分股
zz1000 = IO.read_data([start_date,end_date_next],columns=['index_1000'],alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
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
    ZZ1000_sw2 = s.hsi(list(df_ZZ1000['stock']), date, flag, 2).set_index('stock')
    ZZ1000_sw_weight_date[['sw_industry_code_1','sw_industry_name_1']] = ZZ1000_sw1[['industry_code','industry_name']]
    ZZ1000_sw_weight_date[['sw_industry_code_2','sw_industry_name_2']] = ZZ1000_sw2[['industry_code','industry_name']]
    ZZ1000_sw_weight_date['sw_industry_code'] = ZZ1000_sw_weight_date.apply(lambda row: row['sw_industry_code_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_code_1'],axis=1)
    ZZ1000_sw_weight_date['sw_industry_name'] = ZZ1000_sw_weight_date.apply(lambda row: row['sw_industry_name_2'] if row['sw_industry_name_1'] == '非银金融' else row['sw_industry_name_1'],axis=1)
    ZZ1000_sw_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.reset_index()
    ZZ1000_sw_weight_date['dt'] = pd.to_datetime(date)
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_sw_weight_date = ZZ1000_sw_weight_date.set_index(['dt','Ticker'])[['sw_industry_code','sw_industry_name','sw_industry_code_1','sw_industry_name_1','sw_industry_code_2','sw_industry_name_2','weight']]
    ZZ1000_sw_weight.append(ZZ1000_sw_weight_date)

ZZ1000_sw_weight = pd.concat(ZZ1000_sw_weight, axis=0)
ZZ1000_sw_weight_and_price = pd.concat([ZZ1000_sw_weight,ZZ1000_min_close], axis=1)

ZZ1000_sw_weight_and_price.to_pickle('/dfs/user/023859/industry_hedging/ZZ1000_sw_weight_and_price_%s_%s.pkl'%(start_date,end_date))
'''