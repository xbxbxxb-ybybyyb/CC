import pandas as pd
import IO
#
df_ori = pd.read_pickle('test_data_2023.pkl')
df_ori.columns = ['dt','Ticker','ins','ind']
df_ori['dt'] = df_ori['dt'].apply(lambda x : pd.Timestamp(str(x)))
df_ori['ins'] = df_ori['ins'].astype(float)
df_ori['ind'] = df_ori['ind'].astype(float)
df_ori = df_ori.set_index(['dt','Ticker'])
df_ori = df_ori.sort_values(['dt','Ticker'])
# 因子

df_ori['factor1'] = (df_ori['ins'] - df_ori['ins'].unstack().shift(1).stack())/(df_ori['ins']+1)
df_ori['factor3'] = (df_ori['ind'] - df_ori['ind'].unstack().shift(1).stack())/(df_ori['ind']+1)
df_ori['factor5'] = df_ori['ins']
df_ori['factor6'] = df_ori['ind']
df_ori['factor2'] = df_ori['factor1'].unstack().rolling(20,1).mean().stack()
df_ori['factor4'] = df_ori['factor3'].unstack().rolling(20,1).mean().stack()
df_ori['factor7'] = df_ori['ins'].unstack().rolling(20,1).std().stack()
df_ori['factor8'] = df_ori['ind'].unstack().rolling(20,1).std().stack()
#
df_ori[['factor1','factor2','factor3','factor4','factor5','factor6']].to_pickle('factor_20231205.pkl')


## wind label
df_wind = IO.read_data([20210101, 20230930],
                      columns=['pct_chg'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
for col in df_ori.columns:
    df_wind[col] = df_ori[col].unstack().shift(2).stack()
res = df_wind.corr(method = 'spearman')
print(res['pct_chg'])