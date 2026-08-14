import pandas as pd
import os
import numpy
import numpy as np
all_factor = pd.read_pickle('all_factor_df.pkl')

# 和其他因子的相关性
df_corr = pd.read_pickle('/dfs/user/023859/share_file/for_qyh/飞笛舆情测试/all_factor_corr.pkl')
columns_label = ['IC_label_t2o30d1', 'IC_label_t4o30d1', 'IC_label_t6o30d1',]
columns_others = [x for x in df_corr.columns if x not in columns_label]
df_corr['max_corr'] = abs(df_corr[columns_others]).max(axis=1).to_frame(name = 'max_corr')
df_corr['ratio_nan'] = np.nan
for i in all_factor.columns:
    tmp = all_factor[i]
    ratio = len(tmp[tmp == 0]) / len(all_factor)
    df_corr.loc[i, 'ratio_nan'] = ratio
# IC
df_IC = pd.read_pickle('/dfs/user/023859/share_file/for_qyh/飞笛舆情测试/all_factor_neutralized_IC.pkl')
columns_label = ['IC_label_t2o30d1', 'IC_label_t4o30d1', 'IC_label_t6o30d1',]
columns_others = [x for x in df_IC.columns if x not in columns_label]
#
res = pd.concat([df_corr[['max_corr', 'ratio_nan']], df_IC[columns_label]], axis=1)


