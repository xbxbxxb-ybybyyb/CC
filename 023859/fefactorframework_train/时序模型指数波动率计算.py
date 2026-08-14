import pandas as pd
from xquant.thirdpartydata.factordata import FactorData
s = FactorData()

day_df = s.get_factor_value('WIND_AIndexEODPrices', factors=['S_INFO_WINDCODE','TRADE_DT','S_DQ_PRECLOSE','S_DQ_HIGH','S_DQ_LOW'], S_INFO_WINDCODE='000852.SH', TRADE_DT=['>=20160101','<=20211231'])
day_df = day_df.rename(columns={'TRADE_DT':'dt','S_INFO_WINDCODE':'Ticker'})
day_df['dt'] = pd.to_datetime(day_df['dt'])
day_df = day_df.set_index(['dt','Ticker'])
day_df['range_1'] = (day_df['S_DQ_HIGH'] - day_df['S_DQ_LOW'])/day_df['S_DQ_PRECLOSE']
day_df['range_2'] = (day_df['S_DQ_HIGH']/day_df['S_DQ_PRECLOSE'] - 1).abs()
day_df['range_3'] = (day_df['S_DQ_LOW']/day_df['S_DQ_PRECLOSE'] - 1).abs()
day_df['range'] = day_df[['range_1','range_2','range_3']].max(axis=1)
day_df['range'] = day_df['range'].rolling(7).mean()
day_df['factor_range'] = day_df['range'].shift(1)

day_df[['factor_range']].loc[pd.Timestamp('20170110'):].to_pickle('/dfs/user/023859/share_file/for_xbc/neptune/20250729/ZZ1000_index_vol.pkl')
