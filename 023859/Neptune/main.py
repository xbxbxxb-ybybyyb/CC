import pandas as pd

factor_df = pd.read_pickle('/dfs/user/023859/neptune/20250428/factor_df_20160101_20191231.pkl')
label_df = pd.read_pickle('/dfs/user/023859/neptune/20250428/label_df_20160101_20250331.pkl')

factor_df = factor_df.join(label_df)
factor_df.to_pickle('/dfs/user/023859/neptune/20250428/factor_df_20160101_20191231')