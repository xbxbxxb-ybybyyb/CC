import IO
import pandas as pd
import numpy as np

factor_df = pd.read_hdf('/dfs/user/020412/团队分享/for_hotspot/factor_df_20160101_20231231.h5')
label_df = pd.read_hdf('/dfs/user/020412/团队分享/for_hotspot/md2_20250512_20150901_20231231.h5')

factor_IC_year = pd.DataFrame()
for year in [2016,2017,2018,2019]:
    factor_df_year = factor_df.loc[pd.Timestamp(f'{year}0101'): pd.Timestamp(f'{year}1231')]
    label_df_year = label_df.loc[pd.Timestamp(f'{year}0101'): pd.Timestamp(f'{year}1231')]
    corr_df = factor_df_year.corrwith(label_df_year['label_reward'],method='spearman').to_frame(name = year).T
    factor_IC_year = factor_IC_year.append(corr_df)
factor_IC_year_abs = factor_IC_year.abs()
# 每年的因子IC分布
print(factor_IC_year_abs.quantile([0.25,0.5,0.75,0.9], axis=1))

# 年度因子IC的diff的均值
columns_T = [x for x in factor_IC_year_abs.columns if 'md' not in x and 'zwh' not in x]
factor_IC_year_abs_T = factor_IC_year_abs[columns_T]
print(factor_IC_year_abs.diff().abs().mean().quantile([0.25,0.5,0.75,0.9]))

print((factor_IC_year_abs.diff().abs().mean() / factor_IC_year_abs.mean()).quantile([0.25,0.5,0.75,0.9]))




