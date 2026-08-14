# coding: utf-8
# Author：fengchi863
# Date ：2025/2/21 14:07

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range
from tqdm import tqdm
fd = FactorData()

#%% 读取历史europe样本，2021-2024年
europa_df = pd.read_pickle('/data/user/018107/share_file/for_fc/20250114_europa_index_20160101_20250112.pkl')
europa_df['trade_date'] = europa_df.index.get_level_values(0).map(lambda x: int(x.strftime('%Y%m%d')))
europa_df['stock_code'] = europa_df.index.get_level_values(1).tolist()
date_list = get_date_range(20210101, 20241231)
date_str_list = list(map(lambda x: str(x), date_list))
stock_list = list(set(europa_df['stock_code'].tolist()))
europa_df = europa_df.query(f'trade_date in {date_list}')
europa_df = europa_df.reset_index()

daily_data = fd.get_factor_value('Basic_factor', factor_names=['pre_close_badj', 'close_badj', 'open_badj', 'high_badj', 'stpt', 'mdc_maxpx', 'adjfactor', 'maxupordown'], mddate=date_str_list, stock=stock_list)
# 统计被ST的可能
st_df = daily_data['stpt'].unstack()
st_df = st_df.fillna(0).applymap(int) - st_df.fillna(0).applymap(int).shift(1)

st_df_5day = st_df.rolling(5).sum()
st_df_5day = st_df_5day.shift(-5)
# europa_df['stIn5days'] = europa_df[['trade_date', 'Ticker']].apply(lambda x: st_df_5day.loc[x['trade_date'], x['Ticker']], axis=1)
europa_df['stIn5days'] = np.nan
for idx in tqdm(range(len(europa_df))):
    row = europa_df.iloc[idx]
    trade_date = row['trade_date']
    Ticker = row['stock_code']
    europa_df.loc[idx, 'stIn5days'] = st_df_5day.loc[str(trade_date), Ticker]
check = europa_df.sort_values('stIn5days')
print(1)