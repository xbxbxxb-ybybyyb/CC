import pandas as pd
import numpy as np
import IO
'''
统计低频策略表现
1、复牌当日是否一字板
2、label = 复牌后一日均价 / 复牌前一日开盘价
'''
df = pd.read_excel('停复牌统计.xlsx')
df['index'] = df.apply(lambda x : (x['复牌日期'],x['股票代码']), axis=1)
df = df.set_index(df['index'])

md_data = IO.read_data([20241001, 20250114], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['zcz']=(((md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='30'))&(md_data.reset_index()['dt']>='2020-08-24'))
|(md_data.reset_index()['Ticker'].apply(lambda x:x[0:2]=='68'))).values
zt_price = np.floor(md_data['pre_close'] * 100 * 1.1 + 0.5) / 100
zt_price[md_data['zcz']] = np.floor(md_data['pre_close'] * 100 * 1.2 + 0.5) / 100
md_data['zt_price'] = zt_price
md_data['is_1'] = md_data['zt_price'] == md_data['low']
md_data['label'] = (md_data['vwap'] * md_data['adjfactor']).unstack().shift(-1).stack() / md_data['zt_price'] / md_data['adjfactor'] - 1
md_data_filter = md_data.reindex(df['index'])

df['is_1'] = md_data_filter['is_1']
df['label'] = md_data_filter['label']