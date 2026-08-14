import pandas as pd
import IO
from xquant.factordata import FactorData
s = FactorData()
start_date = 20151001
end_date = 20241231
df_sw = pd.read_excel('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/申万行业指数代码表.xlsx')

index_data = s.get_factor_value('WIND_ASWSIndexEOD',TRADE_DT = [f'>=20150930',f'<=20151231'])
for year in range(2016,2025):
    print(year)
    index_data_year = s.get_factor_value('WIND_ASWSIndexEOD',TRADE_DT = [f'>={year}0101',f'<={year}1231'])
    index_data = index_data.append(index_data_year)

index_data = index_data.rename(columns = {'S_INFO_WINDCODE':'Ticker',
                                          'TRADE_DT':'dt',
                                          'S_DQ_PRECLOSE':'pre_close',
                                          'S_DQ_OPEN':'open',
                                          'S_DQ_HIGH':'high',
                                          'S_DQ_LOW':'low',
                                          'S_DQ_CLOSE':'close',
                                          'S_DQ_VOLUME':'volume',
                                          'S_DQ_AMOUNT':'amt',
                                          'S_DQ_MV':'mv'
                                          })
index_data['dt'] = index_data['dt'].apply(pd.Timestamp)
index_data = index_data.set_index(['dt','Ticker']).sort_values(['dt','Ticker'])
index_data['mv'] = index_data['mv'] * 10000
index_data['float_shares'] = (index_data['mv'] / index_data['close']).unstack().shift(1).stack()
index_data = index_data.reset_index()
index_data_sw = index_data[index_data['Ticker'].isin(list(df_sw['code']))].set_index(['dt','Ticker'])[['amt','pre_close','open','high','low','close','volume','float_shares']]
# index_data_sw.to_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/basic_file_sw_20160101_20241231.pkl')

# 补充vwap，按成交额计算
index_data_sw = pd.read_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/basic_file_sw_20160101_20241231.pkl')
index_data_sw = index_data_sw.loc[pd.Timestamp('20171201'):]
res = pd.DataFrame()
list_tradingday = list(set(index_data_sw.index.get_level_values(0)))
list_tradingday.sort()

for tradingday in list_tradingday:
    print(tradingday)
    tick_df = pd.read_pickle(f'/dfs/user/015585/04_行业指数数据/申万2021/{tradingday.strftime("%Y%m%d")}.pkl')
    res_tradingday = tick_df.groupby('Ticker').apply(lambda x : (x['LastPx'] * (x['TotalValueTrade'].diff().fillna(0))).sum() / x['TotalValueTrade'].max())
    res_tradingday = pd.DataFrame(res_tradingday)
    res_tradingday['dt'] = tradingday
    res_tradingday.reset_index(inplace = True)
    res_tradingday.set_index(['dt','Ticker'], inplace = True)
    res_tradingday.columns = ['vwap']
    res = res.append(res_tradingday)
index_data_sw['vwap'] = res['vwap']
index_data_sw.to_pickle('/data/user/015585/01-因子挖掘/20250121-大模型-主题轮动策略/file/basic_file_sw_20160101_20241231.pkl')





