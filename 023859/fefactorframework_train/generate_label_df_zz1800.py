import pandas as pd
import numpy as np
import os
import decimal
from h5data.IO import IO
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
mdp = MarketData()

def round_(x, n=13):
    x = x + 1e-15
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

strategy_version = 20250603
start_date, end_date = 20160101,20241231

trading_days = s.tradingday(start_date, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = '/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_20160101_20201231.h5' # zz1000 sc时点基础样本，比s1更大一些
md_path = '/dfs/user/023859/neptune/20250527/label_0931_0940_t_1000_1010'

basic_file = pd.read_hdf(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(os.path.join(md_path,file)))

md = pd.concat(md)[['pre_close','open','close','amt','adjfactor','buy_0931_0940_twap','sell_0931_0940_twap',\
                    'buy_1000_1010_twap','sell_1000_1010_twap','buy_amt_pos_ratio','buy_amt_neg_ratio']].sort_index(level=['Ticker', 'dt'])

# 处理数据集错误
if '20230905' in trading_days:
    md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
    md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['buy_0931_0940_twap_adj'] = md['buy_0931_0940_twap']*md['adjfactor']
md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap']*md['adjfactor']
md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['sell_0931_0940_twap_adj'] = md['sell_0931_0940_twap']*md['adjfactor']
md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap']*md['adjfactor']
md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['label_t2o9d1_pos'] = 1 - md['buy_1000_1010_twap_adj']/md['sell_0931_0940_twap_adj']
md['label_t2o9d1_neg'] = md['sell_1000_1010_twap_adj']/md['buy_0931_0940_twap_adj'] - 1

label_df = basic_file.join(md[['label_t2o9d1_neg', 'label_t2o9d1_pos']])

label_df = label_df.dropna()
label_df = label_df.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

# 存储数据，分享标签文件
sft_df = label_df[['label_t2o9d1_neg', 'label_t2o9d1_pos', 'list_len','Circu_Mkt']]
sft_df.loc[:pd.Timestamp('20201231')].to_pickle('/data/user/023859/factor_zooZZ/factor_lib/sft_update_931_20160101_20201231.pkl')
IO.pd_hdf5_writer(sft_df.loc[:pd.Timestamp('20201231')], hdf5='/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_20160101_20201231.h5', dataset='neptune')
IO.pd_hdf5_writer(sft_df.loc[:pd.Timestamp('20191231')], hdf5='/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5', dataset='neptune')
