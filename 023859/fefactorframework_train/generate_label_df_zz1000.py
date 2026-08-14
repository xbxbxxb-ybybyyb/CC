import pandas as pd
import numpy as np
import os
from h5data.IO import IO
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
mdp = MarketData()

start_date, end_date = 20170110,20241231

trading_days = s.tradingday(start_date, end_date)

basic_file_path = '/dfs/user/023859/share_file/for_skk/neptune/zz1000_profit_interval_20170110_20250630.h5'
md_path = '/dfs/user/023859/neptune/label_0931_0941_s1_1100_1110/'

basic_file = pd.read_hdf(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]
basic_file_pos = basic_file.copy()
basic_file_neg = basic_file.copy()

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(os.path.join(md_path,file)))

md = pd.concat(md)[['pre_close','open','close','amt','adjfactor','buy_0931_0941_twap','sell_0931_0941_twap',\
                    'buy_1100_1110_twap','sell_1100_1110_twap','buy_amt_pos_ratio','buy_amt_neg_ratio']].sort_index(level=['Ticker', 'dt'])

# 处理数据集错误
if '20230905' in trading_days:
    md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
    md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
    md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['buy_0931_0941_twap_adj'] = md['buy_0931_0941_twap']*md['adjfactor']
md['sell_1100_1110_twap_adj'] = md['sell_1100_1110_twap']*md['adjfactor']
md['sell_1100_1110_twap_adj'] = md['sell_1100_1110_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['sell_0931_0941_twap_adj'] = md['sell_0931_0941_twap']*md['adjfactor']
md['buy_1100_1110_twap_adj'] = md['buy_1100_1110_twap']*md['adjfactor']
md['buy_1100_1110_twap_adj'] = md['buy_1100_1110_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['label_ta2to10_neg'] = 1 - md['buy_1100_1110_twap_adj']/md['sell_0931_0941_twap_adj']
md['label_ta2to10_pos'] = md['sell_1100_1110_twap_adj']/md['buy_0931_0941_twap_adj'] - 1



basic_file_pos['pct'] = md['label_ta2to10_pos']
basic_file_pos['buy_amt'] = basic_file_pos['buy_amt']*md['buy_amt_pos_ratio']

basic_file_neg['pct'] = md['label_ta2to10_neg']
basic_file_neg['buy_amt'] = basic_file_neg['buy_amt']*md['buy_amt_neg_ratio']

# basic_file_neg = basic_file_neg.dropna()
# basic_file_neg = basic_file_neg.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]

IO.pd_hdf5_writer(basic_file_pos.dropna(), hdf5='/dfs/user/023859/share_file/for_xbc/neptune/profit/20250729_a/2017_2024/zz1000_profit_interval.h5', dataset='neptune')
IO.pd_hdf5_writer(basic_file_neg.dropna(), hdf5='/dfs/user/023859/share_file/for_xbc/neptune/profit/20250729_a/2017_2024/neg/zz1000_profit_interval.h5', dataset='neptune')


'''
basic_file_neg.to_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_filter_20170110_20191231.pkl')

factor_df = pd.read_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_filter_20170110_20191231.pkl')

factor_df_sw_high = pd.read_pickle('/data/group/800463/tangsq/neptune/20250609/20170110_20191231/factor_df_s1_sw_high_filter_short_term_20170110_20191231.pkl')
factor_df_sw_low = pd.read_pickle('/data/group/800463/tangsq/neptune/20250609/20170110_20191231/factor_df_s1_sw_low_filter_short_term_20170110_20191231.pkl')
factor_df_vol_high = pd.read_pickle('/data/group/800463/tangsq/neptune/20250609/20170110_20191231/factor_df_s1_vol_high_filter_short_term_20170110_20191231.pkl')
factor_df_vol_low = pd.read_pickle('/data/group/800463/tangsq/neptune/20250609/20170110_20191231/factor_df_s1_vol_low_filter_short_term_20170110_20191231.pkl')


factor_df_sw_high[['label_ta2to10_pos','label_ta2to10_neg']] = factor_df[['label_ta2to10_pos','label_ta2to10_neg']]
factor_df_sw_low[['label_ta2to10_pos','label_ta2to10_neg']] = factor_df[['label_ta2to10_pos','label_ta2to10_neg']]
factor_df_vol_high[['label_ta2to10_pos','label_ta2to10_neg']] = factor_df[['label_ta2to10_pos','label_ta2to10_neg']]
factor_df_vol_low[['label_ta2to10_pos','label_ta2to10_neg']] = factor_df[['label_ta2to10_pos','label_ta2to10_neg']]

factor_df_sw_high.to_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_sw_high_filter_20170110_20191231.pkl')
factor_df_sw_low.to_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_sw_low_filter_20170110_20191231.pkl')
factor_df_vol_high.to_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_vol_high_filter_20170110_20191231.pkl')
factor_df_vol_low.to_pickle('/data/group/800463/tangsq/neptune/20250905/factor_df_s1_vol_low_filter_20170110_20191231.pkl')
'''