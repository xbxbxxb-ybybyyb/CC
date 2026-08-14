import pandas as pd

label_df_pos = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/zz1000_profit_interval.h5')
label_df_neg = pd.read_hdf('/data/group/800463/tangsq/neptune/profit/20250609_a/2017_2024/neg/zz1000_profit_interval.h5')

factor_path_dict = {
    'factor_path_1':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_931_20170110_20211231.pkl',
    'factor_path_2':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_1301_20170110_20211231.pkl',
    'factor_path_3':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_1445_20170110_20211231.pkl',
    'factor_path_4':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_ammax_20170110_20211231.pkl',
    'factor_path_5':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_max_20170110_20211231.pkl',
    'factor_path_6':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_min_20170110_20211231.pkl',
    'factor_path_7':'/dfs/user/023859/share_file/for_xbc/neptune/20250729/factor_df_pmmax_20170110_20211231.pkl'
}

factor_path_dict_new = {
    'factor_path_1':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_931_20170110_20211231.pkl',
    'factor_path_2':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_1301_20170110_20211231.pkl',
    'factor_path_3':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_1445_20170110_20211231.pkl',
    'factor_path_4':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_ammax_20170110_20211231.pkl',
    'factor_path_5':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_max_20170110_20211231.pkl',
    'factor_path_6':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_min_20170110_20211231.pkl',
    'factor_path_7':'/dfs/user/023859/share_file/for_xbc/neptune/20250729_a/factor_df_pmmax_20170110_20211231.pkl'
}

for path in factor_path_dict:
    factor_df = pd.read_pickle(factor_path_dict[path])
    factor_df['label_ta2to10_pos'] = label_df_pos['pct']
    factor_df['label_ta2to10_neg'] = label_df_neg['pct']
    factor_df = factor_df[(~factor_df['label_ta2to10_pos'].isna())&(~factor_df['label_ta2to10_neg'].isna())]
    factor_df.to_pickle(factor_path_dict_new[path])
