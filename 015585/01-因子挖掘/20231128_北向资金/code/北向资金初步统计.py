import pandas as pd
import numpy as np


df = pd.read_pickle('/data/user/015585/01-因子挖掘/20231128_北向资金/file/north_funds.pkl')
df_count = df.groupby('dt').count()



from xquant.thirdpartydata.factordata import FactorData
# SHSCChannelholdings 陆港通通道持股数量统计(中央结算系统)
s = FactorData()
s.get_factor_value('WIND_SHSCChannelholdings',
                          factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_INFO_EXCHMARKETNAME', 'S_QUANTITY'],
                          TRADE_DT=[f'>{20250601}', f'<={20250701}'])
