import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
mdp = MarketData()

start_date, end_date = 20160101,20250331
start_date_ = int(s.tradingday(start_date,-250)[0])
end_date_ = int(s.tradingday(end_date,250)[-1])

strategy_path = '/dfs/user/023859/neptune/20250428'
basic_file_path = '/dfs/user/023859/neptune/20250428/basic_file_zz1000_20160101_20250331.pkl'
md_path = '/dfs/user/023859/Neptune/label_1430_1440_next_0930_0940'

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(os.path.join(md_path,file)))

md = pd.concat(md)[['pre_close','open','close','amt','adjfactor','buy_1430_1440_twap','sell_0930_0940_twap']].sort_index()
# 处理数据集错误
md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['close_adj'] = md['close']*md['adjfactor']
md['open_adj'] = md['open']*md['adjfactor']
md['buy_1430_1440_twap_adj'] = md['buy_1430_1440_twap']*md['adjfactor']
md['sell_0930_0940_twap_adj'] = md['sell_0930_0940_twap']*md['adjfactor']

md['next_sell_0930_0940_twap_adj'] = md.groupby('Ticker')['sell_0930_0940_twap_adj'].apply(lambda x: x.shift(-1).bfill())
md['next_open_adj'] = md.groupby('Ticker')['open_adj'].apply(lambda x: x.shift(-1).bfill())
# md['next_3_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-3).bfill())
# md['next_5_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-5).bfill())

md['label_t2o10dc'] = md['next_sell_0930_0940_twap_adj']/md['buy_1430_1440_twap_adj'] - 1
md['label_buy_close'] = md['close_adj']/md['buy_1430_1440_twap_adj'] - 1
md['label_close_next_open'] = md['next_open_adj']/md['close_adj'] - 1
md['label_next_open_sell'] = md['next_sell_0930_0940_twap_adj']/md['next_open_adj'] - 1

# md['label_t4o30d1'] = md['next_3_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
# md['label_t6o30d1'] = md['next_5_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
labels_file = basic_file.join(md[['label_t2o10dc','label_buy_close','label_close_next_open','label_next_open_sell']])
labels_file[['label_t2o10dc','label_buy_close','label_close_next_open','label_next_open_sell']].to_pickle(os.path.join(strategy_path, f'label_df_detail_{start_date}_{end_date}.pkl'))