import pandas as pd

factor_df = pd.read_pickle('/data/group/800463/tangsq/neptune/20250609/20170110_20201231/factor_df_s1_filter_short_term_20170110_20201231.pkl')
profit_pos = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/zz1000_profit_interval.h5')
profit_neg = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/neg/zz1000_profit_interval.h5')

factor_df['label_ta2to10_pos'] = profit_pos['pct']
factor_df['label_ta2to10_neg'] = profit_neg['pct']

factor_df = factor_df[(~factor_df['label_ta2to10_pos'].isna())&(~factor_df['label_ta2to10_neg'].isna())]

factor_df.to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250609_a/factor_df_s1_filter_20170110_20201231.pkl')
