#%%

import pandas as pd
import numpy as np
import IO
import decimal
#%%

'''
筛选股票，读取基础数据
1、剔除当日停牌，剔除europa（当日10分钟未达到涨停价-0.01）/saturn样本，剔除沪深300成分
2、最近10日总成交量（不是金额）/总流通股本得到换手率
3、取每天换手率在前1000名的样本
4、读取同花顺热度，取上述1000中，点击量占比前500的
'''

#%%

start_date = 20180101
end_date = 20201231
start_date_ = 20170930
end_date_ = 20210130
def round_(x, n=0):
    x = x + 1e-10
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_float = IO.read_data([start_date_,end_date_],
                  alt = '/data/group/800080/warehouse/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
# 停牌
f_data = f_data[f_data['amt'] > 0] # 剔除当日停牌
# 计算10日换手率
f_data['float_shares'] = df_float['FLOAT_A_SHR_TODAY']
f_data['turn_10'] = (f_data['volume'] / f_data['float_shares']).unstack().shift(1).rolling(10,1).mean().stack()
# 剔除saturn和europa
f_data['zcz']=(((f_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='30'))&(f_data.reset_index()['dt']>='2020-08-24'))
|(f_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='68'))).values
zt_price = np.floor(f_data['pre_close'] * 100 * 1.1 + 0.5) / 100
zt_price[f_data['zcz']] = np.floor(f_data['pre_close'] * 100 * 1.2 + 0.5) / 100
f_data['zt_price'] = zt_price
f_data['trigger_price'] = (f_data['zt_price']-0.01).apply(lambda x : round_(x,2))
f_data['is_zt'] = f_data['close'] == f_data['zt_price']
f_data['is_trigger'] = f_data['high'] >= f_data['trigger_price']
f_data['pre_is_zt'] = f_data['is_zt'].unstack().shift(1).stack()
#
filter1 = f_data['pre_is_zt'] == False
filter2 = f_data['is_trigger'] == False
# hs300成分
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()
df1 = s.get_factor_value('WIND_AIndexHS300Weight',
                         factors=['S_CON_WINDCODE', 'TRADE_DT'],
                         TRADE_DT=['>='+str(start_date_), '<='+str(end_date_)])
df1['dt'] = df1['TRADE_DT'].apply(lambda x:pd.Timestamp(str(x)))
df1 = df1[['S_CON_WINDCODE','dt']]
df1.columns = ['Ticker','dt']
df1['is_hs300'] = 1
df1 = df1.set_index(['dt','Ticker'])
f_data['is_hs300'] = df1['is_hs300']
f_data['is_hs300'] = f_data['is_hs300'].fillna(0)
filter3 = f_data['is_hs300'] == 0
# 同花顺热度
df = pd.read_csv('/data/user/015585/01-因子挖掘/20230616-同花顺行为数据测试/thsindex1.csv')
df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
df.columns = ['dt', 'Ticker', 'name', 'ori']
df = df.set_index(['dt', 'Ticker'])
f_data['ths_heat'] = df['ori'].unstack().shift(1).rolling(5,2).mean().stack()

# 排序，前1000与前500
# raise ValueError
f_data = f_data[filter1 & filter2 & filter3]

f_data['turn_10_rank'] = f_data['turn_10'].unstack().rank(axis=1,ascending=False).stack()
f_data = f_data[f_data['turn_10_rank'] <= 1000]
f_data['ths_heat_rank'] = f_data['ths_heat'].unstack().rank(axis=1,ascending=False).stack()
f_data = f_data[f_data['ths_heat_rank'] <= 500]

# 储存筛选后结果
f_data.to_pickle('/data/user/015585/01-因子挖掘/20230703-暑期实习生数据准备/code_202412/filter_df.pkl')